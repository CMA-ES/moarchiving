# -*- coding: utf-8 -*-
""" Module for the CMOArchive class, which provides additional functionality for constrained
multi-objective optimization to the MOArchive classes, while keeping the same interface. """

from moarchiving.moarchiving import BiobjectiveNondominatedSortedList as MOArchive2obj
from moarchiving.moarchiving3obj import MOArchive3obj
from moarchiving.moarchiving4obj import MOArchive4obj

import warnings as _warnings
try:
    import fractions
except ImportError:
    _warnings.warn('`fractions` module not installed, arbitrary precision hypervolume computation not available')

inf = float('inf')


class CMOArchive:
    """ Class CMOArchive provides additional functionality for constrained multi-objective
    optimization to the MOArchive classes, while keeping the same interface. """
    try:
        hypervolume_final_float_type = fractions.Fraction
        hypervolume_computation_float_type = fractions.Fraction
    except:
        hypervolume_final_float_type = float
        hypervolume_computation_float_type = float

    def __init__(self, list_of_f_vals=None, list_of_g_vals=None, reference_point=None,
                 infos=None, n_obj=None, tau=1, hypervolume_final_float_type=None,
                 hypervolume_computation_float_type=None):
        """ Initialize a CMOArchive object.

        Additionally to the list of objective values `list_of_f_vals`, also list of constraint
        vectors `list_of_g_vals` should be provided.
        The reference point is used for the hypervolume computation and pruning of the archive.
        The list of additional information `infos` can be used to store additional information
        for each objective vector.
        Tau is a threshold that is used for computing the indicator.
        """
        hypervolume_final_float_type = CMOArchive.hypervolume_final_float_type \
            if hypervolume_final_float_type is None else hypervolume_final_float_type
        hypervolume_computation_float_type = CMOArchive.hypervolume_computation_float_type \
            if hypervolume_computation_float_type is None else hypervolume_computation_float_type

        if n_obj == 2:
            self.archive = MOArchive2obj(
                reference_point=reference_point,
                hypervolume_final_float_type=hypervolume_final_float_type,
                hypervolume_computation_float_type=hypervolume_computation_float_type)
        elif n_obj == 3:
            self.archive = MOArchive3obj(
                reference_point=reference_point,
                hypervolume_final_float_type=hypervolume_final_float_type,
                hypervolume_computation_float_type=hypervolume_computation_float_type)
        elif n_obj == 4:
            self.archive = MOArchive4obj(
                reference_point=reference_point,
                hypervolume_final_float_type=hypervolume_final_float_type,
                hypervolume_computation_float_type=hypervolume_computation_float_type)

        self.tau = tau
        self.n_obj = n_obj
        self._hypervolume_plus_constr = -inf

        if list_of_f_vals is not None:
            self.add_list(list_of_f_vals, list_of_g_vals, infos)

    def __iter__(self):
        """ Return an iterator over the objective vectors in the archive. """
        return iter(self.archive)

    def __len__(self):
        """ Return the number of objective vectors in the archive. """
        return len(self.archive)

    def add(self, f_vals, g_vals, info=None):
        """ Add the objective vector f_vals with corresponding constraints to the archive
        if it is feasible. If no feasible solution was found yet, also update the indicator.

        >>> from moarchiving.get_archive import get_cmo_archive
        >>> moa = get_cmo_archive(reference_point=[5, 5], tau=10)
        >>> moa.add([4, 4], 0)
        >>> list(moa)
        [[4, 4]]
        >>> moa.add([3, 4], 1)
        >>> list(moa)
        [[4, 4]]
        >>> moa.add([2, 2], 0)
        >>> list(moa)
        [[2, 2]]
        """
        try:
            constraint_violation = sum([max(0, g) for g in g_vals])
        except TypeError:
            constraint_violation = max(g_vals, 0)

        if constraint_violation > 0:
            if (self.archive.reference_point is not None and
                    constraint_violation + self.tau < -self._hypervolume_plus_constr):
                self._hypervolume_plus_constr = -(constraint_violation + self.tau)
        else:
            self.archive.add(f_vals, info)

            if self.archive.reference_point is not None:
                self._hypervolume_plus_constr = max(self.archive._hypervolume_plus, -self.tau)

    def add_list(self, list_of_f_vals, list_of_g_vals, infos=None):
        """ Add a list of objective vectors f_vals with corresponding constraints vectors g_vals
        and infos to the archive.

        >>> from moarchiving.get_archive import get_cmo_archive
        >>> moa = get_cmo_archive(reference_point=[5, 5], tau=10)
        >>> moa.add_list([[4, 4], [3, 3], [2, 2]], [0, 1, 0])
        >>> list(moa)
        [[2, 2]]
        >>> moa.add_list([[1, 6], [1, 3], [3, 0]], [[0], [0], [10]])
        >>> list(moa)
        [[1, 3], [2, 2]]
         """
        if infos is None:
            infos = [None] * len(list_of_f_vals)

        if self._hypervolume_plus_constr < 0:
            for obj, cons, info in zip(list_of_f_vals, list_of_g_vals, infos):
                self.add(obj, cons, info)
        else:
            try:
                list_of_g_vals = [sum([max(g, 0) for g in g_vals]) for g_vals in list_of_g_vals]
            except TypeError:
                list_of_g_vals = [max(g_vals, 0) for g_vals in list_of_g_vals]

            list_of_f_vals = [f_vals for f_vals, g_vals in zip(list_of_f_vals, list_of_g_vals) if g_vals == 0]
            infos = [info for info, g_vals in zip(infos, list_of_g_vals) if g_vals == 0]

            self.archive.add_list(list(list_of_f_vals), list(infos))
            self._hypervolume_plus_constr = self.archive._hypervolume_plus

    def remove(self, f_vals):
        """ Remove a feasible point with objective vector f_vals from the archive.

        >>> from moarchiving.get_archive import get_cmo_archive
        >>> moa = get_cmo_archive([[2, 3], [1, 4], [4, 1]], [0, 0, 0], reference_point=[5, 5])
        >>> list(moa)
        [[1, 4], [2, 3], [4, 1]]
        >>> moa.remove([2, 3])
        >>> list(moa)
        [[1, 4], [4, 1]]
        """
        info = self.archive.remove(f_vals)
        self._hypervolume_plus_constr = self.archive._hypervolume_plus
        return info

    @property
    def hypervolume(self):
        """ Return the hypervolume indicator. """
        return self.archive.hypervolume

    @property
    def hypervolume_plus(self):
        """ Return the hypervolume_plus indicator. """
        return self.archive.hypervolume_plus

    @property
    def hypervolume_plus_constr(self):
        """ Return the hypervolume_plus_constr (icmop) indicator. """
        if self.archive.reference_point is None:
            raise ValueError("to compute the hypervolume_plus_constr indicator a reference"
                             " point is needed (must be given initially)")
        return self._hypervolume_plus_constr

    @property
    def contributing_hypervolumes(self):
        """ Return the hypervolume contributions of each point in the archive. """
        return self.archive.contributing_hypervolumes

    @property
    def infos(self):
        """ Return the list of additional information for each point in the archive. """
        return self.archive.infos

    def compute_hypervolume(self, reference_point=None):
        """ Compute the hypervolume of the archive. """
        if self.n_obj == 2:
            return self.archive.compute_hypervolume(reference_point)
        return self.archive.compute_hypervolume()

    def contributing_hypervolume(self, f_vals):
        """ Compute the hypervolume contribution of the objective vector f_vals to the archive. """
        return self.archive.contributing_hypervolume(f_vals)

    def copy(self):
        """ Return a deep copy of the CMOArchive object. """
        new_cmoa = CMOArchive(reference_point=self.archive.reference_point, tau=self.tau)
        new_cmoa.archive = self.archive.copy()
        new_cmoa._hypervolume_plus_constr = self._hypervolume_plus_constr
        return new_cmoa

    def distance_to_hypervolume_area(self, f_vals):
        """ Compute the distance of the objective vector f_vals to the hypervolume area. """
        return self.archive.distance_to_hypervolume_area(f_vals)

    def distance_to_pareto_front(self, f_vals, ref_factor=1):
        """ Compute the distance of the objective vector f_vals to the Pareto front. """
        return self.archive.distance_to_pareto_front(f_vals, ref_factor=ref_factor)

    def dominates(self, f_vals):
        """ Returns True if the objective vector f_vals is dominated by any of the
        points in the archive. """
        return self.archive.dominates(f_vals)

    def dominators(self, f_vals, number_only=False):
        """ Returns a list of points in the archive that dominate the objective vector f_vals.
        If number_only is True, only the number of dominators is returned. """
        return self.archive.dominators(f_vals, number_only=number_only)

    def hypervolume_improvement(self, f_vals):
        """ Compute the hypervolume improvement of the archive
        if the objective vector f_vals is added. """
        return self.archive.hypervolume_improvement(f_vals)

    def hypervolume_plus_constr_improvement(self, f_vals, g_vals):
        """ Compute the improvement of the indicator if the objective vector f_vals is added.

        >>> from moarchiving.get_archive import get_cmo_archive
        >>> get_cmo_archive.hypervolume_final_float_type = float
        >>> moa = get_cmo_archive(reference_point=[5, 5], tau=4) # hv+c = -inf
        >>> moa.hypervolume_plus_constr_improvement([1, 1], 10)
        inf
        >>> moa.add([1, 1], [10, 0]) # hv+c = -14
        >>> int(moa.hypervolume_plus_constr_improvement([2, 2], 4))
        6
        >>> moa.add([2, 2], [3, 1]) # hv+c = -8
        >>> int(moa.hypervolume_plus_constr_improvement([8, 9], 0))
        4
        >>> moa.add([8, 9], [0, 0]) # hv+c = -4
        >>> int(moa.hypervolume_plus_constr_improvement([8, 5], 0))
        1
        >>> moa.add([8, 5], [0, 0]) # hv+c = -3
        >>> int(moa.hypervolume_plus_constr_improvement([0, 0], 1))
        0
        >>> moa.add([0, 0], [1, -3]) # hv+c = -3
        >>> int(moa.hypervolume_plus_constr_improvement([4, 4], 0))
        4
        >>> moa.add([4, 4], [0, 0]) # hv+c = 1
        >>> int(moa.hypervolume_plus_constr_improvement([3, 3], 0))
        3
        """
        try:
            constraint_violation = sum([max(0, g) for g in g_vals])
        except TypeError:
            constraint_violation = max(g_vals, 0)
        if constraint_violation > 0:
            if constraint_violation + self.tau < -self._hypervolume_plus_constr:
                return - self._hypervolume_plus_constr - (constraint_violation + self.tau)
            return 0

        if not self.in_domain(f_vals):
            if self._hypervolume_plus_constr > 0:
                return 0
            distance_to_hv_area = min(self.distance_to_hypervolume_area(f_vals), self.tau)
            if distance_to_hv_area < - self._hypervolume_plus_constr:
                return -self._hypervolume_plus_constr - distance_to_hv_area
            return 0

        if not self.dominates(f_vals):
            return max(-self._hypervolume_plus_constr, 0) + self.hypervolume_improvement(f_vals)
        return 0

    def in_domain(self, f_vals, reference_point=None):
        """ Returns True if the objective vector f_vals dominates the reference point. """
        return self.archive.in_domain(f_vals, reference_point=reference_point)


if __name__ == "__main__":
    import doctest
    print('doctest.testmod() in constrained_moarchive.py')
    print(doctest.testmod())
