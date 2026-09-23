"""Freeze/verify a local release candidate; never grants approval or performs an upload."""
import argparse
import hashlib
import json
from pathlib import Path


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def create(root, output):
    root, output = root.resolve(), output.resolve()
    if output.exists():
        raise FileExistsError('Use a new version; do not overwrite an approved manifest.')
    if not root.is_dir() or output.parent != root:
        raise ValueError('Manifest must be directly inside an existing release directory.')
    files = []
    for path in sorted(root.rglob('*')):
        if path.is_symlink():
            raise ValueError('Release candidates must contain real files, not symlinks.')
        if path.is_file():
            files.append(dict(path=path.relative_to(output.parent).as_posix(), sha256=sha(path)))
    if not files:
        raise ValueError('Empty release candidate.')
    output.write_text(json.dumps(dict(schema=1, files=files), ensure_ascii=False, indent=2), encoding='utf-8')
    return dict(candidate_sha256=sha(output), status='candidate_pending_authorization')


def verify(manifest, grant=None, platform=None, account=None, action=None):
    manifest = manifest.resolve()
    data = json.loads(manifest.read_text(encoding='utf-8-sig'))
    if not data.get('files'):
        raise ValueError('Empty manifest.')
    listed = {item['path'] for item in data['files']}
    actual = {p.relative_to(manifest.parent).as_posix() for p in manifest.parent.rglob('*')
              if p.is_file() and p != manifest}
    if listed != actual:
        raise ValueError('Release file set changed; build a new candidate manifest.')
    for item in data['files']:
        if (manifest.parent / item['path']).is_symlink():
            raise ValueError('Release file became a symlink.')
        path = (manifest.parent / item['path']).resolve()
        if not path.is_relative_to(manifest.parent) or not path.is_file() or sha(path) != item['sha256']:
            raise ValueError(f'Changed or unsafe candidate file: {item["path"]}')
    if grant:
        g = json.loads(Path(grant).read_text(encoding='utf-8-sig'))
        expected = dict(candidate_sha256=sha(manifest), platform=platform, account=account, action=action)
        if any(not v or g.get(k) != v for k, v in expected.items()) or not g.get('evidence'):
            raise ValueError('Grant does not cover this exact candidate, account, platform and action.')
    return dict(candidate_sha256=sha(manifest), status='hashes_verified', grant_matched=bool(grant))


def main():
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest='command', required=True)
    c = sub.add_parser('create')
    c.add_argument('--root', type=Path, required=True)
    c.add_argument('--output', type=Path, required=True)
    v = sub.add_parser('verify')
    v.add_argument('--manifest', type=Path, required=True)
    for name in ('grant', 'platform', 'account', 'action'):
        v.add_argument('--' + name)
    a = p.parse_args()
    result = create(a.root, a.output) if a.command == 'create' else verify(a.manifest, a.grant, a.platform, a.account, a.action)
    print(json.dumps(result))


if __name__ == '__main__':
    main()
