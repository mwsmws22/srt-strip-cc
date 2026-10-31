from __future__ import annotations

import unittest
from pathlib import Path

from strip_cc import clean_text_line, output_path_for, process_file, strip_srt

FIXTURES = Path(__file__).parent / "fixtures"


class StripCcTests(unittest.TestCase):
    def test_fixture_round_trip(self) -> None:
        raw = (FIXTURES / "sample.srt").read_text(encoding="utf-8")
        expected = (FIXTURES / "sample.expected.srt").read_text(encoding="utf-8")
        self.assertEqual(strip_srt(raw), expected)

    def test_partial_strip(self) -> None:
        self.assertEqual(clean_text_line("［女性２］テレビ"), "テレビ")
        self.assertEqual(clean_text_line("[Narrator] Hello (cough)"), "Hello")

    def test_whole_line_deleted(self) -> None:
        self.assertIsNone(clean_text_line("（せき払い）"))
        self.assertIsNone(clean_text_line("［女子高生１］"))

    def test_renumber_after_delete(self) -> None:
        result = strip_srt(
            "1\n00:00:01,000 --> 00:00:02,000\n（音）\n\n"
            "2\n00:00:03,000 --> 00:00:04,000\n残る\n"
        )
        self.assertEqual(
            result,
            "1\n00:00:03,000 --> 00:00:04,000\n残る\n",
        )

    def test_bom_stripped(self) -> None:
        result = strip_srt("\ufeff1\n00:00:01,000 --> 00:00:02,000\nこんにちは\n")
        self.assertEqual(result, "1\n00:00:01,000 --> 00:00:02,000\nこんにちは\n")

    def test_output_path(self) -> None:
        self.assertEqual(
            output_path_for(Path("/tmp/movie.srt")),
            Path("/tmp/movie.clean.srt"),
        )

    def test_process_file_writes_sibling(self) -> None:
        src = FIXTURES / "sample.srt"
        out = process_file(src, force=True)
        self.addCleanup(lambda: out.unlink(missing_ok=True))
        self.assertEqual(out.name, "sample.clean.srt")
        expected = (FIXTURES / "sample.expected.srt").read_text(encoding="utf-8")
        self.assertEqual(out.read_text(encoding="utf-8"), expected)


if __name__ == "__main__":
    unittest.main()
