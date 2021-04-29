# -*- coding: utf-8 -*-
#  Copyright (c) 2020. Distributed under the terms of the MIT License.


import argparse
import sys
import warnings
from pathlib import Path

from monty.serialization import loadfn
from pydefect.cli.main import epilog, description, add_sub_parser
from pydefect.cli.vasp.main_vasp_util_functions import \
    calc_defect_charge_info, make_parchg_dir, make_refine_defect_poscar, \
    calc_charge_state
from pymatgen import Structure
from pymatgen.io.vasp.inputs import UnknownPotcarWarning

warnings.simplefilter('ignore', UnknownPotcarWarning)


def parse_args_main_vasp_util(args):
    parser = argparse.ArgumentParser(epilog=epilog,
                                     description=description + """      
    This command provides some utilities related to the VASP calculations""")

    subparsers = parser.add_subparsers()
    dir_parser = add_sub_parser(argparse, name="dir")

    # -- calc charge state -----------------------------------------------------
    parser_calc_charge_state = subparsers.add_parser(
        name="calc_charge_state",
        description="Calc defect charge states from INCAR, POSCAR and POTCAR"
                    "files.",
        parents=[dir_parser],
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        aliases=['ccs'])

    parser_calc_charge_state.set_defaults(func=calc_charge_state)

    # -- make parchg dir -----------------------------------------------
    parser_make_parchg_dir = subparsers.add_parser(
        name="parchg_dir",
        description="Make parchg dir.",
        parents=[dir_parser],
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        aliases=['pd'])

    parser_make_parchg_dir.set_defaults(func=make_parchg_dir)

    # -- make refine defect poscar ---------------------------------------------
    parser_make_refine_defect_poscar = subparsers.add_parser(
        name="refine_defect_poscar",
        description="Refine defect structure POSCAR.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        aliases=['rdp'])

    parser_make_refine_defect_poscar.add_argument(
        "-p", "--poscar", dest="structure", type=Structure.from_file)
    parser_make_refine_defect_poscar.add_argument(
        "-d", "--defect_entry", type=loadfn)
    parser_make_refine_defect_poscar.add_argument(
        "-n", "--poscar_name", type=str)
    parser_make_refine_defect_poscar.set_defaults(
        func=make_refine_defect_poscar)

    # -- calc defect charge info -----------------------------------------------
    parser_calc_def_charge_info = subparsers.add_parser(
        name="calc_defect_charge_info",
        description="Calc defect charge info.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        aliases=['cdc'])

    parser_calc_def_charge_info.add_argument(
        "-p", "--parchgs", type=str, nargs="+", required=True,
        help="PARCHG files.")
    parser_calc_def_charge_info.add_argument(
        "-v", "--vesta_file", type=Path, help="defect.vesta file")
    parser_calc_def_charge_info.add_argument(
        "-b", "--bin_interval", type=float, default=0.2)
    parser_calc_def_charge_info.add_argument(
        "-g", "--grids_dirname", type=Path)

    parser_calc_def_charge_info.set_defaults(func=calc_defect_charge_info)

    return parser.parse_args(args)


def main():
    args = parse_args_main_vasp_util(sys.argv[1:])
    args.func(args)


if __name__ == "__main__":
    main()

