"""核对同一来源链上的接收、解释、账本和缺口。"""
import unittest
from pathlib import Path
from capture_service.transport import Replay
from capture_service.ledger import connect,receive
from capture_service.view import overview
ROOT=Path(__file__).resolve().parents[1]
COLLECTION='energy-filings'
class Integration(unittest.TestCase):
    def test_complete_receipt_chain(self):
        replay=Replay(ROOT/'data/normal.json')
        db=connect(':memory:')
        for step in replay.steps:
            req=step['request']
            raw,receipt=replay.request(req['method'],req['url'])
            receive(db,COLLECTION,raw,receipt)
        view=overview(db,COLLECTION)
        self.assertGreaterEqual(len(view['records']),2)
        self.assertFalse(view['publishable'])
        self.assertTrue(view['reasons'])
        self.assertEqual(db.execute('SELECT COUNT(*) FROM receipts').fetchone()[0],len(replay.steps))
        db.close()
    def test_credential_scope(self):
        replay=Replay(ROOT/'data/normal.json')
        req=replay.steps[0]['request']
        with self.assertRaises(ValueError):replay.request(req['method'],req['url'],credential_scope='https://other.example.test')
        self.assertEqual(replay.position,0)
    def test_same_version_conflict_rolls_back(self):
        replay=Replay(ROOT/'data/conflict.json')
        db=connect(':memory:')
        req=replay.steps[0]['request']
        raw,receipt=replay.request(req['method'],req['url'])
        receive(db,COLLECTION,raw,receipt)
        before=overview(db,COLLECTION)
        req=replay.steps[1]['request']
        raw,receipt=replay.request(req['method'],req['url'])
        with self.assertRaises(ValueError):receive(db,COLLECTION,raw,receipt)
        self.assertEqual(overview(db,COLLECTION),before)
        self.assertEqual(db.execute('SELECT COUNT(*) FROM receipts').fetchone()[0],1)
        db.close()
