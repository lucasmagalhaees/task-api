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


def load():
    import httpx

    try:
        httpx.get("http://localhost:8001", timeout=2)
    except (httpx.ConnectError, httpx.ConnectTimeout):
        print("Aplicação não está rodando em localhost:8001. Execute `uv run python -m cli up` primeiro.")
        sys.exit(1)

    args, extra = _parse_load_args()
    result = subprocess.run([
        "locust",
        "-f", "tests/load/locustfile.py",
        "--headless",
        "--host", "http://localhost:8001",
        "--users", args.users,
        "--spawn-rate", args.spawn_rate,
        "--run-time", args.time,
        "--exit-code-on-error", "1",
        *extra,
    ])

    if result.returncode == 0:
        print("\n✅ Load test PASSED — no request failures.")
    else:
        print("\n❌ Load test FAILED — one or more requests returned errors.")

    sys.exit(result.returncode)


def _parse_load_args():
    import argparse

    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--users", default="20")
    parser.add_argument("--spawn-rate", default="5")
    parser.add_argument("--time", default="30s")
    return parser.parse_known_args(sys.argv[2:])


_COMMANDS = {"e2e": e2e, "up": up, "load": load}

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else None
    if cmd not in _COMMANDS:
        print(f"Uso: uv run python -m cli [{' | '.join(_COMMANDS)}]")
        sys.exit(1)
    _COMMANDS[cmd]()
