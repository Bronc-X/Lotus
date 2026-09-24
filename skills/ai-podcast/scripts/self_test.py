"""Offline contract checks; no model download, external upload or approval fabrication."""
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from release_manifest import create, verify, sha
from runtime_support import choose_device
from synthesize import normalize_job, job_fingerprint, prompt_profiles
from synthesis_contract import validate_output_paths, output_lock, validate_runtime_numbers, require_voice_identity


class Contracts(unittest.TestCase):
    def test_fixed_speaker_profile_mismatch(self):
        require_voice_identity({'voice_id':'brian-fixture'},'brian')
        with self.assertRaises(ValueError):
            require_voice_identity({'voice_id':'toni-fixture'},'brian')

    def test_inputs_and_sidecars_are_preserved(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            source = root / 'episode.txt'
            source.write_text('Original input must not be overwritten', encoding='utf-8')
            job = {'output': root / 'episode.wav'}
            with self.assertRaises(ValueError):
                validate_output_paths([job], [source])
            with self.assertRaises(FileExistsError):
                validate_output_paths([job], [])
            self.assertEqual(source.read_text(encoding='utf-8'), 'Original input must not be overwritten')
            with self.assertRaises(ValueError):
                validate_output_paths([{'output': root/'task.wav'}], [root/'task.json'])
            with self.assertRaises(ValueError):
                validate_output_paths([{'output': root/'a.wav'}, {'output': root/'a.parts'/'b.wav'}], [])
            validate_output_paths([{'output': root/'new.wav'}], [source])

    def test_exclusive_output_lock_and_cleanup(self):
        with tempfile.TemporaryDirectory() as d:
            out = Path(d) / 'test.wav'
            with output_lock(out):
                with self.assertRaises(RuntimeError):
                    with output_lock(out):
                        self.fail('Second owner acquired a busy output')
            self.assertFalse(out.with_suffix('.lock').exists())
            with self.assertRaises(ValueError):
                with output_lock(out):
                    raise ValueError('Simulated synthesis error')
            self.assertFalse(out.with_suffix('.lock').exists())

    def test_nonfinite_parameters_fail_before_generation(self):
        for key, value in [('gap_seconds', float('inf')), ('peak_ceiling_db', float('nan')),
                           ('num_step', True), ('cpu_threads', 0), ('max_batch_size', 5)]:
            with self.subTest(key=key), self.assertRaises(ValueError):
                validate_runtime_numbers({key: value})
        with tempfile.TemporaryDirectory() as d:
            for key, value in [('speed', float('nan')), ('gap_seconds', float('inf'))]:
                with self.subTest(key=key), self.assertRaises(ValueError):
                    normalize_job({'language':'zh','output':'out.wav','chunks':['A sentence.'],key:value}, Path(d))

    def test_devices(self):
        def fake(cuda, mps):
            return SimpleNamespace(cuda=SimpleNamespace(is_available=lambda: cuda),
                                   backends=SimpleNamespace(mps=SimpleNamespace(is_available=lambda: mps)))
        self.assertEqual(choose_device('auto', fake(False, False)), 'cpu')
        self.assertEqual(choose_device('auto', fake(False, True)), 'mps')
        self.assertEqual(choose_device('auto', fake(True, True)), 'cuda:0')
        with self.assertRaises(RuntimeError):
            choose_device('mps', fake(False, False))
        with self.assertRaises(RuntimeError):
            choose_device('cuda:0', fake(False, False))

    def test_timing_and_resume_identity(self):
        with tempfile.TemporaryDirectory() as d:
            job = {'language': 'zh', 'output': 'audio.wav', 'chunks': [{'text': '测试。', 'duration_seconds': 5}]}
            normalized = normalize_job(job, Path(d))
            self.assertEqual(normalized['gap_seconds'], 0)
            first = job_fingerprint(normalized, {'device': 'cpu'}, {})
            self.assertNotEqual(first, job_fingerprint(normalized, {'device': 'mps'}, {}))
            job['chunks'][0]['duration_seconds'] = 31
            with self.assertRaises(ValueError):
                normalize_job(job, Path(d))
            job['chunks'][0] = {'text': '测试。', 'reference': 'another-speaker'}
            with self.assertRaises(ValueError):
                normalize_job(job, Path(d))

    def test_custom_prompt_names(self):
        voice = {'default_prompt': 'calm', 'prompts': {'calm': {'asset': 'calm.pt'},
                 'emphasis': {'asset': 'emphasis.pt'}},
                 'assets': {'calm.pt': 'hash-a', 'emphasis.pt': 'hash-b'}}
        default, prompts = prompt_profiles(voice)
        self.assertEqual(default, 'calm')
        self.assertEqual(set(prompts), {'calm', 'emphasis'})
        with tempfile.TemporaryDirectory() as d:
            job = {'language': 'zh', 'output': 'audio.wav',
                   'chunks': [{'text': '一句话。', 'reference': 'emphasis'}]}
            self.assertEqual(normalize_job(job, Path(d), default, prompts)['chunks'][0]['reference'], 'emphasis')
        voice['prompts']['../escape'] = {'asset': 'calm.pt'}
        with self.assertRaises(ValueError):
            prompt_profiles(voice)

    def test_release_integrity_and_scope(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            release = root / 'release'
            release.mkdir()
            content = release / 'show-notes.txt'
            content.write_text('A reviewed candidate', encoding='utf-8')
            manifest = release / 'manifest.json'
            create(release, manifest)
            self.assertFalse(verify(manifest)['grant_matched'])
            extra = release / 'unreviewed.txt'
            extra.write_text('not in candidate', encoding='utf-8')
            with self.assertRaises(ValueError):
                verify(manifest)
            extra.unlink()
            with self.assertRaises(FileExistsError):
                create(release, manifest)
            grant = root / 'grant.json'
            grant.write_text(json.dumps(dict(candidate_sha256=sha(manifest), platform='fixture',
                account='test', action='upload', evidence='synthetic test fixture, not real authorization')))
            self.assertTrue(verify(manifest, grant, 'fixture', 'test', 'upload')['grant_matched'])
            with self.assertRaises(ValueError):
                verify(manifest, grant, 'fixture', 'test', 'publish')
            with self.assertRaises(ValueError):
                verify(manifest, grant, 'fixture', 'different', 'upload')
            content.write_text('Changed after approval', encoding='utf-8')
            with self.assertRaises(ValueError):
                verify(manifest)

    def test_manifest_duplicate_paths_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root/'audio.txt').write_text('fixture', encoding='utf-8')
            manifest = root/'manifest.json'
            create(root, manifest)
            data = json.loads(manifest.read_text(encoding='utf-8'))
            data['files'].append(data['files'][0])
            manifest.write_text(json.dumps(data), encoding='utf-8')
            with self.assertRaises(ValueError):
                verify(manifest)


if __name__ == '__main__':
    unittest.main()
