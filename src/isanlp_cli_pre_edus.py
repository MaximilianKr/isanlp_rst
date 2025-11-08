#!/usr/bin/env python3

import  sys
import argparse
from pathlib import Path
from isanlp_rst.parser import Parser  # API per README


def read_edus(p: Path) -> list[str]:
    """Return all non-empty EDUs (one per line) from the file."""
    edus = []
    for line in p.read_text(encoding="utf-8").splitlines():
        edu = line.strip()
        if edu:
            edus.append(edu)
    return edus


def parse_args():
    ap = argparse.ArgumentParser(
        description=(
            "Run IsaNLP RST on pre-segmented EDU files (one EDU per line) "
            "and save RS3."
        )
    )
    ap.add_argument(
        "input",
        help="Path to input .txt file (UTF-8) or directory of .txt files."
    )
    ap.add_argument(
        "-o", "--out", required=True, 
        help="Output folder. Each input file becomes <name>.rs3 in the folder."
    )
    ap.add_argument(
        "--model", default="rstdt",
        choices=["rstdt", "gumrrg", "rstreebank", "unirst"],
        help="Model tag, as in the README."
    )
    ap.add_argument(
        "--relinventory", default=None,
        help="Only for --model unirst, e.g. deu.rst.pcc or eng.rst.rstdt."
    )
    ap.add_argument(
        "--device", default="0",
        help="CUDA device id. Use -1 for CPU, 0 for first GPU."
    )
    return ap.parse_args()


def build_parser(args) -> Parser:
    kwargs = dict(
        hf_model_name="tchewik/isanlp_rst_v3",
        hf_model_version=args.model,
        cuda_device=int(args.device),
    )
    if args.model == "unirst" and args.relinventory:
        kwargs["relinventory"] = args.relinventory
    return Parser(**kwargs)


def parse_one(parser: Parser, in_file: Path, out_dir: Path):
    edus = read_edus(in_file)
    if not edus:
        raise ValueError("No non-empty EDUs found in the file.")
    res = parser.from_edus(edus)
    tree = res["rst"][0]
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / (in_file.stem + ".rs3")
    tree.to_rs3(str(out_file))
    print(f"Wrote {out_file}")


def main():
    args = parse_args()
    inp = Path(args.input)
    out_dir = Path(args.out)

    if not inp.exists():
        print(f"Input path not found: {inp}", file=sys.stderr)
        return 1

    parser = build_parser(args)

    if inp.is_file():
        if inp.suffix.lower() != ".txt":
            print("Input file must have .txt extension.", file=sys.stderr)
            return 1
        parse_one(parser, inp, out_dir)
        return 0

    if not inp.is_dir():
        print("Input must be a .txt file or a directory.", file=sys.stderr)
        return 1

    # Directory mode
    files = sorted(
        p for p in inp.iterdir() if p.is_file() and p.suffix.lower() == ".txt"
    )
    if not files:
        print("No .txt files found in the directory.", file=sys.stderr)
        return 1

    for f in files:
        try:
            parse_one(parser, f, out_dir)
        except Exception as e:
            print(f"[ERROR] {f}: {e}", file=sys.stderr)

    return 0

if __name__ == "__main__":
    sys.exit(main())
