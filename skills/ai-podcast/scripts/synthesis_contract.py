"""Local I/O and numeric guards shared by the standalone synthesis entry points."""
from contextlib import contextmanager
import math
import os
from pathlib import Path


def finite_number(value, name, minimum=None, maximum=None, strict_minimum=False):
    if isinstance(value, bool):
        raise ValueError(f'{name} must be a finite number, not a boolean.')
    try:
        result = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f'{name} must be a finite number.') from exc
    if not math.isfinite(result):
        raise ValueError(f'{name} must be finite.')
    if minimum is not None and (result <= minimum if strict_minimum else result < minimum):
        raise ValueError(f'{name} is below its allowed range.')
    if maximum is not None and result > maximum:
        raise ValueError(f'{name} is above its allowed range.')
    return result


def validate_runtime_numbers(cfg):
    for name, low, high in [('gap_seconds', 0, None), ('edge_trim_threshold', 0, 1),
                            ('edge_margin_seconds', 0, None), ('edge_fade_seconds', 0, None),
                            ('target_rms_db', None, 0), ('peak_ceiling_db', None, 0)]:
        if name in cfg:
            finite_number(cfg[name], name, low, high)
    for name, low, high in [('num_step', 1, None), ('cpu_threads', 1, None),
                            ('max_batch_size', 1, 4), ('seed', 0, None)]:
        if name in cfg:
            value = cfg[name]
            if isinstance(value, bool) or not isinstance(value, int):
                raise ValueError(f'{name} must be an integer.')
            finite_number(value, name, low, high)


def linked(path):
    return path.is_symlink() or (hasattr(path, 'is_junction') and path.is_junction())


def require_voice_identity(voice, speaker):
    if not isinstance(voice.get('voice_id'), str) or not voice['voice_id'].startswith(speaker + '-'):
        raise ValueError(f'This runner requires a {speaker} voice profile; a different speaker was selected.')


def validate_output_paths(jobs, protected):
    """Reserve WAV, sidecars and cache trees before any synthesis writes occur."""
    protected = {Path(p).resolve() for p in protected}
    targets, caches = set(), []
    for job in jobs:
        out = job['output']
        siblings = [out, out.with_suffix('.json'), out.with_suffix('.txt'),
                    out.with_suffix('.tmp.wav'), out.with_suffix('.json.tmp'), out.with_suffix('.lock')]
        cache = out.with_suffix('.parts')
        if linked(cache):
            raise ValueError(f'Cache directory is a link: {cache}')
        caches.append(cache.resolve())
        for path in siblings:
            resolved = path.resolve()
            if linked(path) or resolved in protected or resolved in targets:
                raise ValueError(f'Output collides with an input, another job or a linked file: {path}')
            targets.add(resolved)
        if not out.exists():
            for path in siblings[1:-1]:
                if path.exists():
                    raise FileExistsError(f'Existing sidecar has no matching master; preserve it and use a new output: {path}')
    for cache in caches:
        if any(p == cache or p.is_relative_to(cache) for p in protected | targets):
            raise ValueError(f'Cache directory overlaps a source or output: {cache}')
    if len(set(caches)) != len(caches):
        raise ValueError('Jobs must not share a cache directory.')


@contextmanager
def output_lock(out):
    """Do not let two local jobs write the same master/checkpoints concurrently."""
    out.parent.mkdir(parents=True, exist_ok=True)
    lock = out.with_suffix('.lock')
    try:
        handle = lock.open('x', encoding='utf-8')
    except FileExistsError as exc:
        raise RuntimeError(f'Output is locked: {lock}. Check the owning process before removing a stale lock.') from exc
    with handle:
        handle.write(str(os.getpid()))
    try:
        yield
    finally:
        lock.unlink()
