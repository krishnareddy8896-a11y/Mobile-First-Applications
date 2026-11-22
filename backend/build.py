import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent

for command in (
    [sys.executable, "manage.py", "migrate", "--noinput"],
    [sys.executable, "manage.py", "import_data"],
):
    subprocess.run(command, cwd=ROOT, check=True)
