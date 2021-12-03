import json
from unittest import mock
from unittest.mock import patch, call, sentinel, mock_open, Mock

import pytest

from truffshuff import parse_args, input_bar_specifier, DEFAULT_PLATES, accept_inventory_file, read_inventory, GymStock, \
    parse_cmd_line_args

MOCK_JSON = '''
{
    "barbells": "1*350", "dumbbells": "2*120", "sizes": [
        {"weight": 5, "thickness": 30, "quantity": 6},
        {"weight": 11.5, "thickness": 40, "quantity": 2}
    ]
}
'''


@patch("builtins.open", mock_open(read_data=MOCK_JSON))
@patch("truffshuff.GymStock", autospec=True)
def test_read_inventory_complete(patched_gym_stock):
    barbells, dumbbells, weight_dict = read_inventory(sentinel.path)
    inventory = json.loads(MOCK_JSON)
    barbells_spec = inventory.get("barbells", "0")
    barbells_spec = list(map(int, barbells_spec.split("*")))
    dumbbells_spec = inventory.get("dumbbells", "0")
    dumbbells_spec = list(map(int, dumbbells_spec.split("*")))
    assert barbells == barbells_spec[0]
    assert dumbbells == dumbbells_spec[0]
    patched_gym_stock.check_bar_capacities.assert_called_once_with(barbells_spec, dumbbells_spec)


@patch("truffshuff.read_inventory", return_value=[1, 2, {sentinel.plate: 2}])
def test_accept_inventory_file_complete(patched_read_inventory):
    gym_stock = accept_inventory_file(["-i", sentinel.path])
    patched_read_inventory.assert_called_once_with(sentinel.path)
    assert gym_stock.weight_dict == {sentinel.plate: 2}


@patch("truffshuff.read_inventory", return_value=[1, 2, {sentinel.plate: 0}])
@patch("truffshuff.GymStock", autospec=True)
def test_accept_inventory_file_wout_weights(mock_gymstock, patched_read_inventory):
    gym_stock = accept_inventory_file(["-i", sentinel.path])
    patched_read_inventory.assert_called_once_with(sentinel.path)
    mock_gymstock.assert_called_once_with(1, 2)
    mock_gymstock.return_value.elicit_weights.assert_called_once_with([sentinel.plate])


@patch("truffshuff.read_inventory", return_value=(0, 0, {sentinel.plate: 2}))
@patch("truffshuff.elicit_bars", return_value=mock.create_autospec(GymStock))
def test_accept_inventory_file_wout_bars(patched_elicit_bars, patched_read_inventory):
    gym_stock = accept_inventory_file(["-i", sentinel.path])
    patched_read_inventory.assert_called_once_with(sentinel.path)
    patched_elicit_bars.assert_called_once_with()
    assert gym_stock.weight_dict == {sentinel.plate: 2}


@patch("truffshuff.parse_cmd_line_args", return_value=Mock(spec=GymStock))
@patch("truffshuff.accept_inventory_file", return_value=None)
def test_parse_args(patched_accept_inventory, patched_parse_cmd_line):
    parse_args(sentinel.arg_list)
    patched_accept_inventory.assert_called_once_with(sentinel.arg_list)
    patched_parse_cmd_line.assert_called_once_with(sentinel.arg_list)
    patched_parse_cmd_line.return_value.balance_plates.assert_called_once_with()


@patch("builtins.input", side_effect=["1", "2"])
@patch("truffshuff.GymStock", autospec=True, STD_BARBELL_CAPACITY=sentinel.barbell_cap,
       STD_DUMBBELL_CAPACITY=sentinel.dumbbell_cap)
def test_parse_cmd_line_args_interactive(mock_gym_stock, patched_input):
    parse_cmd_line_args([])
    mock_gym_stock.assert_called_once_with(1, 2)
    patched_input.assert_has_calls([
        call("How many barbells (append '*thread_length' to change from {}mm)? ".
             format(mock_gym_stock.STD_BARBELL_THREAD_LEN)),
        call("How many dumbbells (append '*thread_length' to change from {}mm)? ".
             format(mock_gym_stock.STD_DUMBBELL_THREAD_LEN))
    ])
    mock_gym_stock.return_value.elicit_weights.assert_called_once_with(DEFAULT_PLATES)


@patch("truffshuff.GymStock", autospec=True)
def test_parse_cmd_line_args_semi_interactive(mock_gym_stock):
    parse_cmd_line_args(["1", "2"])
    mock_gym_stock.assert_called_once_with("1", "2")
    mock_gym_stock.return_value.elicit_weights.assert_called_once_with(DEFAULT_PLATES)


@patch("truffshuff.show_usage")
def test_parse_cmd_line_args_help(patched_show_usage):
    parse_cmd_line_args(["--help"])
    patched_show_usage.assert_called_once_with()


@patch("truffshuff.GymStock", autospec=True)
def test_parse_cmd_line_args_std_cmdline(mock_gym_stock):
    weight_qtys = ["0", "4", "2"]
    parse_cmd_line_args(["1", "2"] + weight_qtys)
    mock_gym_stock.assert_called_once_with("1", "2")
    mock_gym_stock.return_value.set_weights_quantities.assert_called_once_with(weight_qtys, DEFAULT_PLATES)


@patch("truffshuff.GymStock", autospec=True)
def test_parse_cmd_line_args_std_cmdline_fails(mock_gym_stock):
    weight_qtys = ["0", "doh!", "2"]
    mock_gym_stock.return_value.set_weights_quantities.side_effect = ValueError
    with pytest.raises(SystemExit) as e_info:
        parse_cmd_line_args(["1", "2"] + weight_qtys)
    mock_gym_stock.assert_called_once_with("1", "2")
    mock_gym_stock.return_value.set_weights_quantities.assert_called_once_with(weight_qtys, DEFAULT_PLATES)


@patch("truffshuff.GymStock", autospec=True)
def test_parse_cmd_line_args_mixed_cmdline_fails(mock_gym_stock):
    weight_qtys = ["0", "2.5*12*4", "2"]
    with pytest.raises(SystemExit) as e_info:
        parse_cmd_line_args(["1", "2"] + weight_qtys)
    mock_gym_stock.assert_called_once_with("1", "2")
    mock_gym_stock.return_value.set_weights_quantities.assert_not_called()


@patch("truffshuff.GymStock", autospec=True)
def test_parse_cmd_line_args_custom_cmdline(mock_gym_stock):
    weight_qtys = ["3*15*4", "6*25*4", "12*35*2"]
    parse_cmd_line_args(["1", "2"] + weight_qtys)
    mock_gym_stock.assert_called_once_with("1", "2")
    mock_gym_stock.return_value.set_custom_weights.assert_called_once_with(weight_qtys)


@patch("truffshuff.GymStock", autospec=True)
def test_parse_cmd_line_args_custom_cmdline_fails(mock_gym_stock):
    weight_qtys = ["3*15*4", "f**"]
    mock_gym_stock.return_value.set_custom_weights.side_effect = ValueError
    with pytest.raises(SystemExit) as e_info:
        parse_cmd_line_args(["1", "2"] + weight_qtys)
    mock_gym_stock.assert_called_once_with("1", "2")
    mock_gym_stock.return_value.set_custom_weights.assert_called_once_with(weight_qtys)


@patch("builtins.input", side_effect=["2", "2000", "000", "0", "xA", "1", "4*120"])
def test_input_bar_specifier(patched_input):
    assert [2] == input_bar_specifier("xyz", 32)
    assert [2000] == input_bar_specifier("xyz", 32)
    assert [0] == input_bar_specifier("xyz", 32)
    assert [0] == input_bar_specifier("xyz", 32)
    assert [1] == input_bar_specifier("xyz", 32)
    assert [4, 120] == input_bar_specifier("xyz", 32)
