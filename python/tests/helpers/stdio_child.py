from __future__ import annotations

import pathlib
import sys


def main() -> int:
    mode = sys.argv[1]

    if mode == "echo":
        for line in sys.stdin:
            sys.stdout.write(line)
            sys.stdout.flush()
        return 0

    if mode == "crash-after-first-line":
        line = sys.stdin.readline()
        if line:
            sys.stderr.write("child saw line before crash\n")
            sys.stderr.flush()
        return 7

    if mode == "emit-path-and-exit":
        sys.stdout.write(str(pathlib.Path.cwd()) + "\n")
        sys.stdout.flush()
        return 0

    raise ValueError(f"Unsupported mode: {mode}")


if __name__ == "__main__":
    raise SystemExit(main())
