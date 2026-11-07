from __future__ import annotations
import argparse
import datetime
import os
from pathlib import Path
import shutil
import uuid
from common import digest, job_directory, read_json, write_json

parser = argparse.ArgumentParser(description='Collect an existing MP4 into the same local job, preserving its submission evidence')
parser.add_argument('--project', required=True, type=Path)
parser.add_argument('--job', required=True)
parser.add_argument('--video', required=True, type=Path)
parser.add_argument('--model', required=True)
parser.add_argument('--provenance', choices=['browser-download','user-supplied-original','user-supplied-remux','local-fixture'], required=True)
parser.add_argument('--task-id')
parser.add_argument('--creation-resource-id')
args = parser.parse_args()
directory = job_directory(args.project.expanduser().resolve(), args.job)
video = args.video.expanduser().resolve(strict=True)
with video.open('rb') as stream:
    header = stream.read(16)
if len(header) < 16 or header[4:8] != b'ftyp':
    raise ValueError('Expected an actual MP4 container; renaming a file is not conversion')
checksum = digest(video)
receipt_path = directory/'receipt.json'
record = read_json(receipt_path) if receipt_path.exists() else {}
if record and record.get('jobId') != args.job:
    raise ValueError('Receipt belongs to another request')
if record.get('status') == 'succeeded' and record.get('sha256') != checksum:
    raise ValueError('A different completed result already exists; preserve it instead of overwriting')
if record.get('model') and record['model'] != args.model:
    raise ValueError('Actual model label differs from the recorded submission')
target = directory/'result.mp4'
if target.exists() and digest(target) != checksum:
    raise ValueError('Existing result.mp4 differs; select and reconcile the actual result before collecting')
if not target.exists():
    temporary = directory/('result.'+uuid.uuid4().hex+'.tmp')
    shutil.copy2(video, temporary)
    os.replace(temporary, target)
record.update({'format':'hypit.kling-ui-receipt@1','jobId':args.job,'status':'succeeded',
               'service':'Kling browser UI','model':args.model,'taskId':record.get('taskId'),
               'output':'result.mp4','sha256':checksum,'bytes':target.stat().st_size,
               'fileProvenance':args.provenance,'platformOriginalBytesVerified':False,
               'receivedAt':datetime.datetime.now(datetime.timezone.utc).isoformat()})
if args.task_id is not None:
    record['taskId'] = args.task_id
if args.creation_resource_id is not None:
    record['creationResourceId'] = args.creation_resource_id
write_json(receipt_path, record)
print(str(receipt_path))
