"""按来源身份原子登记原文与领域记录。"""
import hashlib
import json
import sqlite3
from .domain import decode
SCHEMA="""
CREATE TABLE IF NOT EXISTS receipts(collection TEXT NOT NULL,body_sha256 TEXT NOT NULL,source_url TEXT NOT NULL,status INTEGER NOT NULL,raw BLOB NOT NULL,PRIMARY KEY(collection,body_sha256));
CREATE TABLE IF NOT EXISTS entities(collection TEXT NOT NULL,entity_type TEXT NOT NULL,entity_id TEXT NOT NULL,version TEXT NOT NULL,receipt_sha256 TEXT NOT NULL,payload_json TEXT NOT NULL,PRIMARY KEY(collection,entity_type,entity_id,version),FOREIGN KEY(collection,receipt_sha256) REFERENCES receipts(collection,body_sha256));
"""
def connect(path):
    c=sqlite3.connect(path)
    c.execute('PRAGMA foreign_keys=ON')
    c.executescript(SCHEMA)
    return c
def receive(c,collection,raw,receipt):
    if receipt['status']!=200:raise ValueError('来源未返回成功正文')
    sha=hashlib.sha256(raw).hexdigest()
    if sha!=receipt['body_sha256']:raise ValueError('收据与原文不符')
    rows=decode(raw,receipt)
    with c:
        c.execute('INSERT OR IGNORE INTO receipts VALUES(?,?,?,?,?)',(collection,sha,receipt['url'],receipt['status'],raw))
        for row in rows:
            payload=json.dumps(row['payload'],ensure_ascii=False,sort_keys=True)
            key=(collection,row['type'],row['id'],row['version'])
            prior=c.execute('SELECT receipt_sha256,payload_json FROM entities WHERE collection=? AND entity_type=? AND entity_id=? AND version=?',key).fetchone()
            if prior and prior!=(sha,payload):raise ValueError('同一实体版本原文冲突')
            c.execute('INSERT OR IGNORE INTO entities VALUES(?,?,?,?,?,?)',(*key,sha,payload))
    return sha
def entities(c,collection):
    return [dict(type=r[0],id=r[1],version=r[2],source=r[3],payload=json.loads(r[4])) for r in c.execute('SELECT entity_type,entity_id,version,receipt_sha256,payload_json FROM entities WHERE collection=? ORDER BY entity_type,entity_id,version',(collection,))]
