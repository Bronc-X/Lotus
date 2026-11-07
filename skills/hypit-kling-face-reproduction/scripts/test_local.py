"""Isolated real Hypit execution with synthetic media; no cloud or browser calls."""
from __future__ import annotations
import argparse
import datetime
import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import tempfile
import time
from common import SKILL_ROOT, PORTS, digest, read_json, write_json, discover_cli

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--hypit-cli', required=True)
    parser.add_argument('--ffmpeg', default='ffmpeg')
    parser.add_argument('--ffprobe', default='ffprobe')
    parser.add_argument('--font')
    parser.add_argument('--report', type=Path)
    args = parser.parse_args()
    argv = discover_cli(args.hypit_cli)
    version = subprocess.check_output(argv+['--version'], text=True).strip()
    report = {'format':'hypit.kling-skill-local-validation@1',
              'status':'RUNNING','startedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),
              'scope':'Synthetic local fixture, actual Hypit Build/Result and media helpers only',
              'hypitVersion':version,'platform':platform.system(),'cloudGenerationPerformed':False,
              'browserPerformed':False,'independentForwardTestPerformed':False,
              'faceIdentityQualityAccepted':False,'optimizationClaim':'UNASSESSED','cases':[]}
    project = None
    def command(name, command_argv, cwd=None, expected=0, timeout=60):
        environment = os.environ.copy()
        environment.update({'PYTHONIOENCODING':'utf-8','PYTHONDONTWRITEBYTECODE':'1'})
        result = subprocess.run(command_argv, cwd=cwd, capture_output=True, text=True,
                                encoding='utf-8', errors='replace', env=environment, timeout=timeout)
        passed = result.returncode == expected if expected is not None else result.returncode != 0
        report['cases'].append({'case':name,'status':'PASS' if passed else 'FAIL',
                                'exitCode':result.returncode,'stdoutSha256':hashlib.sha256(result.stdout.encode()).hexdigest(),
                                'stderrSha256':hashlib.sha256(result.stderr.encode()).hexdigest()})
        if not passed:
            raise RuntimeError(f'{name} failed: '+(result.stdout+result.stderr)[-4000:])
        return result
    try:
        with tempfile.TemporaryDirectory(prefix='hypit-kling-fixture-') as isolated:
            root = Path(isolated)
            source = root/'source.mp4'
            generated = root/'downloaded-fixture.mp4'
            command('synthetic-source', [args.ffmpeg,'-hide_banner','-v','error','-y','-f','lavfi','-i',
                'testsrc2=size=320x240:rate=30:duration=2','-f','lavfi','-i','sine=frequency=440:sample_rate=48000:duration=2',
                '-c:v','libx264','-pix_fmt','yuv420p','-c:a','aac','-b:a','96k',str(source)])
            command('synthetic-generated-fixture', [args.ffmpeg,'-hide_banner','-v','error','-y','-i',str(source),
                '-map','0:v:0','-c:v','copy','-an',str(generated)])
            photos = []
            for index, color in enumerate(['red','green','blue','yellow','purple']):
                photo = root/f'portrait-{index}.png'
                command(f'synthetic-image-{index+1}',[args.ffmpeg,'-hide_banner','-v','error','-y','-f','lavfi','-i',
                    f'color=c={color}:size=96x96:duration=0.04','-frames:v','1','-threads:v','1',str(photo)])
                photos.append(photo)
            scripts = SKILL_ROOT/'scripts'
            init = [sys.executable,str(scripts/'init_project.py'),'--hypit-cli',args.hypit_cli,
                    '--source',str(source),'--source-upload',str(source)]
            bad_args = [item for port in PORTS for item in ['--'+port,str(photos[0])]]
            command('reject-repeated-identity-photo',init+['--project',str(root/'rejected')]+bad_args,expected=None)
            if (root/'rejected').exists():
                raise RuntimeError('Invalid repeated identities created a project before rejection')
            project = root/'project'
            photo_args = [item for port,photo in zip(PORTS,photos) for item in ['--'+port,str(photo)]]
            command('initialize-check-plan-runtime-selection',init+['--project',str(project)]+photo_args)
            build_output = command('actual-hypit-build',argv+['build','build.svrun','--runtime','hypit.runtime.json','--json'],cwd=project)
            build = json.loads(build_output.stdout)['build']['id']
            deadline = time.monotonic()+30
            requests = []
            while time.monotonic()<deadline:
                requests = list((project/'exchange').glob('*/request.json'))
                if requests:
                    break
                time.sleep(.3)
            if len(requests)!=1:
                raise RuntimeError('Expected one durable local request from the real Build')
            request = read_json(requests[0])
            job = request['jobId']
            identities = request['inputs']['identities']
            assert [item['port'] for item in identities]==list(PORTS)
            assert len({item['resource'] for item in identities})==5
            for item in [request['inputs']['source'],request['inputs']['uploadVideo'],*identities]:
                assert item['personReference'] is True
                assert digest(requests[0].parent/item['file'])==item['sha256']
            assert request['submission']['authorized'] is False
            report['cases'].append({'case':'five-ports-seven-frozen-resources-no-submission','status':'PASS','resourceCount':7})
            command('reject-wrong-local-job', [sys.executable,str(scripts/'complete.py'),'--project',str(project),
                '--job','0'*24,'--video',str(generated),'--model','local-fixture','--provenance','local-fixture'],expected=None)
            command('record-fixture-observation', [sys.executable,str(scripts/'receipt.py'),'--project',str(project),
                '--job',job,'--status','running','--model','local-fixture','--creation-resource-id','fixture-resource','--approved-credits','0'])
            complete = [sys.executable,str(scripts/'complete.py'),'--project',str(project),'--job',job,
                        '--video',str(generated),'--model','local-fixture','--provenance','local-fixture']
            command('complete-existing-fixture',complete)
            command('complete-same-fixture-idempotently',complete)
            receipt = read_json(requests[0].parent/'receipt.json')
            assert receipt['creationResourceId']=='fixture-resource' and receipt['approvedCredits']==0
            assert receipt['taskId'] is None and receipt['fileProvenance']=='local-fixture'
            report['cases'].append({'case':'preserve-observation-evidence-and-null-task-id','status':'PASS'})
            deadline = time.monotonic()+35
            while time.monotonic()<deadline:
                status = subprocess.run(argv+['status',build,'--runtime','hypit.runtime.json','--json'],cwd=project,
                    capture_output=True,text=True,encoding='utf-8',errors='replace')
                if status.returncode:
                    raise RuntimeError('Status failed: '+status.stderr)
                data = json.loads(status.stdout)['build']
                if data['work'].get('outcome')=='complete':
                    break
                if data['work'].get('outcome') in {'failed','cancelled'}:
                    raise RuntimeError('Fixture Build failed: '+status.stdout)
                time.sleep(.5)
            else:
                raise RuntimeError('Timed out waiting for local fixture collection')
            inspect = command('inspect-valid-operation-receipt',argv+['inspect',build,'--output','edit.video','--json'],cwd=project)
            assert json.loads(inspect.stdout)['build']['outcome']=='complete'
            edited = project/'output/edited.mp4'
            command('get-real-result-output',argv+['get',build,'--output','edit.video','--to','output/edited.mp4'],cwd=project)
            assert digest(edited)==digest(generated)
            report['cases'].append({'case':'result-export-byte-equality','status':'PASS','byteCount':edited.stat().st_size})
            final = project/'output/final.mp4'
            command('finalize-original-audio', [sys.executable,str(scripts/'finalize.py'),'--generated',str(edited),
                '--source',str(source),'--output',str(final),'--parent-build',build,'--parent-job',job,
                '--ffmpeg',args.ffmpeg,'--ffprobe',args.ffprobe])
            qc = read_json(project/'output/final-qc/final-QC.json')
            assert all(qc['checks'].values()) and qc['audio_packet_hash']['equal']
            assert qc['parent']['build']==build and qc['file_sha256']['generated']==digest(generated)
            report['cases'].append({'case':'final-frame-color-audio-payload-and-provenance','status':'PASS','checks':qc['checks'],
                                    'audioPackets':qc['audio_packet_hash']['final']['packet_count']})
            compare = project/'output/comparison.mp4'
            comparison_args = [sys.executable,str(scripts/'compare_sync.py'),'--left',str(final),'--right',str(final),
                '--output',str(compare),'--left-label','Fixture A','--right-label','Fixture B','--height','240',
                '--ffmpeg',args.ffmpeg,'--ffprobe',args.ffprobe]
            if args.font:
                comparison_args+=['--font',args.font]
            command('frame-synchronous-comparison',comparison_args)
            comparison_qc = read_json(compare.with_suffix('.qc.json'))
            assert all(comparison_qc['checks'].values()) and comparison_qc['clock']['retime'] is False
            command('reject-comparison-overwrite',comparison_args,expected=None)
            different = root/'different-fps.mp4'
            command('synthetic-different-fps',[args.ffmpeg,'-hide_banner','-v','error','-y','-i',str(final),
                '-vf','fps=24','-an','-c:v','libx264',str(different)])
            mismatch_args = comparison_args.copy()
            mismatch_args[mismatch_args.index('--right')+1]=str(different)
            mismatch_args[mismatch_args.index('--output')+1]=str(project/'output/rejected.mp4')
            command('reject-unmatched-frame-clock',mismatch_args,expected=None)
            report['status']='TECHNICAL_PASS'
            report['fixture']={'sourceFrames':60,'sourceFrameRate':'30','identityImages':5,'realHypitBuildResultCollected':True,
                               'newCloudTaskCount':0,'visualIdentityVerdict':'not_applicable_synthetic_fixture'}
            command('stop-isolated-runtime',argv+['runtime','down','hypit.runtime.json'],cwd=project)
            project = None
    except Exception as error:
        report['status']='FAILED'
        report['failure']=str(error).replace(args.hypit_cli,'<installed-hypit>')
        print(str(error),file=sys.stderr)
    finally:
        if project is not None and project.exists():
            subprocess.run(argv+['runtime','down','hypit.runtime.json'],cwd=project,capture_output=True)
        report['finishedAt']=datetime.datetime.now(datetime.timezone.utc).isoformat()
        report['passedCases']=sum(item['status']=='PASS' for item in report['cases'])
        report['failedCases']=sum(item['status']=='FAIL' for item in report['cases'])
        if args.report:
            write_json(args.report.resolve(),report)
        print(json.dumps(report,ensure_ascii=False,indent=2))
    return 0 if report['status']=='TECHNICAL_PASS' else 1

if __name__=='__main__':
    raise SystemExit(main())
