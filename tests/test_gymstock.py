"""
Though not especially utilised herein, this page was recognised as
an authoritative rationale of mocking for unit testing:

https://www.fugue.co/blog/2016-02-11-python-mocking-101

That leaves mocking only specific methods of our object:

https://stackoverflow.com/a/19737253
"""
from unittest.mock import patch, call, sentinel

import pytest

from truffshuff import GymStock, DEFAULT_PLATES, Plate


@pytest.fixture
def plate():
    return Plate(5, 30)


@pytest.fixture
def stock_gym_stock():
    return GymStock(1, 2)


def test_set_weights_quantities(stock_gym_stock):
    """Supply quantities of standard sized weights and check they are stored."""
    quantities = ["6", "6", "4", "2"]
    stock_gym_stock.set_weights_quantities(quantities, DEFAULT_PLATES)
    assert stock_gym_stock.weight_dict == {x[0]: int(x[1]) for x in zip(DEFAULT_PLATES, quantities)}


def test_set_weights_quantities_ignores_extra(stock_gym_stock):
    quantities = ["6", "6", "4", "2", "2", "2"]
    stock_gym_stock.set_weights_quantities(quantities, DEFAULT_PLATES)
    assert stock_gym_stock.weight_dict == {x[0]: int(x[1]) for x in zip(DEFAULT_PLATES, quantities)}


def test_set_weights_quantities_fails(stock_gym_stock):
    with pytest.raises(ValueError) as e_info:
        stock_gym_stock.set_weights_quantities(["6*4", "6", "4", "2"], DEFAULT_PLATES)
    with pytest.raises(ValueError) as e_info:
        stock_gym_stock.set_weights_quantities(["6.1", "6", "4", "2"], DEFAULT_PLATES)
    with pytest.raises(ValueError) as e_info:
        stock_gym_stock.set_weights_quantities(["abc", "6", "4", "2"], DEFAULT_PLATES)


def test_set_custom_weights(stock_gym_stock):
    stock_gym_stock.set_custom_weights(["7.5*35*3"])
    custom_plate = Plate(7.5, 35)
    assert {custom_plate: 3} == stock_gym_stock.weight_dict
    stock_gym_stock.set_custom_weights(["7.5*35*3", "12*45*2"])
    custom_plate_2 = Plate(12, 45)
    assert {custom_plate: 3, custom_plate_2: 2} == stock_gym_stock.weight_dict


def test_validate_custom_weight():
    GymStock.validate_custom_weight("7.5*35*3")  # 7.5kg 35mm 3 of
    GymStock.validate_custom_weight("3*15*4")


def test_validate_custom_weight_float_not_int_failure():
    with pytest.raises(ValueError) as e_info:
        GymStock.validate_custom_weight("7*35.2*3")
    with pytest.raises(ValueError) as e_info:
        GymStock.validate_custom_weight("7*35.2*3.5")


def test_validate_custom_weight_missing_qty_failure():
    with pytest.raises(ValueError) as e_info:
        GymStock.validate_custom_weight("7.5*3")


def test_validate_custom_weight_bad_kg_failure():
    with pytest.raises(ValueError) as e_info:
        GymStock.validate_custom_weight("seven*3*2")


def test_validate_custom_weight_bad_qty_failure():
    with pytest.raises(ValueError) as e_info:
        GymStock.validate_custom_weight("5*3*0.5")


@patch("builtins.input", side_effect=["4", "5"])
def test_elicit_plate_count(patched_input, plate):
    count = GymStock.elicit_plate_count(plate)
    assert count == "4"
    patched_input.assert_called_once()
    patched_input.assert_called_once_with("{}*".format(plate))
    count = GymStock.elicit_plate_count(plate)
    assert count == "5"
    patched_input.assert_has_calls([call("{}*".format(plate)), call("{}*".format(plate))])


@patch("builtins.input", side_effect=[""])
def test_elicit_plate_count_done(patched_input, plate):
    count = GymStock.elicit_plate_count(plate)
    assert count == ""
    patched_input.assert_called_once_with("{}*".format(plate))


@patch("builtins.input", side_effect=["foobar", "4"])
def test_elicit_plate_count_invalid_input(patched_input, capsys, plate):
    count = GymStock.elicit_plate_count(plate)
    captured = capsys.readouterr()
    assert captured.out == 'foobar invalid quantity, try again.\n'
    assert count == "4"
    patched_input.assert_has_calls([call("{}*".format(plate)), call("{}*".format(plate))])


@patch("builtins.input", side_effect=["1", "0", "2", "4", ""])
def test_elicit_weights_std(patched_input, stock_gym_stock):
    with patch.object(stock_gym_stock, "elicit_weight_quantities") as mock_elicit_weight_quantities:
        stock_gym_stock.elicit_weights([sentinel.plate1, sentinel.plate2])
        mock_elicit_weight_quantities.assert_called_once_with([sentinel.plate1, sentinel.plate2])


@patch("builtins.input", side_effect=["2", "7.5*35*3", "doh!", "3*15*4", ""])
def test_elicit_weights_custom(patched_input, stock_gym_stock):
    stock_gym_stock.elicit_weights(DEFAULT_PLATES)
    custom_plate_7k5 = Plate(7.5, 35)
    custom_plate_3kg = Plate(3, 15)
    assert stock_gym_stock.weight_dict == {
        custom_plate_7k5: 3,
        custom_plate_3kg: 4
    }


@patch("builtins.input", side_effect=["0", "2", "4", ""])
def test_elicit_weight_quantities(patched_input, stock_gym_stock):
    """Provide 2*2.5kg and 4*5kg standard weights."""
    stock_gym_stock.elicit_weight_quantities(DEFAULT_PLATES)
    assert stock_gym_stock.weight_dict == {x[0]: x[1] for x in zip(DEFAULT_PLATES, [0, 2, 4])}


def test_check_bar_capacities_odd_dumbbells_fails():
    DEFAULT_BARBELL_MM = GymStock.STD_BARBELL_THREAD_LEN
    DEFAULT_DUMBBELL_MM = GymStock.STD_DUMBBELL_THREAD_LEN
    with pytest.raises(ValueError) as e_info:
        GymStock.check_bar_capacities([1], [1])
    assert DEFAULT_BARBELL_MM == GymStock.STD_BARBELL_THREAD_LEN
    assert DEFAULT_DUMBBELL_MM == GymStock.STD_DUMBBELL_THREAD_LEN


def test_check_bar_capacities_dont_update():
    DEFAULT_BARBELL_MM = GymStock.STD_BARBELL_THREAD_LEN
    DEFAULT_DUMBBELL_MM = GymStock.STD_DUMBBELL_THREAD_LEN
    GymStock.check_bar_capacities([1], [2])
    assert DEFAULT_BARBELL_MM == GymStock.STD_BARBELL_THREAD_LEN
    assert DEFAULT_DUMBBELL_MM == GymStock.STD_DUMBBELL_THREAD_LEN


def test_check_bar_capacities_update():
    DEFAULT_BARBELL_MM = GymStock.STD_BARBELL_THREAD_LEN
    DEFAULT_DUMBBELL_MM = GymStock.STD_DUMBBELL_THREAD_LEN
    GymStock.check_bar_capacities([1, DEFAULT_BARBELL_MM // 2], [2, DEFAULT_DUMBBELL_MM // 2])
    assert DEFAULT_BARBELL_MM // 2 == GymStock.STD_BARBELL_THREAD_LEN
    assert DEFAULT_DUMBBELL_MM // 2 == GymStock.STD_DUMBBELL_THREAD_LEN


def test_validate_custom_bar():
    GymStock.validate_custom_bar("1*250")


def test_validate_custom_bar_raises():
    with pytest.raises(ValueError) as e_info:
        GymStock.validate_custom_bar("1*2*3")
    with pytest.raises(ValueError) as e_info:
        GymStock.validate_custom_bar("1*A")
    with pytest.raises(ValueError) as e_info:
        GymStock.validate_custom_bar("1*2.3")
    with pytest.raises(ValueError) as e_info:
        GymStock.validate_custom_bar("BAD")
