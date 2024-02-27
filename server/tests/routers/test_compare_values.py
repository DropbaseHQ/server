import pytest
import copy
from server.controllers.display_rules import compare_values
from server.tests.routers.test_components import base_data
from datetime import datetime, timedelta
from requests import Response


# Tests the compare_values function in display_rules.py


def test_equals_operator_succeeds_when_equal():
    target_value = 5
    operator = "equals"
    rule_value = 5
    target_type = "int"

    result = compare_values(target_value, operator, rule_value, target_type)

    assert result == True


def test_equals_operator_fails_when_not_equal():
    target_value = 5
    operator = "equals"
    rule_value = 10
    target_type = "int"

    result = compare_values(target_value, operator, rule_value, target_type)

    assert result == False


def test_equals_operator_succeeds_with_string():
    target_value = "test"
    operator = "equals"
    rule_value = "test"
    target_type = "text"

    result = compare_values(target_value, operator, rule_value, target_type)

    assert result == True


def test_equals_operator_fails_with_string():
    target_value = "test"
    operator = "equals"
    rule_value = "test2"
    target_type = "text"

    result = compare_values(target_value, operator, rule_value, target_type)

    assert result == False


def test_equals_operator_succeeds_with_boolean():
    target_value = True
    operator = "equals"
    rule_value = True
    target_type = "boolean"

    result = compare_values(target_value, operator, rule_value, target_type)

    assert result == True


def test_equals_operator_fails_with_boolean():
    target_value = True
    operator = "equals"
    rule_value = False
    target_type = "boolean"

    result = compare_values(target_value, operator, rule_value, target_type)

    assert result == False


def test_equals_operator_succeeds_with_date():
    target_value = datetime.now().timestamp()
    operator = "equals"
    rule_value = target_value
    target_type = "date"

    result = compare_values(target_value, operator, rule_value, target_type)

    assert result == True


def test_equals_operator_fails_with_date():
    target_value = datetime.now().timestamp()
    operator = "equals"
    rule_value = datetime.now() + timedelta(days=1)
    target_type = "date"

    result = compare_values(target_value, operator, rule_value.timestamp(), target_type)

    assert result == False


def test_equals_operator_succeeds_with_mix_string_and_int():
    target_value = "5"
    operator = "equals"
    rule_value = 5
    target_type = "int"

    result = compare_values(target_value, operator, rule_value, target_type)

    assert result == True


def test_equals_operator_fails_with_mix_string_and_int():
    target_value = "5"
    operator = "equals"
    rule_value = 10
    target_type = "int"

    result = compare_values(target_value, operator, rule_value, target_type)

    assert result == False


def test_equals_operator_succeeds_with_mix_string_and_float():
    target_value = "5.0"
    operator = "equals"
    rule_value = 5.0
    target_type = "float"

    result = compare_values(target_value, operator, rule_value, target_type)

    assert result == True


def test_equals_operator_fails_with_mix_string_and_float():
    target_value = "5.0"
    operator = "equals"
    rule_value = 10.0
    target_type = "float"

    result = compare_values(target_value, operator, rule_value, target_type)

    assert result == False


def test_equals_operator_succeeds_with_mix_string_and_boolean():
    target_value = "true"
    operator = "equals"
    rule_value = True
    target_type = "boolean"

    result = compare_values(target_value, operator, rule_value, target_type)

    assert result == True


def test_equals_operator_fails_with_mix_string_and_boolean():
    target_value = "true"
    operator = "equals"
    rule_value = False
    target_type = "boolean"

    result = compare_values(target_value, operator, rule_value, target_type)

    assert result == False


def test_lt_operator_succeeds_when_less_than():
    target_value = 5
    operator = "lt"
    rule_value = 10
    target_type = "int"

    result = compare_values(target_value, operator, rule_value, target_type)

    assert result == True


def test_lt_operator_fails_when_equal():
    target_value = 5
    operator = "lt"
    rule_value = 5
    target_type = "int"

    result = compare_values(target_value, operator, rule_value, target_type)

    assert result == False


# lte operator
def test_lte_operator_succeeds_when_less_than_or_equal():
    target_value = 5
    operator = "lte"
    rule_value = 5
    target_type = "int"

    result = compare_values(target_value, operator, rule_value, target_type)

    assert result == True


def test_lte_operator_fails_when_greater_than():
    target_value = 10
    operator = "lte"
    rule_value = 5
    target_type = "int"

    result = compare_values(target_value, operator, rule_value, target_type)

    assert result == False


def test_gt_operator_succeeds_when_greater_than():
    target_value = 10
    operator = "gt"
    rule_value = 5
    target_type = "int"

    result = compare_values(target_value, operator, rule_value, target_type)

    assert result == True


def test_gt_operator_fails_when_equal():
    target_value = 5
    operator = "gt"
    rule_value = 5
    target_type = "int"

    result = compare_values(target_value, operator, rule_value, target_type)

    assert result == False


def test_gte_operator_succeeds_when_greater_than_or_equal():
    target_value = 10
    operator = "gte"
    rule_value = 10
    target_type = "int"

    result = compare_values(target_value, operator, rule_value, target_type)

    assert result == True


def test_gte_operator_fails_when_less_than():
    target_value = 5
    operator = "gte"
    rule_value = 10
    target_type = "int"

    result = compare_values(target_value, operator, rule_value, target_type)

    assert result == False


def test_not_equals_operator():
    target_value = 5
    operator = "not_equals"
    rule_value = 10
    target_type = "int"

    result = compare_values(target_value, operator, rule_value, target_type)

    assert result == True


def test_not_equals_operator_succeeds_when_not_equal():
    target_value = 5
    operator = "not_equals"
    rule_value = 10
    target_type = "int"

    result = compare_values(target_value, operator, rule_value, target_type)

    assert result == True


def test_not_equals_operator_fails_when_equal():
    target_value = 5
    operator = "not_equals"
    rule_value = 5
    target_type = "int"

    result = compare_values(target_value, operator, rule_value, target_type)

    assert result == False


def test_not_equals_operator_succeeds_with_string():
    target_value = "test"
    operator = "not_equals"
    rule_value = "test2"
    target_type = "text"

    result = compare_values(target_value, operator, rule_value, target_type)

    assert result == True


def test_not_equals_operator_fails_with_string():
    target_value = "test"
    operator = "not_equals"
    rule_value = "test"
    target_type = "text"

    result = compare_values(target_value, operator, rule_value, target_type)

    assert result == False


def test_not_equals_operator_succeeds_with_boolean():
    target_value = True
    operator = "not_equals"
    rule_value = False
    target_type = "boolean"

    result = compare_values(target_value, operator, rule_value, target_type)

    assert result == True


def test_not_equals_operator_fails_with_boolean():
    target_value = True
    operator = "not_equals"
    rule_value = True
    target_type = "boolean"

    result = compare_values(target_value, operator, rule_value, target_type)

    assert result == False


def test_not_equals_operator_succeeds_with_date():
    target_value = datetime.now().timestamp()
    operator = "not_equals"
    rule_value = datetime.now() + timedelta(days=1)
    target_type = "date"

    result = compare_values(target_value, operator, rule_value.timestamp(), target_type)

    assert result == True


def test_not_equals_operator_fails_with_date():
    target_value = datetime.now().timestamp()
    operator = "not_equals"
    rule_value = target_value
    target_type = "date"

    result = compare_values(target_value, operator, rule_value, target_type)

    assert result == False


def test_not_equals_operator_succeeds_with_mix_string_and_int():
    target_value = "5"
    operator = "not_equals"
    rule_value = 10
    target_type = "int"

    result = compare_values(target_value, operator, rule_value, target_type)

    assert result == True


def test_not_equals_operator_fails_with_mix_string_and_int():
    target_value = "5"
    operator = "not_equals"
    rule_value = 5
    target_type = "int"

    result = compare_values(target_value, operator, rule_value, target_type)

    assert result == False


def test_not_equals_operator_succeeds_with_mix_string_and_float():
    target_value = "5.0"
    operator = "not_equals"
    rule_value = 10.0
    target_type = "float"

    result = compare_values(target_value, operator, rule_value, target_type)

    assert result == True


def test_not_equals_operator_fails_with_mix_string_and_float():
    target_value = "5.0"
    operator = "not_equals"
    rule_value = 5.0
    target_type = "float"

    result = compare_values(target_value, operator, rule_value, target_type)

    assert result == False


def test_not_equals_operator_succeeds_with_mix_string_and_boolean():
    target_value = "true"
    operator = "not_equals"
    rule_value = True
    target_type = "boolean"

    result = compare_values(target_value, operator, rule_value, target_type)

    assert result == False


def test_not_equals_operator_fails_with_mix_string_and_boolean():
    target_value = "true"
    operator = "not_equals"
    rule_value = False
    target_type = "boolean"

    result = compare_values(target_value, operator, rule_value, target_type)

    assert result == True
