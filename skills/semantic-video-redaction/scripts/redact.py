"""Local, portable video localization, guided tracking, redaction and review."""
import argparse
from datetime import datetime, timezone
from fractions import Fraction
import hashlib
import importlib.metadata
import json
import math
from pathlib import Path
import re
import shutil
import subprocess
import sys

import cv2
import numpy as np

VERSION='1.0.0'
cv2.setNumThreads(4)


def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda:stream.read(1024*1024),b''): h.update(block)
    return h.hexdigest()


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def save(path,value):
    path=Path(path); path.parent.mkdir(parents=True,exist_ok=True)
    tmp=path.with_name(path.name+'.tmp')
    tmp.write_text(json.dumps(value,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8')
    tmp.replace(path)


def status(job,stage,state,**details):
    save(job/'status.json',{'stage':stage,'state':state,'at':datetime.now(timezone.utc).isoformat(),**details})


def probe(path):
    return json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(path)],encoding='utf-8'))


def video_info(path):
    info=probe(path)
    return info,next(s for s in info['streams'] if s['codec_type']=='video')


def image_write(path,image):
    ok,data=cv2.imencode('.jpg',image,[cv2.IMWRITE_JPEG_QUALITY,93])
    if not ok: raise RuntimeError(f'Cannot encode {path}')
    data.tofile(str(path))


def frame_at(cap,index):
    if round(cap.get(cv2.CAP_PROP_POS_FRAMES))!=index:
        cap.set(cv2.CAP_PROP_POS_FRAMES,index)
    ok,frame=cap.read()
    if not ok: raise RuntimeError(f'Cannot decode frame {index}')
    return frame


def job_data(job):
    manifest=read(job/'job.json')
    if sha(job/'clip.mkv')!=manifest['clip_sha256']:
        raise RuntimeError('Clip changed: prepare a new job.')
    return manifest


def current_tracks(job):
    m=job_data(job); tracks=read(job/'tracks.json')
    if tracks['clip_sha256']!=m['clip_sha256'] or tracks['targets_sha256']!=sha(job/'targets.json'):
        raise RuntimeError('Tracking is stale; rerun track and review.')
    return m,tracks


def prepare(args):
    job=args.job; source=args.source.expanduser().resolve()
    if not source.is_file(): raise ValueError('Source video does not exist.')
    if (job/'job.json').exists() or any(job.iterdir()): raise ValueError('Use a new empty job directory.')
    info,stream=video_info(source)
    duration=float(info['format']['duration'])
    if not 0<=args.start<args.end<=duration+.001: raise ValueError('Invalid source time interval.')
    fps=Fraction(args.fps or stream['r_frame_rate'])
    if not 0<float(fps)<=240: raise ValueError('Specify a valid nominal FPS with --fps.')
    status(job,'prepare','running',progress='decode')
    subprocess.run(['ffmpeg','-hide_banner','-v','error','-n','-ss',str(args.start),'-i',str(source),'-t',str(args.end-args.start),'-vf',f'fps={fps}','-c:v','ffv1','-an',str(job/'clip.mkv')],check=True)
    cap=cv2.VideoCapture(str(job/'clip.mkv'))
    width=int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)); height=int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    import nudenet
    from nudenet import NudeDetector
    detector=NudeDetector()
    model=Path(nudenet.__file__).parent/'320n.onnx'
    rows=[]
    while True:
        ok,frame=cap.read()
        if not ok:break
        i=len(rows)
        rows.append({'frame':i,'seconds':i/float(fps),'detections':detector.detect(frame)})
        if i%30==0:
            print(f'detect {i} frames',flush=True)
            status(job,'prepare','running',decoded_frames=i+1,progress='semantic_detection')
    cap.release()
    if not rows: raise RuntimeError('No decoded frames.')
    save(job/'detections.json',rows)
    manifest={'version':VERSION,'source':str(source),'source_sha256':sha(source),'start':args.start,'end':args.end,'fps':str(fps),'frames':len(rows),'width':width,'height':height,'has_audio':any(s['codec_type']=='audio' for s in info['streams']),'color':{k:stream[k] for k in ('color_space','color_transfer','color_primaries') if stream.get(k) not in (None,'unknown','reserved')},'clip_sha256':sha(job/'clip.mkv'),'detections_sha256':sha(job/'detections.json'),'model':{'name':'NudeNet','version':importlib.metadata.version('nudenet'),'file':model.name,'sha256':sha(model),'providers':detector.onnx_session.get_providers()}}
    save(job/'job.json',manifest)
    status(job,'prepare','succeeded',frames=len(rows),semantic_detections=sum(len(r['detections']) for r in rows))
    print(json.dumps({'frames':len(rows),'clip_sha256':manifest['clip_sha256'],'width':width,'height':height,'fps':str(fps)}))


def validate_targets(config,m):
    if config.get('clip_sha256')!=m['clip_sha256']:raise ValueError('targets.json must bind the current clip_sha256.')
    targets=config.get('targets',[])
    if not targets:raise ValueError('No targets: inspect the video before declaring no result.')
    ids=set()
    for target in targets:
        tid=target['id']
        if not re.fullmatch(r'[A-Za-z0-9_-]+',tid) or tid in ids:raise ValueError('Target IDs must be unique safe filenames.')
        ids.add(tid)
        start,end=target['range']
        if not (isinstance(start,int) and isinstance(end,int) and 0<=start<=end<m['frames']):raise ValueError(f'Invalid range: {tid}')
        if target['method'] not in ('flow','template'):raise ValueError('method must be flow or template.')
        if target.get('shape','ellipse') not in ('ellipse','rectangle'):raise ValueError('shape must be ellipse or rectangle.')
        guides=target['keyframes']
        if not guides or guides[0]['frame']!=start:raise ValueError(f'First keyframe must match range start: {tid}')
        if target['method']=='flow' and guides[-1]['frame']!=end:raise ValueError(f'Flow needs a final keyframe: {tid}')
        if [g['frame'] for g in guides]!=sorted({g['frame'] for g in guides}):raise ValueError('Keyframes must be unique and sorted.')
        for g in guides:
            x,y=g['center']; ax,ay=g.get('axes',target['axes'])
            if not (start<=g['frame']<=end and 0<=x<m['width'] and 0<=y<m['height'] and ax>0 and ay>0 and all(math.isfinite(float(v)) for v in (x,y,ax,ay))):raise ValueError(f'Invalid target coordinates: {tid}')


def track_flow(cap,target,m):
    start,end=target['range']; output={}
    if start==end:
        g=target['keyframes'][0]
        return {start:{'center':g['center'],'axes':g.get('axes',target['axes']),'issues':[]}}
    for ga,gb in zip(target['keyframes'][:-1],target['keyframes'][1:]):
        a,b=ga['frame'],gb['frame']
        if (b-a)/float(Fraction(m['fps']))>target.get('max_gap_seconds',1.0):
            raise ValueError(f'Add keyframes for {target["id"]}: gap {a}..{b}; or justify max_gap_seconds in config.')
        ca=np.array(ga['center'],float); cb=np.array(gb['center'],float)
        aa=np.array(ga.get('axes',target['axes']),float); ab=np.array(gb.get('axes',target['axes']),float)
        pad=np.maximum(aa,ab)*2+20
        lo=np.maximum(np.floor(np.minimum(ca,cb)-pad).astype(int),0)
        hi=np.minimum(np.ceil(np.maximum(ca,cb)+pad).astype(int),[m['width'],m['height']])
        x0,y0=lo; x1,y1=hi
        images=[]
        for i in range(a,b+1):
            f=frame_at(cap,i)
            images.append(cv2.cvtColor(f[y0:y1,x0:x1],cv2.COLOR_BGR2GRAY))
        yy,xx=np.mgrid[:y1-y0,:x1-x0]
        def advance(center,src,dst,axes):
            flow=cv2.calcOpticalFlowFarneback(src,dst,None,.5,4,21,4,7,1.5,0)
            local=center-lo
            area=((xx-local[0])/max(axes[0]*.7,4))**2+((yy-local[1])/max(axes[1]*.75,4))**2<=1
            if not np.any(area):raise RuntimeError('Flow search area left the frame.')
            return center+np.median(flow[area],axis=0)
        forward=[ca]; reverse=[cb]
        for j in range(b-a):forward.append(advance(forward[-1],images[j],images[j+1],aa))
        for j in range(b-a,0,-1):reverse.append(advance(reverse[-1],images[j],images[j-1],ab))
        reverse=reverse[::-1]
        for i in range(a,b+1):
            u=(i-a)/(b-a); j=i-a; expected=(1-u)*ca+u*cb
            center=(1-u)*forward[j]+u*reverse[j]
            limit=target.get('max_drift_px',float(max(aa.max(),ab.max())*.15))
            delta=center-expected; dist=float(np.linalg.norm(delta)); issues=[]
            if dist>limit:
                center=expected+delta*limit/dist; issues.append('flow_drift_limited')
            disagreement=float(np.linalg.norm(forward[j]-reverse[j]))
            if disagreement>max(aa.max(),ab.max())*.5:issues.append('flow_bidirectional_disagreement')
            output[i]={'center':center.tolist(),'axes':((1-u)*aa+u*ab).tolist(),'issues':issues,'flow_disagreement_px':disagreement}
    return output


def track_template(cap,target,m):
    output={}; guides={g['frame']:g for g in target['keyframes']}
    previous=None; template=None
    for i in range(target['range'][0],target['range'][1]+1):
        image=frame_at(cap,i); issues=[]
        if i in guides:
            g=guides[i]; previous=np.array(g['center'],float)
            axes=np.array(g.get('axes',target['axes']),float)
            half=np.array(target.get('template_half_size',(axes+3).tolist()),int)
            x,y=np.rint(previous).astype(int); hx,hy=half
            if x-hx<0 or y-hy<0 or x+hx>m['width'] or y+hy>m['height']:raise ValueError('Template keyframe patch crosses image boundary; use flow or a smaller template_half_size.')
            template=image[y-hy:y+hy,x-hx:x+hx].copy(); confidence=1.0
        else:
            margin=int(target.get('search_margin_px',max(24,max(half)*.6)))
            lo=np.maximum(np.floor(previous-half-margin).astype(int),0)
            hi=np.minimum(np.ceil(previous+half+margin).astype(int),[m['width'],m['height']])
            corr=cv2.matchTemplate(image[lo[1]:hi[1],lo[0]:hi[0]],template,cv2.TM_CCOEFF_NORMED)
            _,confidence,_,location=cv2.minMaxLoc(corr)
            if confidence<target.get('min_template_confidence',.65):
                issues.append('template_low_confidence_held')
            else:previous=lo+np.array(location)+half
        output[i]={'center':previous.tolist(),'axes':axes.tolist(),'issues':issues,'template_confidence':float(confidence)}
    return output


def track(args):
    job=args.job; m=job_data(job); config=read(args.targets)
    validate_targets(config,m)
    if sha(job/'detections.json')!=m['detections_sha256']:raise RuntimeError('Semantic detections changed.')
    semantic=read(job/'detections.json')
    cap=cv2.VideoCapture(str(job/'clip.mkv')); frames=[{'frame':i,'targets':[]} for i in range(m['frames'])]
    for t in config['targets']:
        print(f'track {t["id"]}',flush=True)
        status(job,'track','running',target=t['id'])
        result=(track_flow if t['method']=='flow' else track_template)(cap,t,m)
        for i,record in result.items():
            x,y=record['center']
            if not 0<=x<m['width'] or not 0<=y<m['height']:raise RuntimeError(f'Target {t["id"]} left frame {i}; split its visible range.')
            label=t.get('semantic_class')
            matched=any(d['class']==label and d['box'][0]-20<=x<=d['box'][0]+d['box'][2]+20 and d['box'][1]-35<=y<=d['box'][1]+d['box'][3]+35 for d in semantic[i]['detections']) if label else None
            if matched is False:record['issues'].append('semantic_miss_requires_visual_check')
            frames[i]['targets'].append({'id':t['id'],'shape':t.get('shape','ellipse'),'padding_px':t.get('padding_px',3),'semantic_match':matched,**record})
    cap.release()
    if Path(args.targets).resolve()!=(job/'targets.json').resolve():save(job/'targets.json',config)
    output={'version':VERSION,'clip_sha256':m['clip_sha256'],'targets_sha256':sha(job/'targets.json'),'frames':frames}
    save(job/'tracks.json',output)
    issue_count=sum(bool(t['issues']) for f in frames for t in f['targets'])
    status(job,'track','succeeded',frames=m['frames'],target_frames_with_issues=issue_count,next='visual_review_required')
    print(json.dumps({'frames':m['frames'],'target_frames_with_issues':issue_count}))


def masks(m,tracks,i):
    mask=np.zeros((m['height'],m['width']),np.uint8)
    for target in tracks['frames'][i]['targets']:
        near=[t for f in tracks['frames'][max(0,i-2):i+3] for t in f['targets'] if t['id']==target['id']]
        center=np.median([t['center'] for t in near],axis=0)
        axes=np.max([t['axes'] for t in near],axis=0)+target['padding_px']
        for c,a in ((center,axes),(target['center'],np.array(target['axes'])+target['padding_px'])):
            c=tuple(np.rint(c).astype(int)); a=tuple(np.ceil(a).astype(int))
            if target['shape']=='ellipse':cv2.ellipse(mask,c,a,0,0,360,255,-1)
            else:cv2.rectangle(mask,(c[0]-a[0],c[1]-a[1]),(c[0]+a[0],c[1]+a[1]),255,-1)
    return mask


def binding(job,stage):
    m=job_data(job)
    result={'clip':m['clip_sha256']}
    if stage in ('tracks','export'):
        current_tracks(job); result['tracks']=sha(job/'tracks.json')
    if stage=='export':
        render=read(job/'render.json')
        if render['tracks_sha256']!=result['tracks'] or sha(render['output'])!=render['output_sha256']:raise RuntimeError('Export is stale or changed.')
        result['export']=render['output_sha256']
    return result


def review(args):
    job=args.job; m=job_data(job); stage=args.stage; bound=binding(job,stage)
    tracks=read(job/'tracks.json') if stage!='source' else None
    source=Path(read(job/'render.json')['output']) if stage=='export' else job/'clip.mkv'
    cap=cv2.VideoCapture(str(source)); rows=[]
    wanted=set(args.targets.split(',')) if args.targets else None
    detection=read(job/'detections.json') if stage=='source' else None
    for i in range(args.first,min(args.last if args.last is not None else m['frames'],m['frames']),args.every):
        frame=frame_at(cap,i)
        if stage=='source':
            for d in detection[i]['detections']:
                x,y,w,h=d['box']; cv2.rectangle(frame,(x,y),(x+w,y+h),(0,255,0),2)
            rows.append(('source',i,frame))
        else:
            for t in tracks['frames'][i]['targets']:
                if wanted and t['id'] not in wanted:continue
                x,y=np.rint(t['center']).astype(int); ax,ay=np.ceil(np.array(t['axes'])+t['padding_px']+20).astype(int)
                if stage=='tracks':
                    overlay=frame.copy()
                    outline=cv2.morphologyEx(masks(m,tracks,i),cv2.MORPH_GRADIENT,np.ones((3,3),np.uint8))
                    overlay[outline>0]=(0,255,0)
                else:overlay=frame
                rows.append((t['id'],i,overlay[max(0,y-ay):min(m['height'],y+ay),max(0,x-ax):min(m['width'],x+ax)].copy()))
    cap.release()
    if not rows:raise ValueError('No frames or targets in review range.')
    out=job/'qc'/f'{stage}-{hashlib.sha256(json.dumps(bound,sort_keys=True).encode()).hexdigest()[:12]}'
    out.mkdir(parents=True,exist_ok=True); pages=[]
    for tid in sorted({r[0] for r in rows}):
        group=[r for r in rows if r[0]==tid]
        for k in range(0,len(group),40):
            subset=group[k:k+40]; tiles=[]
            for _,i,crop in subset:
                h,w=crop.shape[:2]; scale=min(220/w,180/h)
                thumb=cv2.resize(crop,(max(1,round(w*scale)),max(1,round(h*scale))))
                tile=np.zeros((205,220,3),np.uint8)
                tile[25:25+thumb.shape[0],:thumb.shape[1]]=thumb
                cv2.putText(tile,f'{tid} f={i} t={i/float(Fraction(m["fps"])):.3f}',(3,17),cv2.FONT_HERSHEY_SIMPLEX,.4,(255,255,255),1)
                tiles.append(tile)
            tiles.extend(np.zeros((205,220,3),np.uint8) for _ in range((-len(tiles))%8))
            canvas=cv2.vconcat([cv2.hconcat(tiles[j:j+8]) for j in range(0,len(tiles),8)])
            name=f'{tid}-{k//40+1:04d}.jpg'; image_write(out/name,canvas)
            pages.append({'path':str((out/name).relative_to(job)),'sha256':sha(out/name),'target':tid,'frames':[r[1] for r in subset]})
    index=out/('index-'+hashlib.sha256(json.dumps([(p['target'],p['frames']) for p in pages]).encode()).hexdigest()[:8]+'.json')
    save(index,{'stage':stage,'binding':bound,'pages':pages})
    print(json.dumps({'index':str(index),'pages':[str(job/p['path']) for p in pages]},ensure_ascii=False))


def approve(args):
    index=read(args.index); job=args.job
    if index['stage']=='source':raise ValueError('Source contact sheets do not constitute target QC.')
    if binding(job,index['stage'])!=index['binding']:raise ValueError('Review pages are stale.')
    pages=index['pages'] if args.pages=='all' else [p for p in index['pages'] if Path(p['path']).name in args.pages.split(',')]
    if not pages:raise ValueError('No matching pages.')
    for page in pages:
        path=(job/page['path']).resolve()
        if not path.is_relative_to(job.resolve()) or sha(path)!=page['sha256']:raise ValueError('Review page changed or escaped job directory.')
    approvals=read(job/'approvals.json') if (job/'approvals.json').exists() else []
    approvals.append({'stage':index['stage'],'binding':index['binding'],'reviewer':args.reviewer,'at':datetime.now(timezone.utc).isoformat(),'pages':pages})
    save(job/'approvals.json',approvals)
    print(json.dumps({'approved_pages':len(pages),'stage':index['stage']}))


def require_review(job,stage,tracks):
    bound=binding(job,stage); covered=set()
    approvals=read(job/'approvals.json') if (job/'approvals.json').exists() else []
    for a in approvals:
        if a['stage']==stage and a['binding']==bound:
            for p in a['pages']:
                if sha(job/p['path'])!=p['sha256']:raise ValueError('Approved review image changed.')
                covered.update((p['target'],i) for i in p['frames'])
    needed={(t['id'],f['frame']) for f in tracks['frames'] for t in f['targets']}
    missing=needed-covered
    if missing:raise ValueError(f'{stage}: {len(missing)} target-frames have no recorded visual review; inspect pages then approve them.')


def render(args):
    job=args.job; m,tracks=current_tracks(job)
    require_review(job,'tracks',tracks)
    source=Path(m['source'])
    if sha(source)!=m['source_sha256']:raise ValueError('Original source changed.')
    trackhash=sha(job/'tracks.json')
    output=(args.output or job/f'censored-{trackhash[:10]}.mp4').expanduser().resolve()
    if output==source.resolve() or output.exists():raise ValueError('Output must be a new file distinct from input.')
    if m['width']%2 or m['height']%2:raise ValueError('H.264 4:2:0 requires even dimensions; agree a padding policy first.')
    output.parent.mkdir(parents=True,exist_ok=True)
    block=args.block_size or max(12,round(min(m['width'],m['height'])/720*24))
    if block<8:raise ValueError('block-size must be at least 8.')
    cmd=['ffmpeg','-hide_banner','-v','error','-n','-f','rawvideo','-pix_fmt','bgr24','-s',f'{m["width"]}x{m["height"]}','-r',m['fps'],'-i','pipe:0','-ss',str(m['start']),'-t',str(m['end']-m['start']),'-i',str(source),'-map','0:v:0','-map','1:a:0?','-c:v','libx264','-crf','16','-preset','medium','-pix_fmt','yuv420p','-c:a','aac','-b:a','128k','-t',str(m['frames']/float(Fraction(m['fps']))),'-map_metadata','-1','-movflags','+faststart']
    for key,flag in (('color_primaries','-color_primaries'),('color_transfer','-color_trc'),('color_space','-colorspace')):
        if key=='color_space' and m['color'].get(key) in ('gbr','rgb'):
            # RGB source matrix labels are invalid for this YUV H.264 output.
            # Let swscale convert the raw BGR frames without copying that tag.
            continue
        if key in m['color']:cmd+=[flag,m['color'][key]]
    cmd.append(str(output)); cap=cv2.VideoCapture(str(job/'clip.mkv'))
    status(job,'render','running',output=str(output))
    log=job/'ffmpeg-render.log'
    with log.open('wb') as error:
        proc=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=error)
        try:
            for i in range(m['frames']):
                ok,frame=cap.read()
                if not ok:raise RuntimeError(f'Missing frame {i}')
                mask=masks(m,tracks,i)
                if args.style=='solid':replacement=np.zeros_like(frame)
                else:
                    replacement=cv2.GaussianBlur(frame,(0,0),max(8,block/3))
                    if args.style=='mosaic':replacement=cv2.resize(cv2.resize(replacement,(math.ceil(m['width']/block),math.ceil(m['height']/block)),interpolation=cv2.INTER_AREA),(m['width'],m['height']),interpolation=cv2.INTER_NEAREST)
                frame[mask>0]=replacement[mask>0]
                proc.stdin.write(frame.tobytes())
        finally:
            cap.release(); proc.stdin.close(); code=proc.wait()
    if code:raise RuntimeError(f'ffmpeg failed ({code}); inspect {log}')
    save(job/'render.json',{'output':str(output),'output_sha256':sha(output),'tracks_sha256':trackhash,'style':args.style,'block_size':block})
    status(job,'render','succeeded',output=str(output),next='export_visual_review_required')
    print(json.dumps({'output':str(output)},ensure_ascii=False))


def verify(args):
    job=args.job; m,tracks=current_tracks(job); binding(job,'export')
    result=read(job/'render.json'); output=Path(result['output'])
    require_review(job,'tracks',tracks); require_review(job,'export',tracks)
    info,v=video_info(output); audio=[s for s in info['streams'] if s['codec_type']=='audio']
    cap=cv2.VideoCapture(str(output)); count=0
    while True:
        ok,frame=cap.read()
        if not ok:break
        if frame.shape[:2]!=(m['height'],m['width']):raise RuntimeError('Export dimension mismatch.')
        count+=1
    cap.release()
    if count!=m['frames']:raise RuntimeError(f'Frame count mismatch: {count}/{m["frames"]}')
    fps=float(Fraction(m['fps'])); expected=m['frames']/fps
    if abs(float(v['duration'])-expected)>1/fps+.002:raise RuntimeError('Video duration mismatch.')
    if abs(float(v['duration'])-(m['end']-m['start']))>1/fps+.002:raise RuntimeError('Trim duration mismatch.')
    if abs(float(Fraction(v['avg_frame_rate']))-fps)>.001:raise RuntimeError('Frame rate mismatch.')
    if bool(audio)!=m['has_audio']:raise RuntimeError('Audio stream presence mismatch.')
    if audio and abs(float(audio[0]['duration'])-min(expected,m['end']-m['start']))>1/fps+.03:raise RuntimeError('Audio duration mismatch.')
    subprocess.run(['ffmpeg','-hide_banner','-v','error','-xerror','-i',str(output),'-f','null','-'],check=True)
    report={'technical_pass':True,'visual_review_recorded':True,'frames':count,'duration':v['duration'],'dimensions':[m['width'],m['height']],'audio_present':bool(audio),'source_sha256':m['source_sha256'],'clip_sha256':m['clip_sha256'],'targets_sha256':sha(job/'targets.json'),'tracks_sha256':sha(job/'tracks.json'),'output_sha256':sha(output),'script_sha256':sha(__file__)}
    save(job/'verification.json',report); status(job,'verify','succeeded',frames=count,output=str(output))
    print(json.dumps(report))


def main():
    p=argparse.ArgumentParser(description=__doc__); subs=p.add_subparsers(dest='command',required=True)
    for name in ('prepare','track','review','approve','render','verify'):
        sub=subs.add_parser(name); sub.add_argument('--job',type=Path,required=True)
        if name=='prepare':
            sub.add_argument('--source',type=Path,required=True); sub.add_argument('--start',type=float,required=True); sub.add_argument('--end',type=float,required=True); sub.add_argument('--fps')
        elif name=='track':sub.add_argument('--targets',type=Path,required=True)
        elif name=='review':
            sub.add_argument('--stage',choices=['source','tracks','export'],required=True); sub.add_argument('--every',type=int,default=1); sub.add_argument('--first',type=int,default=0); sub.add_argument('--last',type=int); sub.add_argument('--targets')
        elif name=='approve':
            sub.add_argument('--index',type=Path,required=True); sub.add_argument('--pages',default='all'); sub.add_argument('--reviewer',required=True)
        elif name=='render':
            sub.add_argument('--output',type=Path); sub.add_argument('--style',choices=['mosaic','solid','blur'],default='mosaic'); sub.add_argument('--block-size',type=int)
    args=p.parse_args(); args.job=args.job.expanduser().resolve()
    args.job.mkdir(parents=True,exist_ok=True)
    if not shutil.which('ffmpeg') or not shutil.which('ffprobe'):raise RuntimeError('ffmpeg and ffprobe must be on PATH.')
    if args.command=='review' and (args.every<1 or args.first<0 or args.last is not None and args.last<=args.first):raise ValueError('Invalid review frame interval.')
    try:globals()[args.command](args)
    except Exception as exc:
        status(args.job,args.command,'failed',error=str(exc));raise


if __name__=='__main__':
    try:main()
    except Exception as exc:
        print(f'ERROR: {exc}',file=sys.stderr);sys.exit(1)
