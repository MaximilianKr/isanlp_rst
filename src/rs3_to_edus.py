#!/usr/bin/env python3

import re
import sys
import argparse
from pathlib import Path
import xml.etree.ElementTree as ET


def normalize_ws(s: str) -> str:
    return re.sub(r"\s+", " ", s or "").strip()


def rs3_to_edus(rs3_path: Path) -> list[str]:
    root = ET.parse(rs3_path).getroot()
    segs = []
    for seg in root.findall(".//segment"):
        sid = seg.get("id")
        if sid is None:
            continue
        try:
            sid = int(sid)
        except ValueError:
            continue
        segs.append((sid, normalize_ws(seg.text)))
    segs.sort(key=lambda x: x[0])
    return [t for _, t in segs]


def parse_args():
    ap = argparse.ArgumentParser(
        description="Extract EDUs from single rs3 file or all files in a dir."
    )
    ap.add_argument(
        "input", 
        help="Path to input .rs3 OR a directory containing .rs3 files."
    )
    ap.add_argument(
        "-o", "--out", required=True,
        help="Output folder. Each input becomes <name>_edus.txt here."
    )
    return ap.parse_args()


def write_edus(in_file: Path, out_dir: Path):
    edus = rs3_to_edus(in_file)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / (in_file.stem + "_edus.txt")
    out_file.write_text("\n".join(edus) + "\n", encoding="utf-8")
    print(f"Wrote {out_file} ({len(edus)} EDUs)")


def main():
    args = parse_args()
    inp = Path(args.input)
    out_dir = Path(args.out)

    if not inp.exists():
        print(f"Input path not found: {inp}", file=sys.stderr)
        return 1

    if inp.is_file():
        if inp.suffix.lower() != ".rs3":
            print("Input file must have .rs3 extension.", file=sys.stderr)
            return 1
        write_edus(inp, out_dir)
        return 0

    if not inp.is_dir():
        print("Input must be a .rs3 file or a directory.", file=sys.stderr)
        return 1

    # directory mode
    files = sorted(
        p for p in inp.iterdir() if p.is_file() and p.suffix.lower() == ".rs3"
    )
    if not files:
        print("No .rs3 files found in the directory.", file=sys.stderr)
        return 1

    for f in files:
        try:
            write_edus(f, out_dir)
        except Exception as e:
            print(f"[ERROR] {f}: {e}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
