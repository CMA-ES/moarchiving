"""Convenience create functions for any of the nondominated archives.

The appropriate number of objectives, is derived from the input arguments.
"""

from moarchiving.moarchiving import BiobjectiveNondominatedSortedList as MOArchive2obj
from moarchiving.moarchiving3obj import MOArchive3obj
from moarchiving.moarchiving4obj import MOArchive4obj
from moarchiving.constrained_moarchive import CMOArchive
from moarchiving.moarchiving_utils import true_fraction

import warnings as _warnings


def get_mo_archive(list_of_f_vals=None, reference_point=None, infos=None, ideal_point=None,
                   weights=None, n_obj=None):
    """return a nondominated archive instance with the proper number of objectives.

    `list_of_f_vals` is a list of objective vectors with `n_obj`
    objectives. If `list_of_f_vals` is not provided, `n_obj` can be
    provided to define the number of objectives which is by default 2.

    `reference_point` is used for hypervolume computation and pruning of
    the archive. A list of additional information for each objective
    vector, for example the solution from which the objective values were
    computed, can be provided in `infos`.

    `ideal_point` and weights are lists of length `n_obj` and are used for
    normalization of the hypervolume indicators.
    """
    if not hasattr(get_mo_archive, "hypervolume_final_float_type"):
        get_mo_archive.hypervolume_final_float_type = true_fraction
    if not hasattr(get_mo_archive, "hypervolume_computation_float_type"):
        get_mo_archive.hypervolume_computation_float_type = true_fraction

    if (list_of_f_vals is None or len(list_of_f_vals) == 0) and n_obj is None and reference_point is None:
        n_obj = 2

    if n_obj is None:
        if list_of_f_vals is not None and len(list_of_f_vals) > 0:
            n_obj = len(list_of_f_vals[0])
        else:
            n_obj = len(reference_point)

    # check if the number of objectives matches the number of objectives in the list of f_vals
    # and the reference point if they are provided and not empty
    if list_of_f_vals is not None and len(list_of_f_vals) > 0 and reference_point is not None:
        if len(reference_point) != len(list_of_f_vals[0]):
            raise ValueError(f"n_obj ({len(reference_point)}) does not match the number of "
                             f"objectives in the first element of list_of_f_vals "
                             f"({len(list_of_f_vals[0])})")
        elif n_obj != len(list_of_f_vals[0]):
            _warnings.warn(f"n_obj ({n_obj}) does not match the number of objectives in "
                           f"list_of_f_vals ({len(list_of_f_vals[0])})")
            n_obj = len(list_of_f_vals[0])
    elif list_of_f_vals is not None and len(list_of_f_vals) > 0:
        if n_obj != len(list_of_f_vals[0]):
            _warnings.warn(f"n_obj ({n_obj}) does not match the number of objectives in "
                           f"list_of_f_vals ({len(list_of_f_vals[0])})")
            n_obj = len(list_of_f_vals[0])
    elif reference_point is not None:
        if n_obj != len(reference_point):
            _warnings.warn(f"n_obj ({n_obj}) does not match the number of objectives in "
                           f"reference_point ({len(reference_point)})")
            n_obj = len(reference_point)

    if n_obj == 2:
        return MOArchive2obj(list_of_f_vals, reference_point=reference_point, infos=infos,
                             ideal_point=ideal_point, weights=weights,
                             hypervolume_final_float_type=get_mo_archive.hypervolume_final_float_type,
                             hypervolume_computation_float_type=get_mo_archive.hypervolume_computation_float_type)
    elif n_obj == 3:
        return MOArchive3obj(list_of_f_vals, reference_point=reference_point, infos=infos,
                             ideal_point=ideal_point, weights=weights,
                             hypervolume_final_float_type=get_mo_archive.hypervolume_final_float_type,
                             hypervolume_computation_float_type=get_mo_archive.hypervolume_computation_float_type)
    elif n_obj == 4:
        return MOArchive4obj(list_of_f_vals, reference_point=reference_point, infos=infos,
                             ideal_point=ideal_point, weights=weights,
                             hypervolume_final_float_type=get_mo_archive.hypervolume_final_float_type,
                             hypervolume_computation_float_type=get_mo_archive.hypervolume_computation_float_type)
    else:
        raise ValueError(f"Unsupported number of objectives: {n_obj}")


def get_cmo_archive(list_of_f_vals=None, list_of_g_vals=None, reference_point=None, infos=None,
                    ideal_point=None, weights=None, n_obj=None, tau=1, max_g_vals=None):
    """return a constrained nondominated archive instance with the proper number of objectives.

    `list_of_f_vals` is a list of objective vectors with `n_obj` objectives,
    `list_of_g_vals` is a list of constraint violation vectors (or values).
    If `list_of_f_vals` is not provided, `n_obj` can be provided to define
    the number of objectives.

    `reference_point` is used for the hypervolume computation and pruning of the archive.
    A list of additional information for each objective vector can be provided in `infos`.

    `ideal_point` and weights are lists of length `n_obj` and are used for
    normalization of the hypervolume indicators. `max_g_vals` is a list of
    maximum constraint violation values for each objective vector, used for
    normalization of the hypervolume_plus_constr indicator.

    `tau` is a threshold that is used for calculation of hypervolume_plus_constr indicator.
    """

    if not hasattr(get_cmo_archive, "hypervolume_final_float_type"):
        get_cmo_archive.hypervolume_final_float_type = true_fraction
    if not hasattr(get_cmo_archive, "hypervolume_computation_float_type"):
        get_cmo_archive.hypervolume_computation_float_type = true_fraction

    if (list_of_f_vals is None or len(list_of_f_vals) == 0) and n_obj is None and reference_point is None:
        n_obj = 2

    if n_obj is None:
        if list_of_f_vals is not None and len(list_of_f_vals) > 0:
            n_obj = len(list_of_f_vals[0])
        else:
            n_obj = len(reference_point)

    # check if the number of objectives matches the number of objectives in the list of f_vals
    # and the reference point if they are provided and not empty
    if list_of_f_vals is not None and len(list_of_f_vals) > 0 and reference_point is not None:
        if len(reference_point) != len(list_of_f_vals[0]):
            raise ValueError(f"n_obj ({len(reference_point)}) does not match the number of "
                             f"objectives in the first element of list_of_f_vals "
                             f"({len(list_of_f_vals[0])})")
        elif n_obj != len(list_of_f_vals[0]):
            _warnings.warn(f"n_obj ({n_obj}) does not match the number of objectives in "
                           f"list_of_f_vals ({len(list_of_f_vals[0])})")
            n_obj = len(list_of_f_vals[0])
    elif list_of_f_vals is not None and len(list_of_f_vals) > 0:
        if n_obj != len(list_of_f_vals[0]):
            _warnings.warn(f"n_obj ({n_obj}) does not match the number of objectives in "
                           f"list_of_f_vals ({len(list_of_f_vals[0])})")
            n_obj = len(list_of_f_vals[0])
    elif reference_point is not None:
        if n_obj != len(reference_point):
            _warnings.warn(f"n_obj ({n_obj}) does not match the number of objectives in "
                           f"reference_point ({len(reference_point)})")
            n_obj = len(reference_point)

    if list_of_f_vals is None and list_of_g_vals is not None:
        raise ValueError("list_of_f_vals must be provided if list_of_g_vals is provided")
    if list_of_f_vals is not None and list_of_g_vals is None:
        raise ValueError("list_of_g_vals must be provided if list_of_f_vals is provided")
    if list_of_f_vals is not None and list_of_g_vals is not None and len(list_of_f_vals) != len(list_of_g_vals):
        raise ValueError("list_of_f_vals and list_of_g_vals must have the same length")

    return CMOArchive(list_of_f_vals=list_of_f_vals, list_of_g_vals=list_of_g_vals,
                      reference_point=reference_point, infos=infos, ideal_point=ideal_point,
                      weights=weights, n_obj=n_obj, tau=tau, max_g_vals=max_g_vals,
                      hypervolume_final_float_type=get_cmo_archive.hypervolume_final_float_type,
                      hypervolume_computation_float_type=get_cmo_archive.hypervolume_computation_float_type)
