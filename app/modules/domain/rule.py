from decimal import Decimal as D, ROUND_HALF_UP
from app.errors import DataError
from .values import whole, number, parts


def tiers(raw):
    bands = []
    for entry in parts(raw):
        end, sep, rate = entry.partition(':')
        if not sep:
            raise DataError('ROYALTY_TIER', '费档缺少比率')
        bands.append((None if end == '*' else whole(end, 1, 10**9), number(rate, 0, 100)/100))
    if not bands or bands[-1][0] is not None or any(end is None for end,_ in bands[:-1]):
        raise DataError('ROYALTY_TIER', '最后一档须无上限')
    caps = [end for end,_ in bands[:-1]]
    if caps != sorted(set(caps)):
        raise DataError('ROYALTY_TIER', '费档上限须严格递增')
    return bands


def evaluate(row):
    opening = whole(row['期初净销'], 0, 10**9)
    gross = whole(row['出库册数'], 0, 10**9)
    returned = whole(row['实退册数'], 0, 10**9)
    price = number(row['定价元'], 0, 10**6)
    reserve = number(row['留存百分比'], 0, 100) / 100
    release = number(row['释放准备金元'], 0, 10**12)
    close = opening+gross-returned
    if close < 0:
        raise DataError('ROYALTY_RETURNS', '退货超过累计可冲销量')
    accrued, reversed_ = D(0), D(0)
    proof = []
    lower = 0
    for upper, rate in tiers(row['版税阶梯']):
        cap = upper if upper is not None else opening+gross
        copies = max(0, min(cap, opening+gross)-max(lower, opening))
        refunds = max(0, min(cap, opening+gross)-max(lower, close))
        subtotal = (copies-refunds)*price*rate
        if copies or refunds:
            proof.append((f'{lower+1}–{upper or "以上"} 档净计提', subtotal, '元'))
        accrued += copies*price*rate
        reversed_ += refunds*price*rate
        lower = cap
    held = max(D(0), accrued-reversed_)*reserve
    proof.extend([('出库计提', accrued, '元'), ('实退逆冲', reversed_, '元'),
                  ('本期留存', held, '元'), ('前期释放', release, '元')])
    return (accrued-reversed_-held+release).quantize(D('0.01'), rounding=ROUND_HALF_UP), proof
