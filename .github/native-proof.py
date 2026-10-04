import hashlib
import json
import pathlib
import subprocess
import sys

root = pathlib.Path(sys.argv[1]).resolve()
out = pathlib.Path(sys.argv[2])
def git(*args):
    return subprocess.check_output(['git', '-C', str(root), *args])
entries = []
for record in git('ls-files', '-s', '-z').decode().split('\0'):
    if not record:
        continue
    info, name = record.split('\t', 1)
    mode, blob, stage = info.split()
    data = (root / name).read_bytes()
    entries.append({'path': name, 'mode': mode, 'blob': blob,
                    'sha256': hashlib.sha256(data).hexdigest(), 'bytes': len(data)})
modified = git('diff', '--name-only', 'HEAD').decode().splitlines()
proof = {'head': git('rev-parse', 'HEAD').decode().strip(),
         'modified': modified, 'tracked': entries}
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(proof, indent=2) + '\n')
if modified:
    raise SystemExit('Tracked subject source changed: ' + repr(modified))
