import pytest
from currency import Currency

# Usage:
#   1. Run start_script.py with a "--QuoteServer 0" flag
#   2. run 'pytest' from commandline within project directory to run all project tests
#       - run 'pytest test_system.py' to run just this file
#       - run 'pytest test_system.py::specific_test_name' to run just one test in this file

# 'currency' initializer and zero bound testing ------------------------------------------------------------------------
def test_currency_initializer_zero_value():
    try:
        zero_bound1 = Currency(0.0)
        Currency(0)
        Currency(zero_bound1)
        Currency("0")
        Currency("0.0")
        Currency()
        Currency(None)
    except ValueError as e:
        pytest.fail(repr(e))

    with pytest.raises(ValueError):
        zero_bound_bad = Currency("zero")

def test_currency_equivalence_to_zero():
    zero_bound1 = Currency(0.0)
    zero_bound2 = Currency(0)
    assert zero_bound1.dollars == 0
    assert zero_bound1.cents == 0
    assert zero_bound1 == 0.0
    assert zero_bound1 == 0
    assert zero_bound1 == zero_bound2
    assert isinstance(zero_bound1.dollars, int)
    assert isinstance(zero_bound1.cents, int)
    assert str(zero_bound1) == "0.00"
    assert float(zero_bound1) == 0.0
    assert -0.01 < zero_bound1 < 0.01

# 'currency' initializer and positive bound value testing --------------------------------------------------------------
def test_currency_initializer_positive_value():
    try:
        pos_low_bound1 = Currency(0.01)
        Currency(1)
        Currency(pos_low_bound1)
        Currency("1")
        Currency("0.01")
    except ValueError as e:
        pytest.fail(repr(e))

    with pytest.raises(ValueError):
        pos_low_bound9 = Currency("1l7.12")

def test_currency_equivalence_low_positive():
    pos_low_bound1 = Currency(0.01)
    pos_low_bound2 = Currency(1)
    pos_low_bound3 = Currency("0.01")
    assert pos_low_bound1.dollars == 0
    assert pos_low_bound1.cents == 1
    assert pos_low_bound1 == 0.01
    assert pos_low_bound2 == pos_low_bound1 + 0.99
    assert pos_low_bound1 == pos_low_bound3
    assert pos_low_bound1 != pos_low_bound2
    assert isinstance(pos_low_bound1.dollars, int)
    assert isinstance(pos_low_bound1.cents, int)
    assert str(pos_low_bound1) == "0.01"
    assert float(pos_low_bound1) == 0.01
    assert 0.0 < pos_low_bound1 < 0.02

def test_currency_equivalence_random_positive():
    pos_rndm_bound1 = Currency(10)
    pos_rndm_bound2 = Currency(10.01)
    pos_rndm_bound3 = Currency(10.000000000101)
    pos_rndm_bound4 = Currency(10.006)
    pos_rndm_bound5 = Currency("0.010000000000")
    pos_rndm_bound6 = Currency("0.010000000001")
    pos_rndm_bound7 = Currency("0.016")
    assert pos_rndm_bound1.dollars == 10
    assert pos_rndm_bound1.cents == 0
    assert pos_rndm_bound1 == 10.0

    assert pos_rndm_bound2.dollars == 10
    assert pos_rndm_bound2.cents == 1
    assert pos_rndm_bound2 == 10.01

    assert pos_rndm_bound3.dollars == 10
    assert pos_rndm_bound3.cents == 0
    assert pos_rndm_bound3 == 10.0

    assert pos_rndm_bound4.dollars == 10
    assert pos_rndm_bound4.cents == 1
    assert pos_rndm_bound4 == 10.01

    assert pos_rndm_bound5.dollars == 0
    assert pos_rndm_bound5.cents == 1
    assert pos_rndm_bound5 == 0.01

    assert pos_rndm_bound6.dollars == 0
    assert pos_rndm_bound6.cents == 1
    assert pos_rndm_bound6 == 0.01
    assert pos_rndm_bound6 == pos_rndm_bound5

    assert pos_rndm_bound7.dollars == 0
    assert pos_rndm_bound7.cents == 2
    assert pos_rndm_bound7 == 0.02

    assert isinstance(pos_rndm_bound5.dollars, int)
    assert isinstance(pos_rndm_bound5.cents, int)
    assert str(pos_rndm_bound1) == "10.00"
    assert str(pos_rndm_bound5) == "0.01"
    assert float(pos_rndm_bound5) == 0.01
    assert 0.0 < pos_rndm_bound5 < 0.02

# 'currency' initializer and negative bound value testing --------------------------------------------------------------
def test_currency_initializer_negative():
    try:
        neg_low_bound1 = Currency(-0.01)
        Currency(-1)
        Currency(neg_low_bound1)
        Currency("-1")
        Currency("-0.01")
    except ValueError as e:
        pytest.fail(repr(e))

    with pytest.raises(ValueError):
        neg_low_bound7 = Currency("12.r3")

def test_currency_equivalence_negative():
    neg_low_bound1 = Currency(-0.01)
    neg_low_bound2 = Currency(-1)
    neg_low_bound3 = Currency("-0.01")
    assert neg_low_bound1.dollars == 0
    assert neg_low_bound1.cents == -1
    assert neg_low_bound1 == -0.01
    assert neg_low_bound2 == neg_low_bound1 - 0.99
    assert neg_low_bound1 == neg_low_bound3
    assert neg_low_bound1 != neg_low_bound2
    assert isinstance(neg_low_bound1.dollars, int)
    assert isinstance(neg_low_bound1.cents, int)
    assert str(neg_low_bound1) == "-0.01"
    assert float(neg_low_bound1) == -0.01
    assert 0.0 > neg_low_bound1 > -0.02

def test_currency_equivalence_random_negative():
    neg_rndm_bound1 = Currency(-10)
    neg_rndm_bound2 = Currency(-10.01)
    neg_rndm_bound3 = Currency(-10.00000000101)
    neg_rndm_bound4 = Currency(-10.006)
    neg_rndm_bound5 = Currency("-0.010000000000")
    neg_rndm_bound6 = Currency("-0.010000000001")
    neg_rndm_bound7 = Currency("-0.016")
    assert neg_rndm_bound1.dollars == -10
    assert neg_rndm_bound1.cents == 0
    assert neg_rndm_bound1 == -10.0

    assert neg_rndm_bound2.dollars == -10
    assert neg_rndm_bound2.cents == -1
    assert neg_rndm_bound2 == -10.01

    assert neg_rndm_bound3.dollars == -10
    assert neg_rndm_bound3.cents == 0
    assert neg_rndm_bound3 == -10.0

    assert neg_rndm_bound4.dollars == -10
    assert neg_rndm_bound4.cents == -1
    assert neg_rndm_bound4 == -10.01

    assert neg_rndm_bound5.dollars == 0
    assert neg_rndm_bound5.cents == -1
    assert neg_rndm_bound5 == -0.01

    assert neg_rndm_bound6.dollars == 0
    assert neg_rndm_bound6.cents == -1
    assert neg_rndm_bound6 == -0.01
    assert neg_rndm_bound6 == neg_rndm_bound5

    assert neg_rndm_bound7.dollars == 0
    assert neg_rndm_bound7.cents == -2
    assert neg_rndm_bound7 == -0.02

    assert isinstance(neg_rndm_bound5.dollars, int)
    assert isinstance(neg_rndm_bound5.cents, int)
    assert str(neg_rndm_bound5) == "-0.01"
    assert float(neg_rndm_bound5) == -0.01
    assert 0.0 > neg_rndm_bound5 > -0.02

# 'currency' json encoder testing --------------------------------------------------------------------------------------
def test_currency_json_encoding():
    import json
    unencoded = Currency(12.34)
    user_dict = {"acc": unencoded, "stk": 34.56, "empty_list": []}

    assert json.dumps(user_dict, cls=Currency) == '{"acc": 12.34, "stk": 34.56, "empty_list": []}'
