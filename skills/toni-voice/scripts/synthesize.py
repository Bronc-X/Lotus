"""Pinned Toni voice; local CUDA synthesis with resumable paragraph checkpoints."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]

def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))

def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def fingerprint(data):
    return hashlib.sha256(json.dumps(data,ensure_ascii=False,sort_keys=True).encode()).hexdigest()

def save(path,data):
    tmp=path.with_suffix(path.suffix+'.tmp')
    tmp.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
    tmp.replace(path)

def resolve(base,value):
    path=Path(value).expanduser()
    return (base/path).resolve() if not path.is_absolute() else path.resolve()

def prompt_profiles(voice):
    prompts=voice.get('prompts',{'narration':{'asset':'voice.pt'}})
    default=voice.get('default_prompt','narration')
    if not isinstance(prompts,dict) or not prompts or default not in prompts:
        raise ValueError('Voice profile needs an available default_prompt.')
    for name,profile in prompts.items():
        if name not in ('narration','question'):
            raise ValueError(f'Unknown voice reference: {name}')
        if not isinstance(profile,dict) or profile.get('asset') not in voice['assets']:
            raise ValueError(f'Voice reference has no approved asset hash: {name}')
    return default,prompts

def normalize_job(job,base,default_reference='narration',available_references=('narration','question')):
    if job.get('language') not in ('zh','en'):
        raise ValueError('Set language to zh or en for each job.')
    if 'chunks' in job:
        chunks=[{'text':c} if isinstance(c,str) else dict(c) for c in job['chunks']]
    else:
        text=resolve(base,job['text_file']).read_text(encoding='utf-8-sig')
        chunks=[{'text':p.strip()} for p in re.split(r'\n\s*\n',text) if p.strip()]
    if not chunks or any(not c.get('text','').strip() for c in chunks):
        raise ValueError('Empty narration or paragraph.')
    for c in chunks:
        reference=c.get('reference',default_reference)
        if not isinstance(reference,str) or reference not in available_references:
            raise ValueError(f'Unknown or unavailable voice reference: {reference!r}')
        c['reference']=reference
        d=c.get('duration_seconds')
        if d is not None and (not isinstance(d,(int,float)) or not 0<d<=30):
            raise ValueError('Timed paragraphs must be between 0 and 30 seconds; split longer shots at sentence boundaries.')
    out=resolve(base,job['output'])
    if out.suffix.lower()!='.wav':
        raise ValueError('Output must be a .wav master; export other delivery formats separately.')
    speed=float(job.get('speed',1))
    if speed<=0:raise ValueError('Speed must be positive.')
    timed=any(c.get('duration_seconds') is not None for c in chunks)
    gap=job.get('gap_seconds',0.0 if timed else None)
    if gap is not None and float(gap)<0:raise ValueError('Paragraph gap must be nonnegative.')
    return {'language':job['language'],'chunks':chunks,'output':out,'speed':speed,'timed':timed,'gap_seconds':gap}

def prepare_audio(audio,sr,cfg,duration_seconds=None):
    # Timed shots retain their complete generated waveform and duration.
    if duration_seconds is not None:return audio
    import numpy as np
    threshold=float(cfg.get('edge_trim_threshold',0.001))
    margin=round(sr*float(cfg.get('edge_margin_seconds',0.08)))
    fade_samples=round(sr*float(cfg.get('edge_fade_seconds',0.005)))
    if threshold<0 or margin<0 or fade_samples<0:
        raise ValueError('Edge trim settings must be nonnegative.')
    active=np.flatnonzero(np.abs(audio)>threshold)
    if not len(active):raise RuntimeError('Paragraph has no audible samples above the edge trim threshold.')
    left=max(0,int(active[0])-margin)
    right=min(len(audio),int(active[-1])+margin+1)
    audio=audio[left:right].copy()
    fade=min(fade_samples,len(audio)//2)
    if fade:
        audio[:fade]*=np.linspace(0,1,fade)
        audio[-fade:]*=np.linspace(1,0,fade)
    return audio

def job_fingerprint(job,cfg,voice):
    # Include all approved asset hashes and prompt metadata, even unused prompts.
    return fingerprint({'algorithm_version':2,'job':{**job,'output':str(job['output'])},'profile':cfg,'voice':voice})

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--runtime',type=Path,default=ROOT/'runtime.json')
    p.add_argument('--check',action='store_true')
    p.add_argument('--text-file',type=Path)
    p.add_argument('--language',choices=['zh','en'],default='zh')
    p.add_argument('--output',type=Path)
    p.add_argument('--jobs-file',type=Path)
    a=p.parse_args()
    cfg=read(a.runtime)
    voice=read(ROOT/'voice.json')
    default_reference,profiles=prompt_profiles(voice)
    postprocess_output=cfg.get('postprocess_output',False)
    if not isinstance(postprocess_output,bool):raise ValueError('postprocess_output must be a boolean.')
    for name,expected in voice['assets'].items():
        if digest(ROOT/'assets'/name)!=expected:raise ValueError(f'Approved voice asset changed: {name}')
    for field in ('repository_path','model_path'):
        if not Path(cfg[field]).is_dir():raise FileNotFoundError(f'Repair runtime.json: {field}')
    os.environ['HF_HUB_OFFLINE']='1'
    os.environ['HF_HUB_DISABLE_IMPLICIT_TOKEN']='1'
    os.environ['HF_HUB_DISABLE_TELEMETRY']='1'
    sys.path.insert(0,cfg['repository_path'])
    for path in cfg.get('dependency_paths',[]):
        if not Path(path).is_dir():raise FileNotFoundError(f'Missing dependency path: {path}')
        sys.path.append(path)
    import numpy as np
    import soundfile as sf
    import torch
    from omnivoice import OmniVoice,VoiceClonePrompt
    if not cfg['device'].startswith('cuda') or not torch.cuda.is_available():
        raise RuntimeError('NVIDIA CUDA is unavailable. No CPU or voice-service fallback was performed.')
    if cfg['dtype']!='float16':raise ValueError('Unvalidated runtime dtype; restore float16 or validate a new profile explicitly.')
    torch.set_num_threads(cfg.get('cpu_threads',4))
    prompts={name:VoiceClonePrompt.load(str(ROOT/'assets'/profile['asset'])) for name,profile in profiles.items()}
    info={'voice_id':voice['voice_id'],'torch':torch.__version__,'gpu':torch.cuda.get_device_name(cfg['device']),
        'model_revision':voice['model_revision'],'voice_sha256':voice['assets']['voice.pt'],
        'default_prompt':default_reference,'prompt_assets':{name:{'asset':profile['asset'],'sha256':voice['assets'][profile['asset']]} for name,profile in profiles.items()},
        'default_profile':{'reference':default_reference,'max_batch_size':cfg.get('max_batch_size',4),
            'gap_seconds':cfg['gap_seconds'],'postprocess_output':postprocess_output,
            'edge_trim_threshold':cfg.get('edge_trim_threshold',0.001),'edge_margin_seconds':cfg.get('edge_margin_seconds',0.08),
            'edge_fade_seconds':cfg.get('edge_fade_seconds',0.005)}}
    print(json.dumps({'status':'ready',**info},ensure_ascii=False),flush=True)
    if a.check:
        assert (torch.ones(1,device=cfg['device'])+1).item()==2
        return
    if a.jobs_file:
        jobs=[normalize_job(j,a.jobs_file.resolve().parent,default_reference,profiles) for j in read(a.jobs_file)['jobs']]
    elif a.text_file and a.output:
        jobs=[normalize_job({'language':a.language,'text_file':str(a.text_file.resolve()),'output':str(a.output.resolve())},Path.cwd(),default_reference,profiles)]
    else:p.error('Provide --jobs-file or --text-file and --output.')
    if not jobs:raise ValueError('No jobs supplied.')
    if len({j['output'] for j in jobs})!=len(jobs):raise ValueError('Each job needs a distinct output filename.')
    model=None
    for job in jobs:
        out=job['output']
        cache=out.with_suffix('.parts')
        meta=out.with_suffix('.json')
        key=job_fingerprint(job,cfg,voice)
        if out.exists():
            if meta.exists() and read(meta).get('input_fingerprint')==key and read(meta).get('sha256')==digest(out):
                print(json.dumps({'status':'reused','output':str(out)},ensure_ascii=False),flush=True)
                continue
            raise FileExistsError(f'Existing output differs or lacks its record. Use a new output filename: {out}')
        out.parent.mkdir(parents=True,exist_ok=True)
        cache.mkdir(exist_ok=True)
        state=cache/'status.json'
        save(state,{'status':'running','input_fingerprint':key,'total':len(job['chunks'])})
        try:
            paths=[cache/f'{i+1:04d}.wav' for i in range(len(job['chunks']))]
            missing=[]
            for i,path in enumerate(paths):
                cm=path.with_suffix('.json')
                if path.exists():
                    if not cm.exists() or read(cm).get('input_fingerprint')!=key or read(cm).get('sha256')!=digest(path):
                        raise ValueError(f'Checkpoint mismatch. Preserve it and choose a new output filename: {path}')
                else:missing.append(i)
            if missing and model is None:
                model=OmniVoice.from_pretrained(cfg['model_path'],device_map=cfg['device'],dtype=torch.float16)
            batch_size=max(1,min(4,int(cfg.get('max_batch_size',4))))
            for start in range(0,len(paths),batch_size):
                group=list(range(start,min(start+batch_size,len(paths))))
                if not any(i in missing for i in group):continue
                # Regenerate the complete canonical group after interruption, keeping verified parts.
                # This preserves sampling shape and seed even when only part of a group is missing.
                torch.manual_seed(cfg['seed']+start)
                audios=model.generate(text=[job['chunks'][i]['text'] for i in group],language=job['language'],
                    voice_clone_prompt=[prompts[job['chunks'][i]['reference']] for i in group],duration=[job['chunks'][i].get('duration_seconds') for i in group],
                    speed=job['speed'],num_step=cfg['num_step'],postprocess_output=False if job['timed'] else postprocess_output,
                    pad_duration=0.0 if job['timed'] else 0.1)
                for i,audio in zip(group,audios):
                    if i not in missing:continue
                    if not np.isfinite(audio).all() or not np.any(audio):raise RuntimeError(f'Invalid paragraph {i+1}')
                    temp=paths[i].with_suffix('.tmp.wav')
                    sf.write(temp,audio,model.sampling_rate,subtype='FLOAT')
                    temp.replace(paths[i])
                    save(paths[i].with_suffix('.json'),{'input_fingerprint':key,'sha256':digest(paths[i]),'text':job['chunks'][i]['text'],'reference':job['chunks'][i]['reference']})
                save(state,{'status':'running','completed':sum(path.exists() for path in paths),'total':len(paths)})
                print(json.dumps({'status':'progress','output':str(out),'completed':sum(path.exists() for path in paths),'total':len(paths)},ensure_ascii=False),flush=True)
            arrays=[]
            timeline=[]
            cursor=0
            sr=24000
            for i,path in enumerate(paths):
                audio,rate=sf.read(path,dtype='float32')
                if rate!=sr or audio.ndim!=1:raise ValueError('Unexpected cached audio format.')
                if i:
                    gap_seconds=cfg['gap_seconds'] if job['gap_seconds'] is None else float(job['gap_seconds'])
                    gap=np.zeros(round(sr*gap_seconds),dtype=np.float32)
                    arrays.append(gap)
                    cursor+=len(gap)
                target=job['chunks'][i].get('duration_seconds')
                audio=prepare_audio(audio,sr,cfg,target)
                timing_error=None if target is None else len(audio)/sr-target
                if timing_error is not None and abs(timing_error)>0.1:
                    raise RuntimeError(f'Paragraph {i+1} misses its timing target by {timing_error:.3f}s. Review the saved part.')
                timeline.append({'index':i+1,'text':job['chunks'][i]['text'],'reference':job['chunks'][i]['reference'],'start':cursor/sr,'end':(cursor+len(audio))/sr,'timing_error_seconds':timing_error,
                    'requested_duration_seconds':job['chunks'][i].get('duration_seconds'),'part_file':str(path)})
                arrays.append(audio)
                cursor+=len(audio)
            audio=np.concatenate(arrays)
            rms=float(np.sqrt(np.mean(audio**2)))
            peak=float(np.max(np.abs(audio)))
            gain=min(10**(cfg['target_rms_db']/20)/rms,10**(cfg['peak_ceiling_db']/20)/peak)
            temp=out.with_suffix('.tmp.wav')
            sf.write(temp,audio*gain,sr,subtype='PCM_16')
            check,rate=sf.read(temp)
            if not np.isfinite(check).all() or np.max(np.abs(check))>=1:raise RuntimeError('Output QA failed.')
            temp.replace(out)
            report={'status':'generated_pending_content_and_listening_check','input_fingerprint':key,'sha256':digest(out),**info,
                'duration_seconds':len(check)/rate,'sample_rate':rate,'channels':1,'gain_db':float(20*np.log10(gain)),
                'peak':float(np.max(np.abs(check))),'language':job['language'],'segments':timeline}
            save(meta,report)
            out.with_suffix('.txt').write_text('\n\n'.join(c['text'] for c in job['chunks']),encoding='utf-8')
            save(state,{'status':'complete','output':str(out),'sha256':report['sha256']})
            print(json.dumps({'status':'complete','output':str(out),'duration_seconds':report['duration_seconds']},ensure_ascii=False),flush=True)
        except Exception as exc:
            save(state,{'status':'failed','error':str(exc),'input_fingerprint':key})
            raise

if __name__=='__main__':main()
