# srt-strip-cc

Strip closed-caption labels from SRT subtitle files.

Removes text inside ASCII and full-width brackets/parentheses:

- `[...]` / `(...)`
- `［...］` / `（...）`

Speaker tags and sound effects like `［女性２］` or `（せき払い）` are stripped. If a cue’s text is only labels, the whole cue is deleted and survivors are renumbered.

## Usage

```bash
python strip_cc.py path/to/file.srt
# writes path/to/file.clean.srt
```

```bash
python strip_cc.py a.srt b.srt --force   # overwrite existing .clean.srt
```

## Example

Before:

```srt
8
00:00:38,998 --> 00:00:42,376
［女性２］テレビ画面に女の人が映って
なんか手挙げてたりするとか

15
00:01:13,282 --> 00:01:14,408
（せき払い）
```

After:

```srt
8
00:00:38,998 --> 00:00:42,376
テレビ画面に女の人が映って
なんか手挙げてたりするとか
```

(Cue 15 is removed; later cues are renumbered.)

## Tests

```bash
python -m unittest discover -s tests -v
```

Requires Python 3.10+ (stdlib only).
