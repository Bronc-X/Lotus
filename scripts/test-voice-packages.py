"""Test real installer copy functions in isolated fixtures, without installing globally."""
import os
from pathlib import Path
import shutil
import subprocess
import tempfile

repo = Path(__file__).resolve().parents[1]
fixture = Path(tempfile.mkdtemp(prefix='lotus-voice-packages-')).resolve()
source = fixture / 'source'
packages = ('ai-podcast', 'toni-voice', 'brian-voice', 'broncin-style-writer')
private_files = ('runtime.json', 'voice.json', 'assets/voice.pt', 'assets/private.md',
                 'references/style-profile.md', 'references/evidence.md')
for name in packages:
    shutil.copytree(repo / 'skills' / name, source / name)
    # Ignored local files in a source checkout must not overwrite an enrollment.
    for relative in private_files:
        path = source / name / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b'wrong source private data')


def seed(label):
    target = fixture / label
    for name in packages:
        folder = target / name
        (folder / 'assets').mkdir(parents=True)
        (folder / 'scripts').mkdir()
        for relative in private_files:
            (folder / relative).parent.mkdir(parents=True, exist_ok=True)
            (folder / relative).write_bytes(b'private local sentinel\x00\xff')
        (folder / 'SKILL.md').write_text('previous skill', encoding='utf-8')
        (folder / 'scripts' / 'synthesize.py').write_text('previous script', encoding='utf-8')
    return target


def check(target):
    for name in packages:
        folder = target / name
        for relative in private_files:
            assert (folder / relative).read_bytes() == b'private local sentinel\x00\xff', relative
        assert (folder / 'SKILL.md').read_bytes() == (source / name / 'SKILL.md').read_bytes()
        if (source / name / 'scripts/synthesize.py').exists():
            assert (folder / 'scripts/synthesize.py').read_bytes() == (source / name / 'scripts/synthesize.py').read_bytes()
        assert (folder / 'SKILL.md.lotus.bak').read_text(encoding='utf-8') == 'previous skill'


passed = []
pwsh = shutil.which('pwsh')
if pwsh:
    harness = fixture / 'test.ps1'
    harness.write_text('''param($Installer, $SourceRoot, $TargetRoot)
$ErrorActionPreference = 'Stop'
$tokens = $null; $parseErrors = $null
$ast = [System.Management.Automation.Language.Parser]::ParseFile($Installer, [ref]$tokens, [ref]$parseErrors)
if ($parseErrors.Count) { throw 'Installer parse failed' }
foreach ($name in @('Test-SkillExcluded','Copy-LotusSkillPackages')) {
  $fn = $ast.Find({param($node) $node -is [System.Management.Automation.Language.FunctionDefinitionAst] -and $node.Name -eq $name}, $true)
  . ([scriptblock]::Create($fn.Extent.Text))
}
$SkillsDir = $SourceRoot
Copy-LotusSkillPackages -TargetDir $TargetRoot
''', encoding='utf-8')
    target = seed('powershell-target')
    subprocess.run([pwsh, '-NoProfile', '-File', str(harness), str(repo / 'install.ps1'), str(source), str(target)], check=True)
    check(target)
    subprocess.run([pwsh, '-NoProfile', '-File', str(harness), str(repo / 'install.ps1'), str(source), str(target)], check=True)
    check(target)
    passed.append('PowerShell real copy function')

bash = shutil.which('bash')
if os.name == 'nt' and shutil.which('git'):
    git_bash = Path(shutil.which('git')).resolve().parents[1] / 'bin' / 'bash.exe'
    if git_bash.is_file():
        bash = str(git_bash)
if bash:
    text = (repo / 'install.sh').read_text(encoding='utf-8')
    def extract(name):
        start = text.index(name + '() {')
        end = text.index('\n}\n', start) + 3
        return text[start:end]
    harness = fixture / 'test.sh'
    harness.write_text('set -e\n' + extract('is_skill_excluded') + '\n' + extract('copy_lotus_skill_packages') +
                       '\nSKILLS_DIR="$1"\ncopy_lotus_skill_packages "$2"\n', encoding='utf-8', newline='\n')
    target = seed('bash-target')
    subprocess.run([bash, harness.as_posix(), source.as_posix(), target.as_posix()], check=True)
    check(target)
    subprocess.run([bash, harness.as_posix(), source.as_posix(), target.as_posix()], check=True)
    check(target)
    passed.append('Bash real copy function (not proof of Mac audio runtime)')
if not passed:
    raise RuntimeError('Neither PowerShell nor Bash is available for installer tests.')
print('PASS: ' + '; '.join(passed))
print('Fixture retained at ' + str(fixture))
