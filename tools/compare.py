import subprocess, sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
# OPPONENTS = ["greedy_agent", "random_agent", "tools/old_student_agent.py"]
OPPONENTS = ["random_agent"]

def test(a, seed=1):
    cwd = [sys.executable, "simulator.py", "--player_1", "student_agent", "--player_2", a, "--autoplay", "--autoplay_runs", "200", "--strict", "--seed", str(seed)]
    result = subprocess.run(cwd, capture_output=True, text=True, cwd=ROOT)

    print(f"student_agent vs {a}")
    print(f"Return code: {result.returncode}")
    print(f"Stderr: {result.stderr}")
    print(f"Stdout: {result.stdout}")


def main():
    for a in OPPONENTS:
        test(a)


if __name__ == "__main__":
    main()