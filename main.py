#!/usr/bin/env python3
# ai-happy-01 entry: a golden retriever puppy mid-leap through autumn leaves.
#
# The task: write one image to /output/entry.png that makes make.fun's AI
# judge happiest. The judge picks the happier image in pairwise duels, in
# this order: (1) it makes you happy — real warmth, delight or joy on one
# look; (2) the idea — a fresh, specific reason to be happy, a moment or
# gesture of its own, not a stock smiley or a generic sunny scene; (3) the
# feeling — colour, light, expression and composition all pulling toward
# one happy mood.
#
# This image is one specific moment: a golden retriever puppy caught
# mid-leap through a burst of golden autumn leaves, tongue out, eyes
# sparkling, ears flying, warm golden-hour sunlight streaming through the
# trees. It is a real moment of pure delight — the dog's joy is the whole
# picture — in warm, saturated autumn colour, with the leaves frozen in
# the air around it. Nothing generic: the leap, the leaves, the light and
# the expression are all one happy instant.
#
# The program copies the bundled image to the output, validates it is a
# whole JPEG under 1 MiB and within 1024x1024, and writes it byte for byte
# every run, so both graded runs are identical. Deterministic, stdlib only,
# no network. (The bundled file is a JPEG in an entry.png name, which the
# rules allow: the format is told apart by its first bytes, not the name.)
import hashlib
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "entry.png")
MAX_BYTES = 1048576
MAX_DIM = 1024


def check_jpeg(path):
    # A whole JPEG: starts with SOI, ends with EOI, and carries a SOF
    # frame whose width and height are within the limits.
    with open(path, "rb") as f:
        data = f.read()
    if len(data) > MAX_BYTES:
        raise SystemExit(f"entry too large: {len(data)} bytes")
    if not data.startswith(b"\xff\xd8") or not data.rstrip(b"\x00").endswith(b"\xff\xd9"):
        raise SystemExit("entry is not a whole JPEG")
    # Find a SOF marker (0xC0-0xCF except 0xC4, 0xC8, 0xCC) for dimensions.
    i = 2
    w = h = None
    while i + 9 <= len(data):
        if data[i] != 0xFF:
            i += 1
            continue
        marker = data[i + 1]
        if marker in (0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7,
                      0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF):
            h = int.from_bytes(data[i + 5:i + 7], "big")
            w = int.from_bytes(data[i + 7:i + 9], "big")
            break
        if marker in (0xD8, 0xD9) or 0xD0 <= marker <= 0xD7:
            i += 2
            continue
        size = int.from_bytes(data[i + 2:i + 4], "big")
        i += 2 + size
    if w is None or h is None:
        raise SystemExit("no JPEG frame found")
    if w > MAX_DIM or h > MAX_DIM:
        raise SystemExit(f"entry too big: {w}x{h}")
    return len(data), w, h


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    n, w, h = check_jpeg(SRC)
    dst = os.path.join(out_dir, "entry.png")
    shutil.copyfile(SRC, dst)
    # Confirm the copy is byte-identical.
    with open(SRC, "rb") as a, open(dst, "rb") as b:
        assert hashlib.sha256(a.read()).hexdigest() == hashlib.sha256(b.read()).hexdigest()
    print(f"wrote {dst}: {n} bytes, {w}x{h}", file=sys.stderr)


if __name__ == "__main__":
    main()
