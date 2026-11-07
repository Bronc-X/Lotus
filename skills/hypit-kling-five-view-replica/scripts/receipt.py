from __future__ import annotations
import argparse
import datetime
from pathlib import Path
from common import job_directory, read_json, write_json

parser = argparse.ArgumentParser(description='Record an actually observed human-service state; does not submit generation')
parser.add_argument('--project', required=True, type=Path)
parser.add_argument('--job', required=True)
parser.add_argument('--status', choices=['submitted','running','failed'], required=True)
parser.add_argument('--model', required=True)
parser.add_argument('--task-id')
parser.add_argument('--creation-resource-id')
parser.add_argument('--approved-credits', type=float)
parser.add_argument('--message')
args = parser.parse_args()
directory = job_directory(args.project.expanduser().resolve(), args.job)
path = directory/'receipt.json'
record = read_json(path) if path.exists() else {}
if record.get('status') == 'succeeded':
    raise ValueError('Do not regress a completed receipt')
record.update({'format':'hypit.kling-ui-receipt@1','jobId':args.job,'status':args.status,
               'service':'Kling browser UI','model':args.model,'taskId':record.get('taskId'),
               'observedAt':datetime.datetime.now(datetime.timezone.utc).isoformat()})
for attribute, field in [('task_id','taskId'),('creation_resource_id','creationResourceId'),
                         ('approved_credits','approvedCredits'),('message','message')]:
    if getattr(args, attribute) is not None:
        record[field] = getattr(args, attribute)
write_json(path, record)
print(str(path))
