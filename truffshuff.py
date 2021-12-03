#!/usr/bin/env python3

"""
"""

import json
import os.path
import sys
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional


@dataclass(frozen=True)
class Plate:
    weight: float
    thickness: int

    def __repr__(self):
        return "{}kg*{}mm".format(self.weight, self.thickness)


# Standard weights, in standard units of kg.
# Thicknesses from Opti/Argos cast iron plates. 20kg is interpolated.
DEFAULT_PLATES = [
    Plate(1.25, 18),
    Plate(2.5, 25),
    Plate(5, 30),
    Plate(10, 40),
    Plate(20, 60)
]


@dataclass
class Barbell:
    lhs: List[Plate] = field(default_factory=list)
    rhs: List[Plate] = field(default_factory=list)


@dataclass
class DumbbellPair:
    db1_lhs: List[Plate] = field(default_factory=list)
    db1_rhs: List[Plate] = field(default_factory=list)
    db2_lhs: List[Plate] = field(default_factory=list)
    db2_rhs: List[Plate] = field(default_factory=list)


class GymIteration:
    def __init__(self, plate_inventory: Dict[Plate, int], barbell_cnt: int, dumbbell_cnt: int):
        self.plate_inventory = plate_inventory
        self.barbell_cnt = barbell_cnt
        self.dumbbell_cnt = dumbbell_cnt
        self.plate_stack = []
        self.barbells: List[Barbell] = []
        self.dumbbell_pairs: List[DumbbellPair] = []

    def lay_out_plates(self):
        self.plate_stack.clear()
        for plate, qty in self.plate_inventory.items():
            self.plate_stack.extend([plate] * qty)
        self.plate_stack.sort(key=lambda x: x.weight, reverse=True)

    def nth_iteration(self, iteration_number):
        self.barbells = [Barbell() for _ in range(self.barbell_cnt)]
        self.dumbbell_pairs = [DumbbellPair() for _ in range(self.dumbbell_cnt // 2)]
        self.lay_out_plates()


class GymStock:
    def balance_plates(self):
        """
        Don't attempt to fudge balances, we can accept anything that balances, strict pairing is not a requirement.
        """
        # How to order... Barbells first? Randomly until x configurations or t seconds are reached?
        gym_iteration = GymIteration(self.weight_dict, self.barbells, self.dumbbells)

    STD_DUMBBELL_THREAD_LEN = 100
    STD_BARBELL_THREAD_LEN = 300

    @staticmethod
    def check_bar_capacities(barbells_spec: List[int], dumbbells_spec: List[int]):
        if dumbbells_spec[0] % 2 != 0:
            raise ValueError("Dumbbell count ({}) must be even!".format(dumbbells_spec[0]))
        if len(barbells_spec) == 2:
            GymStock.STD_BARBELL_THREAD_LEN = barbells_spec[1]
        if len(dumbbells_spec) == 2:
            GymStock.STD_DUMBBELL_THREAD_LEN = dumbbells_spec[1]

    def __init__(self, barbells, dumbbells):
        self.barbells = int(barbells)
        self.dumbbells = int(dumbbells)
        self.weight_dict: Dict[Plate, int] = {}

    @staticmethod
    def validate_custom_weight(weight_metrics: str):
        """Ensures 3 * delimited numbers: float, int, int. (weight, thickness, quantity)"""
        x = list(map(str.strip, weight_metrics.split("*")))
        if len(x) != 3:
            raise ValueError("Custom weight requires two * seperators.")
        try:
            float(x[0])
        except ValueError:
            raise ValueError("{} is not a valid float for kg representation.".format(x[0]))
        if not x[1].isdigit():
            raise ValueError("{} is not a valid integer for mm representation.".format(x[1]))
        if not x[2].isdigit():
            raise ValueError("{} is not a valid integer for quantity representation.".format(x[2]))

    @staticmethod
    def validate_custom_bar(bar_specifier: str):
        """Accepts one or 2 integers, '*' delimited. Quantity * bearing_length(mm)"""
        x = list(map(str.strip, bar_specifier.split("*")))
        if len(x) >= 3:
            raise ValueError("Bar specifiers are either qty or qty*end_length.")
        if not x[0].isdigit():
            raise ValueError("{} is not a valid integer quantity.".format(x[0]))
        if len(x) == 1:
            return
        if not x[1].isdigit():
            raise ValueError("{} is not a valid integer for plate bearing length.".format(x[1]))

    def set_custom_weights(self, weights_metrics: List[str]) -> None:
        self.weight_dict = {}
        for weight_metrics in weights_metrics:
            self.validate_custom_weight(weight_metrics)
        self.weight_dict = {Plate(float(x[0]), int(x[1])): int(x[2]) for x in [x.split("*") for x in weights_metrics]}

    def set_weights_quantities(self, counts: List[str], plate_list: List[Plate]) -> None:
        """Stores dict of plates to their quantities observing the ordering of the
        pair of arrays passed in."""
        if not all(count.isdigit() for count in counts):
            raise ValueError("Weight counts contain illegal non-digits.")
        self.weight_dict = {x[0]: int(x[1]) for x in zip(plate_list, counts)}

    def elicit_weights(self, plate_list: List[Plate]) -> None:
        self.weight_dict = {}
        while True:
            print()
            print("(1) Use standard weights {}".format(", ".join(map(str, plate_list))))
            print("(2) Provide different weights.")
            path = input("Choose to quantify the standard weights or provide your own? ")
            if path == "1":
                self.elicit_weight_quantities(plate_list)
                break
            elif path == "2":
                print("Enter nothing to finish.")
                weight_quantities = []
                while True:
                    weight_metrics = input("weight(kg)*thickness(mm)*qty: ")
                    if weight_metrics == "":
                        break
                    try:
                        self.validate_custom_weight(weight_metrics)
                    except ValueError as ve:
                        print(ve)
                        continue
                    weight_quantities.append(weight_metrics)
                self.set_custom_weights(weight_quantities)
                break

    def elicit_weight_quantities(self, plate_list: List[Plate]):
        print("Enter nothing to finish.")
        counts = []
        for w in plate_list:
            count = self.elicit_plate_count(w)
            if count == "":
                break
            counts.append(count)
        self.set_weights_quantities(counts, plate_list)

    @staticmethod
    def elicit_plate_count(w: Plate) -> str:
        while True:
            count = input("{}*".format(w))
            if count.isdigit():
                return count
            if count == "":
                return ""
            print("{} invalid quantity, try again.".format(count))


def show_usage():
    my_name = os.path.split(sys.argv[0])[-1]
    print("This program presents configurations of your dumbbells and barbells.")
    print("This is printed as CSV.")
    print()
    print("usage: {}".format(my_name))
    print("       {} -i INVENTORY_FILE".format(my_name))
    print("       {} [BARBELLS] [DUMBBELLS]".format(my_name))
    print("       {} BARBELLS DUMBBELLS [WEIGHT*THICKNESS*QUANTITY]...".format(my_name))
    print("       {} BARBELLS DUMBBELLS ".format(my_name) +
          " [".join(["QTY_OF_{}".format(x) for x in DEFAULT_PLATES]) + "]" * len(DEFAULT_PLATES))
    print()
    print("Parameters not passed in are prompted for interactively,")
    print("which was better expressed as 4 alternative invocations.")
    print("0 arguments is the fully interactive invocation.")
    print("-i INVENTORY_FILE specifies a json file containing plate sizes and\n"
          "  optionally quantities of each and the barbells and dumbbells (which.\n"
          "  may be integers or multiplied by the plate capacity (mm) each side).\n"
          '    {"barbells": "1*350", "dumbbells": "2*120", "sizes": [\n'
          '      {"weight": 5, "thickness": 30, "quantity": 6}]}')
    print("2 arguments is interactive apart from the given BARBELLS and DUMBBELLS counts.\n"
          "Please ensure DUMBBELLS is even since this requirement helps clean the results.")
    print("Subsequent arguments must all be either integer quantities for the default \n"
          "  weight plates, or all custom plate specifiers: WEIGHT*THICKNESS*QUANTITY.")
    print("    WEIGHT is in kg and can be a float.\n"
          "    THICKNESS is in mm and must be an integer.\n"
          "    QUANTITY must be an integer.")
    raise SystemExit


def read_inventory(inventory_file: str) -> Tuple[int, int, Dict[Plate, int]]:
    """The inventory may range from a list of plate sizes, to a gym setup with quantities for everything."""
    with open(inventory_file, encoding="utf8") as f:
        inventory = json.load(f)
    barbells_spec = inventory.get("barbells", "0")
    barbells_spec = list(map(int, barbells_spec.split("*")))
    dumbbells_spec = inventory.get("dumbbells", "0")
    dumbbells_spec = list(map(int, dumbbells_spec.split("*")))
    GymStock.check_bar_capacities(barbells_spec, dumbbells_spec)
    sizes_list = inventory.get("sizes")
    weight_dict: Dict[Plate, int] = {}
    # valid_quantifiers = all("quantity" in x for x in sizes_list)
    for plate in sizes_list:
        plate_size = Plate(plate["weight"], plate["thickness"])
        weight_dict[plate_size] = plate.get("quantity", 0)
    return barbells_spec[0], dumbbells_spec[0], weight_dict


def accept_inventory_file(args: List[str]) -> Optional[GymStock]:
    for i, elem in enumerate(args[:-1]):
        if elem == "-i":
            barbells, dumbbells, weight_dict = read_inventory(args[i+1])
            if barbells == 0 and dumbbells == 0:
                gym_stock = elicit_bars()
            else:
                gym_stock = GymStock(barbells, dumbbells)
            if all([x == 0 for x in weight_dict.values()]):
                gym_stock.elicit_weights(list(weight_dict.keys()))
            else:
                gym_stock.weight_dict = weight_dict
            return gym_stock


def parse_args(args: List[str]):
    gym_stock = accept_inventory_file(args)
    if gym_stock is None:
        gym_stock = parse_cmd_line_args(args)
    gym_stock.balance_plates()


def parse_cmd_line_args(args: List[str]) -> GymStock:
    gym_stock = None
    if len(args) == 0:
        gym_stock = elicit_bars()
        gym_stock.elicit_weights(DEFAULT_PLATES)
    elif len(args) == 1 or args[0] in ["--help", "-h", "/?", "/h"]:
        show_usage()
    elif len(args) == 2:
        gym_stock = GymStock(args[0], args[1])
        gym_stock.elicit_weights(DEFAULT_PLATES)
        # ask if using standard weights 1.25, 2.5, 5...
    else:
        gym_stock = GymStock(args[0], args[1])
        if all(x.count('*') == 2 for x in args[2:]):
            try:
                gym_stock.set_custom_weights(args[2:])
            except ValueError:
                print("Only digits, decimals, and * may appear in custom weights.")
                show_usage()
        elif all('*' not in x for x in args[2:]):
            try:
                gym_stock.set_weights_quantities(args[2:], DEFAULT_PLATES)
            except ValueError:
                print("Only digits may appear in default weight counts.")
                show_usage()
        else:
            print("After the barbell and dumbell counts, either supply counts of default weights, "
                  "or custom weights and their counts.")
            show_usage()
    return gym_stock


def elicit_bars():
    barbells_spec = input_bar_specifier("barbells", GymStock.STD_BARBELL_THREAD_LEN)
    dumbbells_spec = input_bar_specifier("dumbbells", GymStock.STD_DUMBBELL_THREAD_LEN)
    GymStock.check_bar_capacities(barbells_spec, dumbbells_spec)
    return GymStock(barbells_spec[0], dumbbells_spec[0])


def input_bar_specifier(item_name: str, default_bearing_mm: int) -> List[int]:
    """Accepts pure counts using default plate bearing capacities,
    and an optional additional bearing capacity (mm) delimited by '*'. """
    while True:
        bar_specifier = input("How many {} (append '*thread_length' to change from {}mm)? ".
                              format(item_name, default_bearing_mm))
        try:
            GymStock.validate_custom_bar(bar_specifier)
            break
        except ValueError as ve:
            print(ve)
    return list(map(int, bar_specifier.split("*")))


def main():
    parse_args(sys.argv[1:])


if __name__ == "__main__":
    main()
