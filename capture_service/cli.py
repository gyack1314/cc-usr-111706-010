"""重放冻结来源并显示采集状态。"""
import argparse
import json
from .transport import Replay
from .ledger import connect,receive
from .view import overview
def main():
    p=argparse.ArgumentParser()
    p.add_argument('command',choices=['inspect'])
    p.add_argument('manifest')
    args=p.parse_args()
    replay=Replay(args.manifest)
    db=connect(':memory:')
    collection='energy-filings'
    for step in replay.steps:
        req=step['request']
        raw,receipt=replay.request(req['method'],req['url'])
        receive(db,collection,raw,receipt)
    print(json.dumps(overview(db,collection),ensure_ascii=False,indent=2))
    db.close()
if __name__=='__main__':main()
