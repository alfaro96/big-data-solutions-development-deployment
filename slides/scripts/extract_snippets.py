#!/usr/bin/env python3
"""Extract code snippets for the slides from the public project in ``code/``.

The manifest ``slides/snippets.yaml`` declares what to extract, so the public
code never carries slide-related markers. Output goes to ``slides/snippets/``
together with a lock file recording the hash of every snippet and the last
commit that touched ``code/``.

Usage:
    python slides/scripts/extract_snippets.py           # regenerate snippets
    python slides/scripts/extract_snippets.py --check   # verify, exit 1 on drift
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
CODE_DIR = REPO_ROOT / "code"
MANIFEST_PATH = REPO_ROOT / "slides" / "snippets.yaml"
OUTPUT_DIR = REPO_ROOT / "slides" / "snippets"
LOCK_PATH = OUTPUT_DIR / ".lock.json"


class SnippetError(Exception):
    """Raised when a snippet cannot be extracted as declared."""


def _by_symbol(source: str, symbol: str) -> list[str]:
    lines = source.splitlines()
    for node in ast.walk(ast.parse(source)):
        is_definition = isinstance(
            node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)
        )
        if is_definition and node.name == symbol:
            first = min([node.lineno] + [d.lineno for d in node.decorator_list])
            return lines[first - 1 : node.end_lineno]
    raise SnippetError(f"symbol '{symbol}' not found")


def _by_anchors(source: str, start: str, end: str) -> list[str]:
    lines = source.splitlines()
    begin = next((i for i, line in enumerate(lines) if re.search(start, line)), None)
    if begin is None:
        raise SnippetError(f"start anchor '{start}' not found")
    finish = next(
        (i for i in range(begin, len(lines)) if re.search(end, lines[i])), None
    )
    if finish is None:
        raise SnippetError(f"end anchor '{end}' not found after start")
    return lines[begin : finish + 1]


def _by_lines(source: str, bounds: list[int]) -> list[str]:
    first, last = bounds
    lines = source.splitlines()
    if not 1 <= first <= last <= len(lines):
        raise SnippetError(f"line range {bounds} outside file ({len(lines)} lines)")
    return lines[first - 1 : last]


def _dedent(lines: list[str]) -> list[str]:
    indents = [len(line) - len(line.lstrip()) for line in lines if line.strip()]
    margin = min(indents, default=0)
    return [line[margin:] for line in lines]


def extract(entry: dict) -> str:
    """Return the text of one manifest entry."""
    path = CODE_DIR / entry["file"]
    if not path.is_file():
        raise SnippetError(f"file '{entry['file']}' not found in code/")
    source = path.read_text(encoding="utf-8")
    if "symbol" in entry:
        selected = _by_symbol(source, entry["symbol"])
    elif "start" in entry and "end" in entry:
        selected = _by_anchors(source, entry["start"], entry["end"])
    elif "lines" in entry:
        selected = _by_lines(source, entry["lines"])
    else:
        raise SnippetError("entry needs 'symbol', 'start'+'end' or 'lines'")
    return "\n".join(_dedent(selected)) + "\n"


def _code_commit() -> str:
    result = subprocess.run(
        ["git", "-C", str(REPO_ROOT), "log", "-1", "--format=%H", "--", "code"],
        capture_output=True,
        text=True,
        check=False,
    )
    return result.stdout.strip() if result.returncode == 0 else "unknown"


def build() -> tuple[dict[str, str], dict[str, dict]]:
    """Extract every snippet. Returns (id -> text, id -> metadata)."""
    manifest = yaml.safe_load(MANIFEST_PATH.read_text(encoding="utf-8")) or {}
    entries = manifest.get("snippets") or []
    texts: dict[str, str] = {}
    meta: dict[str, dict] = {}
    errors: list[str] = []
    for entry in entries:
        snippet_id = entry.get("id")
        try:
            if not snippet_id or snippet_id in texts:
                raise SnippetError("missing or duplicated 'id'")
            text = extract(entry)
        except SnippetError as error:
            errors.append(f"[{snippet_id}] {error}")
            continue
        suffix = Path(entry["file"]).suffix or ".txt"
        texts[snippet_id] = text
        meta[snippet_id] = {
            "file": entry["file"],
            "output": f"{snippet_id}{suffix}",
            "sha256": hashlib.sha256(text.encode()).hexdigest(),
        }
    if errors:
        print("Extraction errors:", *errors, sep="\n  ", file=sys.stderr)
        sys.exit(2)
    return texts, meta


def write(texts: dict[str, str], meta: dict[str, dict]) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for old in OUTPUT_DIR.iterdir():
        if old.name not in (".gitkeep", ".lock.json"):
            old.unlink()
    for snippet_id, text in texts.items():
        (OUTPUT_DIR / meta[snippet_id]["output"]).write_text(text, encoding="utf-8")
    lock = {"code_commit": _code_commit(), "snippets": meta}
    LOCK_PATH.write_text(json.dumps(lock, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {len(texts)} snippet(s) from code/@{lock['code_commit'][:8]}")


def check(texts: dict[str, str], meta: dict[str, dict]) -> int:
    problems: list[str] = []
    lock = json.loads(LOCK_PATH.read_text()) if LOCK_PATH.exists() else {}
    locked = lock.get("snippets", {})
    for snippet_id, info in meta.items():
        on_disk = OUTPUT_DIR / info["output"]
        if snippet_id not in locked:
            problems.append(f"[{snippet_id}] declared but never extracted")
        elif not on_disk.exists() or on_disk.read_text() != texts[snippet_id]:
            problems.append(f"[{snippet_id}] out of sync with code/{info['file']}")
    for snippet_id in set(locked) - set(meta):
        problems.append(f"[{snippet_id}] in lock but removed from the manifest")
    if problems:
        print("Snippets out of sync:", *problems, sep="\n  ")
        print("Run: python slides/scripts/extract_snippets.py")
        return 1
    print(f"{len(meta)} snippet(s) in sync.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--check", action="store_true", help="verify only")
    args = parser.parse_args()
    texts, meta = build()
    if args.check:
        return check(texts, meta)
    write(texts, meta)
    return 0


if __name__ == "__main__":
    sys.exit(main())
