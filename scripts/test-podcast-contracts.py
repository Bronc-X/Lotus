"""Offline checks for the three runners, original-recording gates and copy research tools.

No model download, private enrollment, audio publication or global installation.
"""
import ast
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'skills/ai-podcast/scripts'))


def load_runner(name):
    spec = importlib.util.spec_from_file_location(name.replace('-', '_'), ROOT/'skills'/name/'scripts/synthesize.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class PodcastContracts(unittest.TestCase):
    def test_all_runners_share_guards_and_keep_voice_identity(self):
        guard = (ROOT/'skills/ai-podcast/scripts/synthesis_contract.py').read_bytes()
        with tempfile.TemporaryDirectory() as d:
            for name in ('ai-podcast', 'toni-voice', 'brian-voice'):
                with self.subTest(skill=name):
                    self.assertEqual((ROOT/'skills'/name/'scripts/synthesis_contract.py').read_bytes(), guard)
                    module = load_runner(name)
                    job = module.normalize_job({'language':'zh','output':'new.wav','chunks':['A sentence.']},Path(d))
                    self.assertEqual(job['chunks'][0]['text'], 'A sentence.')
                    self.assertNotEqual(module.job_fingerprint(job,{}, {'voice_id':'one'}),
                                        module.job_fingerprint(job,{}, {'voice_id':'two'}))
                    with self.assertRaises(ValueError):
                        module.normalize_job({'language':'zh','output':'new.wav','speed':float('nan'),'chunks':['A sentence.']},Path(d))

    def test_packaged_python_parses(self):
        for name in ('ai-podcast','toni-voice','brian-voice','lieflat-less-ai-tone'):
            for script in (ROOT/'skills'/name/'scripts').glob('*.py'):
                ast.parse(script.read_text(encoding='utf-8-sig'), filename=str(script))

    def test_copy_research_empty_and_nonchinese_input(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            empty, english, chinese = root/'empty', root/'english', root/'chinese'
            for folder in (empty,english,chinese):folder.mkdir()
            (english/'sample.md').write_text('This fixture contains no Chinese.',encoding='utf-8')
            (chinese/'sample.md').write_text('这段文字只用于检查脚本。\n这是另一段可比较的文字。',encoding='utf-8')
            folder = ROOT/'skills/lieflat-less-ai-tone/scripts'
            cases = [('check-structure.py',['--human',str(empty),'--ai',str(chinese)]),
                     ('check-structure.py',['--human',str(chinese),'--ai',str(chinese)]),
                     ('check-translationese.py',[str(english)]),
                     ('check-translationese.py',[str(english),str(chinese)]),
                     ('compare-human-ai.py',['--human',str(empty),'--ai',str(chinese)])]
            for name,args in cases:
                result=subprocess.run([sys.executable,'-X','utf8','-B',str(folder/name),*args],capture_output=True,text=True,encoding='utf-8')
                self.assertEqual(result.returncode,0,result.stderr)

    @unittest.skipUnless(shutil.which('pwsh'), 'PowerShell 7 unavailable')
    def test_recording_blank_and_brand_scaffolds_and_ungranted_release(self):
        scripts=ROOT/'skills/recording/scripts'
        with tempfile.TemporaryDirectory() as d:
            for brand in ('Blank','DeepEvolutions'):
                target=Path(d)/brand
                args=['pwsh','-NoProfile','-File',str(scripts/'new_recording_project.ps1'),'-ProjectId','audit-fixture','-Title','Audit fixture','-Destination',str(target),'-BrandProfile',brand]
                made=subprocess.run(args,capture_output=True,text=True,encoding='utf-8')
                self.assertEqual(made.returncode,0,made.stderr)
                qa=['pwsh','-NoProfile','-File',str(scripts/'qa_recording_project.ps1'),'-ProjectRoot',str(target)]
                result=subprocess.run(qa,capture_output=True,text=True,encoding='utf-8')
                self.assertEqual(result.returncode,0,result.stdout+result.stderr)
                marker=target/'source-sentinel.txt'
                marker.write_text('Keep original',encoding='utf-8')
                self.assertNotEqual(subprocess.run(args,capture_output=True).returncode,0)
                self.assertEqual(marker.read_text(encoding='utf-8'),'Keep original')
                state=target/'state/project-state.json'
                data=json.loads(state.read_text(encoding='utf-8-sig'))
                data['current_state']='S100_RELEASE_AUTHORIZED'
                state.write_text(json.dumps(data),encoding='utf-8')
                self.assertNotEqual(subprocess.run(qa,capture_output=True).returncode,0)


if __name__=='__main__':
    unittest.main()
