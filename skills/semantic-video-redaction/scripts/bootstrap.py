"""Create a project-local runtime; no hard-coded machine paths or credentials."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import venv


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--runtime',type=Path,required=True)
    parser.add_argument('--wheelhouse',type=Path)
    parser.add_argument('--diagnose',action='store_true')
    args=parser.parse_args()
    runtime=args.runtime.expanduser().resolve()
    python=runtime/('Scripts/python.exe' if os.name=='nt' else 'bin/python')
    requirements=Path(__file__).with_name('requirements.txt')
    paths={name:shutil.which(name) for name in ('ffmpeg','ffprobe')}
    if args.diagnose:
        print(json.dumps({'host_python':sys.version,'runtime_exists':python.exists(),'tools':paths},ensure_ascii=False,indent=2))
        return
    if not (3,11)<=sys.version_info[:2]<=(3,13):
        raise RuntimeError('Use Python 3.12 (supported bootstrap range 3.11–3.13).')
    if not all(paths.values()):
        raise RuntimeError('ffmpeg and ffprobe must be on PATH; see references/runtime.md.')
    if runtime.exists() and any(runtime.iterdir()) and not (runtime/'pyvenv.cfg').is_file():
        raise RuntimeError('Runtime must be a new empty directory or an existing virtual environment.')
    expected={line.split('==')[0]:line.split('==')[1] for line in requirements.read_text().splitlines() if line.strip()}
    check='import importlib.metadata,json; print(json.dumps({p:importlib.metadata.version(p) for p in '+repr(list(expected))+'}))'
    ready=False
    if python.exists():
        result=subprocess.run([str(python),'-c',check],capture_output=True,text=True)
        if result.returncode==0:
            ready=json.loads(result.stdout)==expected
    if not ready:
        if not python.exists():
            runtime.mkdir(parents=True,exist_ok=True)
            if shutil.which('uv'):
                subprocess.run(['uv','venv','--python',sys.executable,str(runtime)],check=True)
            else:
                venv.EnvBuilder(with_pip=True).create(runtime)
        if shutil.which('uv'):
            cmd=['uv','pip','install','--python',str(python),'-r',str(requirements)]
        else:
            subprocess.run([str(python),'-m','ensurepip','--upgrade'],check=True)
            cmd=[str(python),'-m','pip','install','-r',str(requirements)]
        if args.wheelhouse:
            cmd+=['--no-index','--find-links',str(args.wheelhouse.resolve())]
        subprocess.run(cmd,check=True)
    smoke='''import hashlib,importlib.metadata,json,pathlib,nudenet,numpy as np
from nudenet import NudeDetector
model=pathlib.Path(nudenet.__file__).parent/'320n.onnx'
detector=NudeDetector()
result=detector.detect(np.zeros((320,320,3),dtype=np.uint8))
assert isinstance(result,list)
print(json.dumps({'packages':{p:importlib.metadata.version(p) for p in PACKAGES},'model_file':model.name,'model_sha256':hashlib.sha256(model.read_bytes()).hexdigest(),'providers':detector.onnx_session.get_providers(),'model_smoke_pass':True}))'''.replace('PACKAGES',repr(list(expected)))
    result=subprocess.run([str(python),'-c',smoke],capture_output=True,text=True,check=True)
    record=json.loads(result.stdout)
    record['requirements_sha256']=hashlib.sha256(requirements.read_bytes()).hexdigest()
    record['python']=sys.version.split()[0]
    (runtime/'environment.json').write_text(json.dumps(record,indent=2),encoding='utf-8')
    print(json.dumps({'runtime_python':str(python),'tools':paths,**record},ensure_ascii=False,indent=2))


if __name__=='__main__':
    try: main()
    except Exception as exc:
        print(f'ERROR: {exc}',file=sys.stderr)
        sys.exit(1)
