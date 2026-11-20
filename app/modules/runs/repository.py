import json
from app.errors import DataError
from app.store import connection

VOLATILE = ('elapsed_ms','created')


def stable(payload):
    result = json.loads(payload)
    for key in VOLATILE:
        result.get('manifest',{}).pop(key,None)
    return result


def lookup(db,run_id):
    row = db.execute('SELECT * FROM runs WHERE id=?',(run_id,)).fetchone()
    if row is None:
        raise DataError('RUN_UNKNOWN','没有此批次',404)
    return row


def fetch(run_id):
    with connection() as db:
        return lookup(db,run_id)


def persist(run_id,source,book,result,created):
    payload = json.dumps(result,ensure_ascii=False)
    with connection() as db:
        cursor = db.execute('INSERT OR IGNORE INTO runs VALUES (?,?,?,?,?)',
                            (run_id,source,book,payload,created))
        row = lookup(db,run_id)
        if not cursor.rowcount:
            # 指纹已存在：旧结果不可覆盖，内容必须一致，否则显式拒绝
            if row['source']!=source or row['book']!=book or stable(row['result'])!=stable(payload):
                raise DataError('RUN_CONFLICT','批次指纹与已存结果冲突，旧结果不可覆盖',409)
        return row


def history():
    with connection() as db:
        return [dict(row) for row in db.execute('SELECT id,created FROM runs ORDER BY created DESC,id DESC LIMIT 50')]
