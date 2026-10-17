"""Meaningful source-preparation checks; no downloads or model calls."""
from pathlib import Path
import sys
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from prepare_study import compact_captions, page_numbers, seconds


class SourceTests(unittest.TestCase):
    def test_rolling_captions_keep_only_new_words(self):
        raw='''WEBVTT

00:00:01.000 --> 00:00:03.000
<c>Matrix</c> exponential

00:00:03.000 --> 00:00:05.000
Matrix exponential maps a state.

00:00:31.000 --> 00:00:32.000
A &amp; B
'''
        rows=compact_captions(raw)
        self.assertEqual(rows,[{'start':0,'text':'Matrix exponential maps a state.'},{'start':30,'text':'A & B'}])

    def test_local_asr_retains_deliberate_repetition(self):
        raw='''00:00:01.000 --> 00:00:03.000
That is very

00:00:03.000 --> 00:00:05.000
very important.
'''
        self.assertEqual(compact_captions(raw,rolling=False)[0]['text'],'That is very very important.')

    def test_later_identical_statement_is_not_removed(self):
        raw='00:00:01.000 --> 00:00:02.000\nYes\n\n00:01:01.000 --> 00:01:02.000\nYes\n'
        self.assertEqual(len(compact_captions(raw)),2)

    def test_page_ranges_deduplicate(self):
        self.assertEqual(page_numbers('351-352,352,354'),[351,352,354])
        for spec in ['0','4-2','-1']:
            with self.assertRaises(ValueError):
                page_numbers(spec)

    def test_timestamps(self):
        self.assertEqual(seconds('01:02:03.500'),3723.5)


if __name__=='__main__':
    unittest.main()
