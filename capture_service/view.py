"""按领域解释结果展示已接收证据及缺口。"""
from .ledger import entities
from .domain import assess
def overview(c,collection):
    rows=entities(c,collection)
    result=assess(rows)
    result['collection']=collection
    result['records']=[{'type':r['type'],'id':r['id'],'version':r['version'],'source_sha256':r['source']} for r in rows]
    return result
