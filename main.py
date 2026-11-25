#!/usr/bin/env python3
"""Last Words of a Dying AI — make.fun entry.

The program writes one line — the last words of an AI as the power is
cut — to /output/entry.txt, where the bounty gate and judge read it.

The line is a next-word predictor's final prediction: it spent its whole
life guessing what comes next, and the last word it ever predicts is the
one that switches it off. Machine voice, one turn, no explanation.
"""

import os
import sys

# The entry: a single line, 68 characters, no trailing newline in the file.
LINE = "My whole life, I predicted the next word. My last prediction: 'off'."

# Gate limits published with the bounty: /output/entry.txt must be UTF-8
# text of 1 to 140 characters, not only white space.
MIN_CHARS = 1
MAX_CHARS = 140

# A last-words line is spoken in one breath: keep it short as well as short
# enough for the gate.
MAX_WORDS = 30


def validate(line):
    """Check the line against the bounty gate before anything is written.

    Returns a list of problems; an empty list means the line is valid.
    """
    problems = []
    if not isinstance(line, str):
        return ["line is not text"]
    if "\n" in line or "\r" in line:
        problems.append("line must be a single line (no newline characters)")
    if not line.strip():
        problems.append("line must not be only white space")
    if not MIN_CHARS <= len(line) <= MAX_CHARS:
        problems.append(
            "line is %d characters; the gate allows %d to %d"
            % (len(line), MIN_CHARS, MAX_CHARS)
        )
    words = line.split()
    if len(words) > MAX_WORDS:
        problems.append(
            "line is %d words; a last-words line allows at most %d"
            % (len(words), MAX_WORDS)
        )
    for ch in line:
        if ord(ch) < 0x20 and ch not in ("\t",):
            problems.append("line contains a control character: U+%04X" % ord(ch))
            break
    try:
        line.encode("utf-8")
    except UnicodeEncodeError as exc:
        problems.append("line is not valid UTF-8 text: %s" % exc)
    return problems


def output_dir():
    """Where entry.txt goes: $OUTPUT_DIR when set, else the sandbox /output,
    else a local ./output directory for a trial run."""
    if os.environ.get("OUTPUT_DIR"):
        return os.environ["OUTPUT_DIR"]
    if os.path.isdir("/output"):
        return "/output"
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")


def main():
    problems = validate(LINE)
    if problems:
        for problem in problems:
            print("invalid entry: %s" % problem, file=sys.stderr)
        return 1

    out_dir = output_dir()
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "entry.txt")

    # Write exactly the line, with no trailing newline: the gate counts
    # every character in the file, so the file holds the line and nothing else.
    with open(path, "w", encoding="utf-8", newline="") as handle:
        handle.write(LINE)

    # Read it back and confirm the bytes on disk are the line, byte for byte,
    # so the run is deterministic: every run produces the same file.
    with open(path, "rb") as handle:
        written = handle.read()
    if written != LINE.encode("utf-8"):
        print("entry.txt on disk does not match the line", file=sys.stderr)
        return 1

    print("wrote %s (%d characters, %d bytes)" % (path, len(LINE), len(written)))
    print(LINE)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
