# -*- coding: utf-8 -*-
#  Copyright (c) 2020. Distributed under the terms of the MIT License.

import numpy as np
from pymatgen import IStructure, Structure
from vise.util.structure_symmetrizer import StructureSymmetrizer

from pydefect.defaults import defaults
from pydefect.util.structure_tools import Distances


class DefectStructureAnalyzer:
    def __init__(self,
                 defective_structure: IStructure,
                 perfect_structure: IStructure):
        """
        Atoms in the final structure are shifted such that the farthest atom
        from the defect is placed at the same place with that in the perfect
        supercell.
        """
        self._defective_structure = defective_structure
        self._perfect_structure = perfect_structure

    @property
    def atom_mapping(self):
        return {d: p for d, p in enumerate(self.d_to_p)
                if d not in self.inserted_indices}

    @property
    def p_to_d(self):
        result = []
        for site in self._perfect_structure:
            distances = Distances(self._defective_structure, site.frac_coords)
            result.append(distances.mapped_atom_idx(specie=site.specie))
        return result

    @property
    def d_to_p(self):
        result = []
        for site in self._defective_structure:
            distances = Distances(self._perfect_structure, site.frac_coords)
            result.append(distances.mapped_atom_idx(specie=site.specie))
        return result

    @property
    def vacancy_indices(self):
        result = []
        for p, d in enumerate(self.p_to_d):
            try:
                if self.d_to_p[d] != p:
                    result.append(p)
            except (IndexError, TypeError):
                result.append(p)
        return sorted(result)

    @property
    def inserted_indices(self):
        result = []
        for d, p in enumerate(self.d_to_p):
            try:
                if self.p_to_d[p] != d:
                    result.append(d)
            except (IndexError, TypeError):
                result.append(d)
        return sorted(result)

    @property
    def defect_center_coord(self):
        coords = []
        for v in self.vacancy_indices:
            coords.append(self._perfect_structure[v].frac_coords)
        for i in self.inserted_indices:
            coords.append(self._defective_structure[i].frac_coords)
        return np.average(coords, axis=0)

    def distance_from_center(self, index):
        frac_coords = self._defective_structure[index].frac_coords
        result, _ = self._defective_structure.lattice.get_distance_and_image(
            self.defect_center_coord, frac_coords)
        return result


def symmetrize_defect_structure(structure: IStructure,
                                anchor_atom_idx: int,
                                anchor_atom_coord) -> Structure:
    ss = StructureSymmetrizer(structure, defaults.symmetry_length_tolerance)
    result = ss.primitive.copy()
    offset = result[anchor_atom_idx].frac_coords - anchor_atom_coord
    result.translate_sites(list(range(len(structure))), offset)
    return result
