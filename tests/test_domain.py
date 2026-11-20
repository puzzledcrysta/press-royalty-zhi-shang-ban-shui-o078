from decimal import Decimal
import pytest
from app.errors import DataError
from app.modules.domain.rule import evaluate


def test_crosses(cases):
    actual, proof = evaluate(cases['crosses'])
    assert actual == Decimal('144.00')
    assert Decimal(str(dict((label, value) for label, value, _ in proof)['出库计提'])) == Decimal('160.0')


def test_reverse_higher(cases):
    # TRAP-104
    actual, proof = evaluate(cases['reverse_higher'])
    assert actual == Decimal('90.00')
    assert Decimal(str(dict((label, value) for label, value, _ in proof)['实退逆冲'])) == Decimal('165.00')


def test_contract_release(cases):
    actual, proof = evaluate(cases['contract_release'])
    assert actual == Decimal('90.90')
    assert Decimal(str(dict((label, value) for label, value, _ in proof)['前期释放'])) == Decimal('13')


def test_negative_net(cases):
    actual, proof = evaluate(cases['negative_net'])
    assert actual == Decimal('-20.00')
    assert Decimal(str(dict((label, value) for label, value, _ in proof)['本期留存'])) == Decimal('0')


def test_half_cent(cases):
    # TRAP-10
    actual, proof = evaluate(cases['half_cent'])
    assert actual == Decimal('0.01')
    assert proof


def test_exact_split(cases):
    actual, proof = evaluate(cases['exact_split'])
    assert actual == Decimal('50.54')
    assert proof


def test_excess_return(cases):
    with pytest.raises(DataError) as error:
        evaluate(cases['excess_return'])
    assert error.value.code == 'ROYALTY_RETURNS'


def test_out_of_order(cases):
    with pytest.raises(DataError) as error:
        evaluate(cases['out_of_order'])
    assert error.value.code == 'ROYALTY_TIER'


def test_no_open_tier(cases):
    with pytest.raises(DataError) as error:
        evaluate(cases['no_open_tier'])
    assert error.value.code == 'ROYALTY_TIER'
