""" This module contains the factory functions for creating MOArchive objects
of the appropriate dimensionality, for both constrained and unconstrained problems. """

from moarchiving.moarchiving2d import BiobjectiveNondominatedSortedList as MOArchive2d
from moarchiving.moarchiving3d import MOArchive3d
from moarchiving.moarchiving4d import MOArchive4d
from moarchiving.constrained_moarchive import CMOArchive

import warnings as _warnings
try:
    import fractions
except ImportError:
    _warnings.warn('`fractions` module not installed, arbitrary precision hypervolume computation not available')


def get_mo_archive(list_of_f_vals=None, reference_point=None, infos=None, n_obj=None):
    """
    Factory function for creating MOArchive objects of the appropriate dimensionality.

    Args:
        list_of_f_vals: list of objective vectors, can be None if n_obj is provided
        reference_point: reference point for the archive
        infos: list of additional information for each objective vector
        n_obj: must be provided if list_of_f_vals is None

    Returns:
        MOArchive object of the appropriate dimensionality, based on the number of objectives
    """
    if not hasattr(get_mo_archive, "hypervolume_final_float_type"):
        try:
            get_mo_archive.hypervolume_final_float_type = fractions.Fraction
        except:
            get_mo_archive.hypervolume_final_float_type = float
    if not hasattr(get_mo_archive, "hypervolume_computation_float_type"):
        try:
            get_mo_archive.hypervolume_computation_float_type = fractions.Fraction
        except:
            get_mo_archive.hypervolume_computation_float_type = float

    assert list_of_f_vals is not None or n_obj is not None or reference_point is not None, \
        "At least one of `list_of_f_vals`, `reference_point` or `n_obj` must be provided"

    if n_obj is None:
        if list_of_f_vals is not None and len(list_of_f_vals) > 0:
            n_obj = len(list_of_f_vals[0])
        else:
            n_obj = len(reference_point)

    if list_of_f_vals is not None and len(list_of_f_vals) > 0:
        assert len(list_of_f_vals[0]) == n_obj, \
            "The number of objectives in list_of_f_vals must match n_obj"
    if reference_point is not None:
        assert len(reference_point) == n_obj, \
            "The number of objectives in reference_point must match n_obj"

    if n_obj == 2:
        return MOArchive2d(list_of_f_vals, reference_point=reference_point, infos=infos,
                           hypervolume_final_float_type=get_mo_archive.hypervolume_final_float_type,
                           hypervolume_computation_float_type=get_mo_archive.hypervolume_computation_float_type)
    elif n_obj == 3:
        return MOArchive3d(list_of_f_vals, reference_point=reference_point, infos=infos,
                           hypervolume_final_float_type=get_mo_archive.hypervolume_final_float_type,
                           hypervolume_computation_float_type=get_mo_archive.hypervolume_computation_float_type)
    elif n_obj == 4:
        return MOArchive4d(list_of_f_vals, reference_point=reference_point, infos=infos,
                           hypervolume_final_float_type=get_mo_archive.hypervolume_final_float_type,
                           hypervolume_computation_float_type=get_mo_archive.hypervolume_computation_float_type)
    else:
        raise ValueError(f"Unsupported number of objectives: {n_obj}")


def get_cmo_archive(list_of_f_vals=None, list_of_g_vals=None, reference_point=None,
                    infos=None, n_obj=None, tau=1):
    """
    Function for creating CMOArchive objects, with similar interface as get_mo_archive.

    Args:
        list_of_f_vals: list of objective vectors, can be None if n_obj is provided
        list_of_g_vals: list of constraint vectors, must be the same length as list_of_f_vals
        reference_point: reference point for the archive
        infos: list of additional information for each objective vector
        n_obj: must be provided if list_of_f_vals is None
        tau: threshold that indicates when the indicator reaches feasibility
    Returns:
        MOArchive object of the appropriate dimensionality, based on the number of objectives
    """

    if not hasattr(get_cmo_archive, "hypervolume_final_float_type"):
        try:
            get_cmo_archive.hypervolume_final_float_type = fractions.Fraction
        except:
            get_cmo_archive.hypervolume_final_float_type = float
    if not hasattr(get_cmo_archive, "hypervolume_computation_float_type"):
        try:
            get_cmo_archive.hypervolume_computation_float_type = fractions.Fraction
        except:
            get_cmo_archive.hypervolume_computation_float_type = float

    return CMOArchive(list_of_f_vals=list_of_f_vals, list_of_g_vals=list_of_g_vals,
                      reference_point=reference_point, infos=infos, n_obj=n_obj, tau=tau,
                      hypervolume_final_float_type=get_cmo_archive.hypervolume_final_float_type,
                      hypervolume_computation_float_type=get_cmo_archive.hypervolume_computation_float_type)
