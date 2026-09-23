"""Enroll a human reference into a NEW local voice profile (candidate until listened to)."""
import argparse
import json
from pathlib import Path
import shutil
import time
from runtime_support import load_runtime, configure
from synthesize import digest, save


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--runtime', type=Path, required=True)
    p.add_argument('--reference', type=Path, required=True)
    p.add_argument('--transcript', type=Path, required=True)
    p.add_argument('--voice-id', required=True)
    p.add_argument('--language', choices=['zh', 'en'], required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    if a.output.exists():
        raise FileExistsError('Preserve existing voice profiles; use a new output directory.')
    transcript = a.transcript.read_text(encoding='utf-8-sig').strip()
    if not transcript:
        raise ValueError('Provide the exact transcript of the selected human reference.')
    cfg = load_runtime(a.runtime)
    import numpy as np
    import soundfile as sf
    import torch
    from omnivoice import OmniVoice
    audio, sr = sf.read(a.reference, dtype='float32')
    if audio.ndim != 1 or not 3 <= len(audio) / sr <= 10:
        raise ValueError('Select a mono WAV reference of 3–10 seconds at a sentence boundary.')
    if not np.isfinite(audio).all() or not np.any(audio) or np.max(np.abs(audio)) >= 1:
        raise ValueError('Reference is silent, clipped, or invalid; repair recording first.')
    dtype = configure(cfg, torch)
    if not cfg.get('model_revision'):
        raise ValueError('Record the installed model revision in runtime.json.')
    a.output.mkdir(parents=True)
    assets = a.output / 'assets'
    assets.mkdir()
    save(a.output / 'status.json', {'status': 'running'})
    start = time.monotonic()
    try:
        shutil.copy2(a.reference, assets / 'reference.wav')
        model = OmniVoice.from_pretrained(cfg['model_path'], device_map=cfg['device'], dtype=dtype)
        prompt = model.create_voice_clone_prompt(ref_audio=str(assets / 'reference.wav'), ref_text=transcript)
        prompt.save(str(assets / 'voice.pt'))
        profile = dict(voice_id=a.voice_id, model='k2-fsa/OmniVoice',
                       model_revision=cfg['model_revision'], code_revision=cfg['actual_code_revision'],
                       method='reference cloning; no parameter fine-tuning',
                       source_sha256=digest(a.reference), languages=[a.language],
                       listening_verified_languages=[], status='candidate_pending_listening',
                       default_prompt='narration', prompts={'narration': {
                           'asset': 'voice.pt', 'reference_asset': 'reference.wav', 'reference_text': transcript}},
                       assets={f: digest(assets / f) for f in ('reference.wav', 'voice.pt')})
        save(a.output / 'voice.json', profile)
        report = dict(status='complete_pending_listening', elapsed_seconds=time.monotonic()-start,
                      device=cfg['device'], dtype=cfg['dtype'], voice_id=a.voice_id)
        save(a.output / 'status.json', report)
        print(json.dumps(report))
    except Exception as exc:
        save(a.output / 'status.json', dict(status='failed', error=str(exc)))
        raise


if __name__ == '__main__':
    main()
