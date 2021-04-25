# -*- coding: utf-8 -*-
#  Copyright (c) 2020. Distributed under the terms of the MIT License.
from argparse import Namespace
from pathlib import Path

from pydefect.analyzer.calc_results import CalcResults
from pydefect.cli.vasp.main_vasp import parse_args_main_vasp
from pydefect.defaults import defaults


def test_unitcell(mocker):
    mock = mocker.patch("pydefect.cli.vasp.main_vasp.Vasprun")
    mock_outcar = mocker.patch("pydefect.cli.vasp.main_vasp.Outcar")

    parsed_args = parse_args_main_vasp(["u",
                                        "-vb", "vasprun.xml",
                                        "-ob", "OUTCAR-1",
                                        "-odc", "OUTCAR-2",
                                        "-odi", "OUTCAR-3",
                                        "-n", "name"])
    # func is a pointer so need to point the same address.
    expected = Namespace(
        vasprun_band=mock.return_value,
        outcar_band=mock_outcar.return_value,
        outcar_dielectric_clamped=mock_outcar.return_value,
        outcar_dielectric_ionic=mock_outcar.return_value,
        name="name",
        func=parsed_args.func,
    )
    assert parsed_args == expected
    mock.assert_called_once_with("vasprun.xml")
    mock_outcar.assert_any_call("OUTCAR-1")
    mock_outcar.assert_any_call("OUTCAR-2")
    mock_outcar.assert_called_with("OUTCAR-3")


def test_make_poscars_wo_options():
    parsed_args = parse_args_main_vasp(["mp", "-e", "Mg", "O"])
    expected = Namespace(
        elements=["Mg", "O"],
        e_above_hull=defaults.e_above_hull,
        func=parsed_args.func)
    assert parsed_args == expected


def test_make_poscars_w_options():
    parsed_args = parse_args_main_vasp([
        "mp", "-e", "Mg", "O", "--e_above_hull", "0.1"])
    expected = Namespace(
        elements=["Mg", "O"],
        e_above_hull=0.1,
        func=parsed_args.func)
    assert parsed_args == expected


def test_defect_entries():
    parsed_args = parse_args_main_vasp(["de"])
    expected = Namespace(func=parsed_args.func)
    assert parsed_args == expected


def test_calc_results():
    parsed_args = parse_args_main_vasp(["cr", "-d", "Va_O1_0", "Va_O1_1"])
    expected = Namespace(
        dirs=[Path("Va_O1_0"), Path("Va_O1_1")],
        func=parsed_args.func,
    )
    assert parsed_args == expected


def test_band_edge_orbital_infos(mocker):
    mock_calc_results = mocker.Mock(spec=CalcResults, autospec=True)

    def side_effect(filename):
        if filename == "perfect/calc_results.json":
            return mock_calc_results
        else:
            raise ValueError

    mocker.patch("pydefect.cli.vasp.main_vasp.loadfn", side_effect=side_effect)
    parsed_args = parse_args_main_vasp(["beoi", "-d", "Va_O1_0", "Va_O1_1",
                                        "-pcr", "perfect/calc_results.json"])
    expected = Namespace(
        dirs=[Path("Va_O1_0"), Path("Va_O1_1")],
        perfect_calc_results=mock_calc_results,
        func=parsed_args.func)
    assert parsed_args == expected


def test_perfect_band_edge_state():
    parsed_args = parse_args_main_vasp(["pbes", "-d", "Va_O1_0"])
    expected = Namespace(
        dir=Path("Va_O1_0"),
        func=parsed_args.func)
    assert parsed_args == expected

