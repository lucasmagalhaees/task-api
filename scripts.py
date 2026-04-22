import subprocess
import sys


def e2e():
    result = subprocess.run(["pytest", "tests/tasks/test_e2e.py", "-v"])
    sys.exit(result.returncode)


def up():
    build = subprocess.run(["docker", "compose", "build", "--no-cache"])
    if build.returncode != 0:
        sys.exit(build.returncode)
    result = subprocess.run(["docker", "compose", "up", "-d"])
    sys.exit(result.returncode)
