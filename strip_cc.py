#!/usr/bin/env python3
"""Strip CC labels in [] / () (and full-width ［］ / （）) from SRT files."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

BRACKET_RE = re.compile(r"\[[^\]]*\]|\([^)]*\)|［[^］]*］|（[^）]*）")
TIMESTAMP_RE = re.compile(
    r"^\d{2}:\d{2}:\d{2}[,.]\d{3}\s*-->\s*\d{2}:\d{2}:\d{2}[,.]\d{3}"
)


def clean_text_line(line: str) -> str | None:
    cleaned = BRACKET_RE.sub("", line).strip()
    return cleaned or None


def parse_cues(text: str) -> list[tuple[str, list[str]]]:
    """Return list of (timestamp_line, text_lines) for each cue."""
    cues: list[tuple[str, list[str]]] = []
    blocks = re.split(r"\n\s*\n", text.strip("\n"))
    for block in blocks:
        lines = [line.rstrip("\r") for line in block.split("\n") if line.strip() != ""]
        if len(lines) < 2:
            continue
        ts_idx = next((i for i, line in enumerate(lines) if TIMESTAMP_RE.match(line)), None)
        if ts_idx is None:
            continue
        timestamp = lines[ts_idx]
        text_lines = lines[ts_idx + 1 :]
        cues.append((timestamp, text_lines))
    return cues


def strip_cues(cues: list[tuple[str, list[str]]]) -> list[tuple[str, list[str]]]:
    kept: list[tuple[str, list[str]]] = []
    for timestamp, text_lines in cues:
        cleaned = [line for raw in text_lines if (line := clean_text_line(raw)) is not None]
        if cleaned:
            kept.append((timestamp, cleaned))
    return kept


def format_srt(cues: list[tuple[str, list[str]]]) -> str:
    parts: list[str] = []
    for index, (timestamp, text_lines) in enumerate(cues, start=1):
        parts.append(str(index))
        parts.append(timestamp)
        parts.extend(text_lines)
        parts.append("")
    return "\n".join(parts)


def strip_srt(text: str) -> str:
    if text.startswith("\ufeff"):
        text = text[1:]
    return format_srt(strip_cues(parse_cues(text)))


def output_path_for(input_path: Path) -> Path:
    return input_path.with_name(f"{input_path.stem}.clean{input_path.suffix}")


def process_file(input_path: Path, *, force: bool) -> Path:
    out = output_path_for(input_path)
    if out.exists() and not force:
        raise FileExistsError(f"refusing to overwrite {out} (use --force)")
    raw = input_path.read_text(encoding="utf-8")
    out.write_text(strip_srt(raw), encoding="utf-8", newline="\n")
    return out


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("inputs", nargs="+", type=Path, help="SRT file(s) to clean")
    parser.add_argument(
        "--force",
        action="store_true",
        help="overwrite existing .clean.srt outputs",
    )
    args = parser.parse_args(argv)

    exit_code = 0
    for path in args.inputs:
        try:
            out = process_file(path, force=args.force)
        except (OSError, FileExistsError, UnicodeError) as exc:
            print(f"{path}: {exc}", file=sys.stderr)
            exit_code = 1
            continue
        print(f"{path} -> {out}")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
