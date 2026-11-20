import pytest
from app.settings import KEY, UNIT


@pytest.fixture
def anchor(client):
    return client.post('/api/runs',json={}).json()['manifest']['run_id']


@pytest.fixture
def clean(client):
    report = client.post('/api/runs',json={}).json()
    lines = [f"{row['key']},{row['amount']}" for row in report['accepted']]
    book = f'{KEY},外部记录值({UNIT})\n' + '\n'.join(lines) + '\n'
    return client.post('/api/runs',json={'book':book}).json()['manifest']['run_id']


def review(client,anchor,version=0,decision='确认',note='已逐条核对外部账'):
    return client.post(f'/api/review/{anchor}',json={'version':version,'decision':decision,'note':note})


def test_stale(client,clean):
    # TRAP-26
    assert review(client,clean).json()['version']==1
    stale = review(client,clean)
    assert (stale.status_code,stale.json()['code'])==(409,'STALE')


def test_noted_differences(client,anchor):
    response = review(client,anchor,decision='退回',note='  ')
    assert (response.status_code,response.json()['code'])==(422,'REVIEW_NOTE')


def test_settlement_blocked(client,anchor):
    blocked = review(client,anchor)
    assert (blocked.status_code,blocked.json()['code'])==(422,'SETTLE_BLOCKED')
    assert review(client,anchor,decision='退回',note='账差未核销，退回发行渠道').status_code==200


def test_versioned_history(client,clean):
    assert review(client,clean).status_code == 200
    assert review(client,clean,1,'退回','请补来源旁证').status_code == 200
    assert [item['version'] for item in client.get(f'/api/review/{clean}').json()] == [2,1]


def test_export_reproducible(client,anchor):
    first = client.get(f'/api/export/{anchor}')
    second = client.get(f'/api/export/{anchor}')
    assert first.content == second.content and 'attachment' in first.headers['content-disposition']


def test_export_carries_source_evidence(client,anchor):
    proof = client.get(f'/api/export/{anchor}').json()
    row = proof['results'][0]
    assert (row['key'],row['line'])==('00101',2)
    assert row['raw'] and row['proof'] and proof['quarantine']


def test_export_preserves_tier_attribution(client,anchor):
    proof = client.get(f'/api/export/{anchor}').json()
    row = next(item for item in proof['results'] if item['key']=='00102')
    attribution = {item['metric']:item['value'] for item in row['proof']}
    assert attribution['1–1000 档退货归属']=='25'
    assert attribution['1001–以上 档退货归属']=='50'
    assert attribution['本期应付']==row['amount']


def test_decision_reaches_export(client,clean):
    assert review(client,clean).status_code==200
    assert client.get(f'/api/export/{clean}').json()['review'][0]['decision']=='确认'
