"""Meaningful source-preparation checks; no downloads or model calls."""
from pathlib import Path
import sys
import unittest
import tempfile
import json

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from prepare_study import compact_captions, page_numbers, seconds
from study_pipeline import route, make_brief, record_stage
from run_claude import summary


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

    def test_registered_playlist_routes_and_selects_recipe(self):
        p=route('https://www.youtube.com/watch?v=u5Sv7YKAkt4&list=PLMrJAkhIeNNR20Mz-VpzgfQs5zrYi085m','Controllability')
        self.assertEqual((p['subject'],p['strategy'],p['book_pages']),('controls','controllability','356-357'))

    def test_unknown_subjects_and_playlist_conflicts_are_not_guessed(self):
        url='https://www.youtube.com/watch?v=u5Sv7YKAkt4'
        with self.assertRaises(ValueError): route(url,'Controls')
        self.assertEqual(route(url,'New Topic',subject='controls')['strategy'],'general')
        with self.assertRaises(ValueError):
            route(url+'&list=PLMrJAkhIeNNR20Mz-VpzgfQs5zrYi085m','Controllability',subject='ode')
        for bad in ['https://evil.example/watch?v=u5Sv7YKAkt4','https://youtube.com/watch?v=bad']:
            with self.assertRaises(ValueError): route(bad,'Controllability',subject='controls')

    def test_brief_bounds_work_and_does_not_request_historical_logs(self):
        p=route('https://youtube.com/watch?v=u5Sv7YKAkt4','Controllability',subject='controls')
        p.update(package='courses/controls/trial',slug='trial',title='Trial')
        brief=make_brief(p)
        self.assertIn('Do NOT render',brief)
        self.assertIn('fresh session',brief)
        self.assertIn('sources/trial/REVIEW.md',brief)

    def test_runner_distinguishes_budget_stop_and_aggregates_usage(self):
        result=summary([{'type':'result','subtype':'error_max_budget_usd','is_error':True,
                         'session_id':'test','modelUsage':{'opus':{'outputTokens':12,'cacheReadInputTokens':100,'costUSD':0.25}}}])
        self.assertTrue(result['is_error'])
        self.assertEqual(result['subtype'],'error_max_budget_usd')
        self.assertEqual(result['usage_totals']['outputTokens'],12)
        self.assertEqual(result['usage_totals']['cacheReadInputTokens'],100)
        self.assertEqual(result['usage_totals']['costUSD'],0.25)

    def test_checkpoint_merges_independent_stages(self):
        with tempfile.TemporaryDirectory() as work:
            p=Path(work)/'pipeline.json';p.write_text(json.dumps({'plan':{'slug':'test'},'stages':{}}),encoding='utf-8')
            record_stage(p,'author',{'ok':False,'running':True})
            record_stage(p,'render',{'ok':True})
            record_stage(p,'author',{'ok':True})
            saved=json.loads(p.read_text(encoding='utf-8'))
            self.assertEqual(saved['stages'],{'author':{'ok':True},'render':{'ok':True}})
            self.assertEqual(saved['plan'],{'slug':'test'})


if __name__=='__main__':
    unittest.main()
