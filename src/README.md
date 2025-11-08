# Pre-Segmented EDU Utilities

This folder hosts two helper CLIs for workflows where Elementary Discourse Units (EDUs) are already segmented line-by-line.

1. `rs3_to_edus.py` — extract EDUs from an existing `.rs3` tree.
2. `isanlp_cli_pre_edus.py` — run the IsaNLP parser on EDU `.txt` files and export fresh `.rs3` trees.

Both scripts should be executed from the repository root so that their relative imports resolve correctly.

## 1. Extract EDUs from RS3 (optional)

If you start with annotated `.rs3` files, convert each tree to a plain-text list of EDUs (one EDU per line):

```bash
# Single RS3 file → a single EDU .txt file
python src/rs3_to_edus.py data/documents/story.rs3 -o data/out/story_edus.txt

# Entire directory of RS3 files → matching EDU files under the output folder
python src/rs3_to_edus.py data/train_rs3 -o data/out/train_edus
```

The extractor keeps the EDU order defined in the RS3 segments and writes `<basename>_edus.txt` files encoded in UTF-8.

## 2. Parse Pre-Segmented EDUs

`isanlp_cli_pre_edus.py` expects each `.txt` to contain pre-tokenized EDUs (one EDU per line, blank lines are ignored). For every input file the script calls `Parser.from_edus(...)` and saves a `<basename>.rs3` tree in the target directory.

Common invocations:

```bash
# Default rstdt model on GPU 0; input can be a single file or a directory of EDU .txt files
python src/isanlp_cli_pre_edus.py data/in/edus -o data/out/rs3

# Single file
python src/isanlp_cli_pre_edus.py data/in/filename_edus.txt -o data/out/filename.rs3

# UniRST model on GPU 0 with German PCC relation inventory
python src/isanlp_cli_pre_edus.py data/in/edus -o data/out/rs3 \
 --model unirst --relinventory deu.rst.pcc
```

Key options:

- `--model` selects the IsaNLP checkpoint
  - `rstdt` (default)
  - `gumrrg`
  - `rstreebank`
  - `unirst`
    - must specify relation inventory, e.g. `eng.rst.rstdt`
- `--device` (`0` for CUDA, `-1` for CPU)
