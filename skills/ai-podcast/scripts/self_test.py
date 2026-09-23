"""Offline contract checks; no model download, external upload or approval fabrication."""
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from release_manifest import create, verify, sha
from runtime_support import choose_device
from synthesize import normalize_job, job_fingerprint


class Contracts(unittest.TestCase):
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


if __name__ == '__main__':
    unittest.main()
