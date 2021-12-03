import dataclasses

import pytest

from truffshuff import Plate


@pytest.fixture
def plate():
    return Plate(5, 30)


@pytest.fixture
def plate_clone():
    return Plate(5, 30)


@pytest.fixture
def heavier_plate():
    return Plate(10, 30)


@pytest.fixture
def thicker_plate():
    return Plate(5, 40)


def test_inequality(plate, heavier_plate, thicker_plate):
    assert plate != heavier_plate, "{} == {}".format(plate, heavier_plate)
    assert plate != thicker_plate, "{} == {}".format(plate, thicker_plate)


def test_equality(plate, plate_clone):
    assert plate == plate_clone, "{} != {}".format(plate, plate_clone)


def test_equality_to_other_type(plate):
    assert plate != "42", "{} == {}".format(plate, 42)


def test_set_membership(plate, plate_clone, thicker_plate, heavier_plate):
    s1 = {plate}
    assert plate_clone in s1, "{} missing from {}".format(plate_clone, s1)
    assert thicker_plate not in s1, "{} not expected in {}".format(thicker_plate, s1)
    assert heavier_plate not in s1, "{} not expected in {}".format(heavier_plate, s1)


def test_str_repr(plate):
    assert "{}kg".format(plate.weight) in str(plate)
    assert "{}mm".format(plate.thickness) in str(plate)


def test_plate_immutable(plate):
    with pytest.raises(dataclasses.FrozenInstanceError) as e_info:
        plate.weight = 1