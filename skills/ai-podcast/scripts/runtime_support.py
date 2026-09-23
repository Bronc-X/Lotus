"""Local-only OmniVoice runtime. No automatic model downloads or device failover."""
import json
import os
from pathlib import Path
import subprocess
import sys


def load_runtime(path):
    path = Path(path).resolve()
    cfg = json.loads(path.read_text(encoding='utf-8-sig'))
    for field in ('repository_path', 'model_path'):
        value = Path(cfg[field]).expanduser()
        cfg[field] = str((path.parent / value).resolve())
        if not Path(cfg[field]).is_dir():
            raise FileNotFoundError(f'Missing {field}: {cfg[field]}')
    cfg['dependency_paths'] = [str((path.parent / Path(p).expanduser()).resolve())
                               for p in cfg.get('dependency_paths', [])]
    for p in cfg['dependency_paths']:
        if not Path(p).is_dir():
            raise FileNotFoundError(p)
    os.environ['HF_HUB_OFFLINE'] = '1'
    os.environ['HF_HUB_DISABLE_IMPLICIT_TOKEN'] = '1'
    os.environ['HF_HUB_DISABLE_TELEMETRY'] = '1'
    sys.path.insert(0, cfg['repository_path'])
    sys.path.extend(cfg['dependency_paths'])
    return cfg


def choose_device(requested, torch):
    mps = getattr(torch.backends, 'mps', None)
    has_mps = mps is not None and mps.is_available()
    if requested == 'auto':
        requested = 'cuda:0' if torch.cuda.is_available() else ('mps' if has_mps else 'cpu')
    if requested.startswith('cuda'):
        if not torch.cuda.is_available():
            raise RuntimeError('CUDA unavailable; choose a new CPU runtime/output explicitly.')
    elif requested == 'mps':
        if not has_mps:
            raise RuntimeError('MPS unavailable; choose a new CPU runtime/output explicitly.')
    elif requested != 'cpu':
        raise ValueError('Supported device: auto, cpu, mps, cuda or cuda:N.')
    return requested


def configure(cfg, torch):
    cfg['device'] = choose_device(cfg.get('device', 'auto'), torch)
    dtype = cfg.get('dtype', 'auto')
    if dtype == 'auto':
        dtype = 'float16' if cfg['device'].startswith('cuda') else 'float32'
    if dtype not in ('float16', 'float32') or (cfg['device'] == 'cpu' and dtype != 'float32'):
        raise ValueError('Use CPU float32; GPU float16 or float32. Rebenchmark changed precision.')
    cfg['dtype'] = dtype
    defaults = dict(num_step=32, seed=42, cpu_threads=4, max_batch_size=1,
                    gap_seconds=0.12, target_rms_db=-20, peak_ceiling_db=-1,
                    postprocess_output=False, edge_trim_threshold=0.001,
                    edge_margin_seconds=0.08, edge_fade_seconds=0.005)
    for key, value in defaults.items():
        cfg.setdefault(key, value)
    torch.set_num_threads(int(cfg['cpu_threads']))
    assert (torch.ones(1, device=cfg['device']) + 1).item() == 2
    # Include installed code and numerical backend in resume fingerprints.
    result = subprocess.run(['git', '-C', cfg['repository_path'], 'rev-parse', 'HEAD'],
                            check=True, capture_output=True, text=True)
    cfg['actual_code_revision'] = result.stdout.strip()
    cfg['torch_version'] = torch.__version__
    return getattr(torch, dtype)


def check_revision(cfg, voice):
    expected = voice.get('code_revision')
    if expected and cfg['actual_code_revision'] != expected:
        raise ValueError('OmniVoice code revision differs from the selected voice; validate a separate profile.')
    expected = voice.get('model_revision')
    if expected and cfg.get('model_revision') != expected:
        raise ValueError('Set runtime model_revision to the revision actually installed for this voice.')
