# -*- coding: utf-8 -*-
#  Copyright (c) 2020 Kumagai group.
import os
from pathlib import Path

from monty.serialization import loadfn
from pydefect.analyzer.band_edge_states import BandEdgeStates
from pydefect.analyzer.calc_results import CalcResults
from pydefect.analyzer.grids import Grids
from pydefect.analyzer.refine_defect_structure import refine_defect_structure
from pydefect.cli.vasp.make_defect_charge_info import make_spin_charges, \
    make_defect_charge_info
from pydefect.cli.vasp.make_light_chgcar import make_light_chgcar
from pymatgen.io.vasp import Chgcar
from vise.input_set.incar import ViseIncar
from vise.util.file_transfer import FileLink
from vise.util.logger import get_logger

logger = get_logger(__name__)


def is_file(filename):
    return Path(filename).is_file() and os.stat(filename).st_size != 0


def make_parchg_dir(args):
    os.chdir(args.dir)
    if is_file("WAVECAR") is False:
        raise FileNotFoundError("WAVECAR does not exist or is empty.")

    try:
        calc_results: CalcResults = loadfn("calc_results.json")
    except FileNotFoundError:
        logger.info("Need to create calc_results.json beforehand.")
        raise
    calc_results.show_convergence_warning()

    # Increment index by 1 as VASP band index begins from 1.
    incar = ViseIncar.from_file("INCAR")
    band_edge_states = loadfn("band_edge_states.json")
    iband = [i + 1 for i in band_edge_states.band_indices_from_vbm_to_cbm]
    incar.update({"LPARD": True, "LSEPB": True, "KPAR": 1, "IBAND": iband})

    parchg = Path("parchg")
    parchg.mkdir()
    os.chdir("parchg")
    incar.write_file("INCAR")
    FileLink(Path("../WAVECAR")).transfer(Path.cwd())
    FileLink(Path("../POSCAR")).transfer(Path.cwd())
    FileLink(Path("../POTCAR")).transfer(Path.cwd())
    FileLink(Path("../KPOINTS")).transfer(Path.cwd())
    os.chdir("..")


def make_refine_defect_poscar(args):
    structure = refine_defect_structure(args.structure,
                                        args.defect_entry.anchor_atom_index,
                                        args.defect_entry.anchor_atom_coords)
    if structure:
        print(structure.to(fmt="poscar", filename=args.poscar_name))


def calc_defect_charge_info(args):
    band_idxs = []
    parchgs = []
    for parchg in args.parchgs:
        band_idx = int(parchg.split(".")[-2])
        logger.info(f"band index {band_idx} is being parsed.")
        # Use the band indices used in VASP, where it begins from 1.
        band_idxs.append(band_idx)
        p = Chgcar.from_file(parchg)
        parchgs.append(p)
        parent = Path(parchg).parent
        for spin, charge in zip(["up", "down"], make_spin_charges(p)):
            to_vesta_file = Path(f"defect_{band_idx}_{spin}.vesta")
            make_light_chgcar(charge,
                              parent / f"PARCHG_{band_idx}_{spin}",
                              vesta_file=args.vesta_file,
                              to_vesta_file=to_vesta_file)

    grids = None
    if args.grids_dirname:
        if (args.grids_dirname / "grids.npz").is_file():
            grids = Grids.from_file(args.grids_dirname / "grids.npz")
        else:
            grids = Grids.from_chgcar(parchgs[0])
            grids.dump(args.grids_dirname / "grids.npz")

    defect_charge_info = make_defect_charge_info(
        parchgs, band_idxs, args.bin_interval, grids)
    defect_charge_info.to_json_file()
    plt = defect_charge_info.show_dist()
    plt.savefig("dist.pdf")