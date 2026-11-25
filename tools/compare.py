import subprocess, sys
from pathlib import Path
import argparse
from datetime import datetime


p = argparse.ArgumentParser(description = "Compare sutdent_agent against opponents")
p.add_argument("opponents", nargs = "*", default = ["greedy_agent"])
p.add_argument("pairs", type = int, default = 50)

args = p.parse_args()

ROOT = Path(__file__).resolve().parent.parent
LOG_PATH = ROOT/"results"/"log.md"
OPPONENTS = args.opponents
SEED = 1

# log results with timestamp, also logs returncode and stderr if needed
def log(opp, returncode, stderr, stdout, pairs=args.pairs):
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    with open(LOG_PATH, "a") as f:
        f.write(f"{stamp}")
        f.write(f"student_agent vs {opp} on {2*pairs} games on seed {SEED}")
        f.write("\n")
        f.write(stdout)
        if returncode != 0:
            f.write(returncode)
            f.write(stderr)
        f.write("\n\n")


# execute simulator.py for student_agent with passed arguments, same seed everytime to compare logs
def test(opp, pairs=args.pairs, seed=SEED):
    cwd = [sys.executable, "simulator.py", "--player_1", "student_agent", "--player_2", opp, "--autoplay", "--autoplay_runs", str(2*pairs), "--strict", "--seed", str(seed)]
    result = subprocess.run(cwd, capture_output=True, text=True, cwd=ROOT)

    print(f"student_agent vs {opp}")
    print(f"Return code: {result.returncode}")
    print(f"Stderr: {result.stderr}")
    print(f"Stdout: {result.stdout}")

    log(opp, result.returncode, result.stderr, result.stdout)


def main():
    for opp in OPPONENTS:
        test(opp)


if __name__ == "__main__":
    main()