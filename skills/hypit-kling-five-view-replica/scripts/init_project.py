from __future__ import annotations
import argparse
from pathlib import Path
import shutil
import subprocess
import sys
from xml.sax.saxutils import escape
from common import PORTS, SKILL_ROOT, digest, discover_cli, write_json

def main() -> None:
    parser = argparse.ArgumentParser(description='Initialize a new portable five-photo Hypit/Kling human-service project')
    parser.add_argument('--project', required=True, type=Path)
    parser.add_argument('--hypit-cli')
    parser.add_argument('--node')
    parser.add_argument('--source', required=True, type=Path)
    parser.add_argument('--source-upload', type=Path)
    for port in PORTS:
        parser.add_argument('--' + port, required=True, type=Path)
    parser.add_argument('--subject', default='原视频中需要替换人脸的前景主角')
    parser.add_argument('--preserve', default='原片头部装饰、衣服、身体、场景及其他人物')
    parser.add_argument('--video-tag', default='@视频1')
    parser.add_argument('--image-tags', nargs=5, default=['@图片1','@图片2','@图片3','@图片4','@图片5'])
    parser.add_argument('--prompt-file', type=Path)
    args = parser.parse_args()
    project = args.project.expanduser().resolve()
    if project.exists():
        raise ValueError('Project path already exists; select a new directory')
    source = args.source.expanduser().resolve(strict=True)
    upload = (args.source_upload or source).expanduser().resolve(strict=True)
    photos = {port: getattr(args, port).expanduser().resolve(strict=True) for port in PORTS}
    for video in [source, upload]:
        if video.suffix.lower() not in {'.mp4', '.mov'}:
            raise ValueError('Supply actual MP4/MOV video files; renaming is not conversion')
    if any(path.suffix.lower() not in {'.png', '.jpg', '.jpeg', '.webp'} for path in photos.values()):
        raise ValueError('Identity inputs must be PNG/JPEG/WebP images')
    if len({digest(path) for path in photos.values()}) != 5:
        raise ValueError('Supply five distinct original identity photographs, not the same file five times')
    argv = discover_cli(args.hypit_cli, args.node)
    prompt = args.prompt_file.read_text(encoding='utf-8') if args.prompt_file else (SKILL_ROOT/'assets/prompt-template.txt').read_text(encoding='utf-8')
    values = {'VIDEO': args.video_tag, 'SUBJECT': args.subject, 'PRESERVE': args.preserve,
              **{f'IMAGE{index}': tag for index, tag in enumerate(args.image_tags, 1)}}
    for key, value in values.items():
        prompt = prompt.replace('{{' + key + '}}', value)
    if '{{' in prompt or not prompt.strip():
        raise ValueError('Prompt contains unresolved template fields or is empty')
    shutil.copytree(SKILL_ROOT/'assets/project-template', project)
    (project/'assets').mkdir()
    records = {}
    for port, original in {'source': source, 'sourceUpload': upload, **photos}.items():
        filename = port + original.suffix.lower()
        target = project/'assets'/filename
        shutil.copy2(original, target)
        records[port] = {'file': 'assets/' + filename, 'sha256': digest(target), 'personReference': True}
    write_json(project/'package.json', {'name': 'hypit-portrait-edit', 'version': '1.0.0', 'private': True, 'type': 'module'})
    write_json(project/'.hypit-tools.json', {'argv': argv})
    write_json(project/'project.json', {'format': 'hypit.kling-portrait-project@1', 'inputs': records,
                                       'identityOrder': list(PORTS), 'cloudSubmissionAuthorized': False})
    lines = ['<?svml using="@hypit/markup@1"?>', '<svml>',
             '  <import as="asset" from="@hypit/media@1"/>', '  <import as="text" from="@hypit/text@1"/>',
             '  <import as="kling" from="@portrait/kling-ui@1"/>']
    for port, record in records.items():
        tag = 'Video' if port in {'source', 'sourceUpload'} else 'Image'
        lines.append(f'  <asset:{tag} id="{port}" src="./{escape(record["file"])}"/>')
    lines.append('  <text:Value id="direction">' + escape(prompt.strip()) + '</text:Value>')
    attributes = ' '.join(f'{port}={{{port}}}' for port in records)
    lines += [f'  <kling:FiveViewVideoEdit id="edit" {attributes} prompt={{direction}}/>', '</svml>']
    (project/'main.svml').write_text('\n'.join(lines)+'\n', encoding='utf-8')
    (project/'prompt.txt').write_text(prompt.strip()+'\n', encoding='utf-8')
    (project/'.gitignore').write_text('.hypit/\n.hypit-tools.json\nassets/\nexchange/\noutput/\n', encoding='utf-8')
    for command in [['runtime','use','hypit.runtime.json'], ['check','build.svrun'], ['plan','build.svrun','--runtime','hypit.runtime.json']]:
        subprocess.run(argv + command, cwd=project, check=True)
    print('Prepared local project; no cloud submission: ' + str(project))

if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError, subprocess.CalledProcessError) as error:
        print(str(error), file=sys.stderr)
        raise SystemExit(1)
