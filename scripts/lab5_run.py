"""Run a real command once and preserve its output, exit code and source hashes."""
import datetime
import hashlib
import json
from pathlib import Path
import subprocess
import sys

root = Path(__file__).resolve().parents[1]
output = root / sys.argv[1]
if output.exists():
    raise SystemExit(f'Refusing to overwrite evidence: {output}')
command = sys.argv[2:]
hashes = {}
for folder in ('salon', 'tests/lab5', 'spec'):
    for path in sorted((root / folder).rglob('*')):
        if path.is_file() and '__pycache__' not in str(path):
            hashes[str(path.relative_to(root))] = hashlib.sha256(path.read_bytes()).hexdigest()
meta = dict(time=datetime.datetime.now(datetime.timezone.utc).isoformat(), cwd=str(root),
            command=command, head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip(),
            python=sys.version, source_sha256=hashes)
result = subprocess.run(command, cwd=root, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
output.parent.mkdir(parents=True, exist_ok=True)
output.write_text(json.dumps(meta, ensure_ascii=False, indent=2) + '\n\n' + result.stdout + f'\nEXIT_CODE={result.returncode}\n')
print(result.stdout)
print(f'EXIT_CODE={result.returncode}; evidence={output.relative_to(root)}')
sys.exit(result.returncode)
