# -*- coding: utf-8 -*-
""" Module for the CMOArchive class, which provides additional functionality for constrained
multi-objective optimization to the MOArchive classes, while keeping the same interface. """

from moarchiving.moarchiving import BiobjectiveNondominatedSortedList as MOArchive2obj
from moarchiving.moarchiving3obj import MOArchive3obj
from moarchiving.moarchiving4obj import MOArchive4obj
from moarchiving.moarchiving_utils import true_fraction

inf = float('inf')


class CMOArchive:
    """ Class CMOArchive provides additional functionality for constrained multi-objective
    optimization to the MOArchive classes, while keeping the same interface. """
    try:
        hypervolume_final_float_type = true_fraction
        hypervolume_computation_float_type = true_fraction
    except:
        hypervolume_final_float_type = float
        hypervolume_computation_float_type = float

    def __init__(self, list_of_f_vals=None, list_of_g_vals=None, reference_point=None,
                 infos=None, ideal_point=None, weights=None, n_obj=None, tau=1, max_g_vals=None,
                 hypervolume_final_float_type=None, hypervolume_computation_float_type=None):
        """ Initialize a CMOArchive object.

        Additionally to the list of objective values `list_of_f_vals`, also list of constraint
        vectors `list_of_g_vals` should be provided.
        The reference point is used for the hypervolume computation and pruning of the archive.
        The list of additional information `infos` can be used to store additional information
        for each objective vector.

        `ideal_point` and `weights` are used for the normalization of the indicator values,
        `max_g_vals` is used for the normalization of the constraint violations.
        `tau` is a threshold that is used for calculation of hypervolume_plus_constr indicator.
        """
        hypervolume_final_float_type = CMOArchive.hypervolume_final_float_type \
            if hypervolume_final_float_type is None else hypervolume_final_float_type
        hypervolume_computation_float_type = CMOArchive.hypervolume_computation_float_type \
            if hypervolume_computation_float_type is None else hypervolume_computation_float_type

        if n_obj == 2:
            self.archive = MOArchive2obj(
                reference_point=reference_point, ideal_point=ideal_point, weights=weights,
                hypervolume_final_float_type=hypervolume_final_float_type,
                hypervolume_computation_float_type=hypervolume_computation_float_type)
        elif n_obj == 3:
            self.archive = MOArchive3obj(
                reference_point=reference_point, ideal_point=ideal_point, weights=weights,
                hypervolume_final_float_type=hypervolume_final_float_type,
                hypervolume_computation_float_type=hypervolume_computation_float_type)
        elif n_obj == 4:
            self.archive = MOArchive4obj(
                reference_point=reference_point, ideal_point=ideal_point, weights=weights,
                hypervolume_final_float_type=hypervolume_final_float_type,
                hypervolume_computation_float_type=hypervolume_computation_float_type)

        self.tau = tau
        self.n_obj = n_obj
        self._hypervolume_plus_constr = -inf

        try:
            self.max_g_vals = list(max_g_vals)
        except TypeError:
            self.max_g_vals = None if max_g_vals is None else [max_g_vals]

        if list_of_f_vals is not None:
            self.add_list(list_of_f_vals, list_of_g_vals, infos)

    def __iter__(self):
        """return an iterator over the objective vectors in the archive. """
        return iter(self.archive)

    def __len__(self):
        """return the number of objective vectors in the archive. """
        return len(self.archive)

    def add(self, f_vals, g_vals, info=None):
        """add the objective vector `f_vals` with constraints `g_vals` to the archive

        objective vector is added if the all the constraints are <= 0. Otherwise, only
        hypervolume_plus_constr indicator value is updated.

        Additionally, the information `info` are stored.

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
            g_vals = list(g_vals)
        except TypeError:
            g_vals = [g_vals]

        constraint_violation = self._get_normalized_constraint_violation(g_vals)

        if constraint_violation > 0:
            if (self.archive.reference_point is not None and
                    constraint_violation + self.tau < -self._hypervolume_plus_constr):
                self._hypervolume_plus_constr = -(constraint_violation + self.tau)
        else:
            self.archive.add(f_vals, info)

            if self.archive.reference_point is not None:
                self._hypervolume_plus_constr = max(self.archive._hypervolume_plus, -self.tau)

    def add_list(self, list_of_f_vals, list_of_g_vals, infos=None):
        """add a list of objective vectors with corresponding constraints to the archive.

        Only the objective vectors with all constraints <= 0 are added to the archive.

        Additionally, the list of `infos` are stored for objective vectors.

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
        """remove a feasible point with objective vector `f_vals` from the archive.

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
        """return the hypervolume indicator. """
        return self.archive.hypervolume

    @property
    def hypervolume_plus(self):
        """return the hypervolume_plus indicator. """
        return self.archive.hypervolume_plus

    @property
    def hypervolume_plus_constr(self):
        """return the hypervolume_plus_constr (icmop) indicator. """
        if self.archive.reference_point is None:
            raise ValueError("to compute the hypervolume_plus_constr indicator a reference"
                             " point is needed (must be given initially)")
        if self._hypervolume_plus_constr > 0:
            return self._hypervolume_plus_constr * self.archive._hv_factor
        else:
            return self._hypervolume_plus_constr

    @property
    def contributing_hypervolumes(self):
        """return the hypervolume contributions of each point in the archive. """
        return self.archive.contributing_hypervolumes

    @property
    def infos(self):
        """return the list of additional information for each point in the archive. """
        return self.archive.infos

    def compute_hypervolume(self, reference_point=None):
        """compute the hypervolume of the archive. """
        if self.n_obj == 2:
            return self.archive.compute_hypervolume(reference_point)
        return self.archive.compute_hypervolume()

    def contributing_hypervolume(self, f_vals):
        """compute the hypervolume contribution of the objective vector f_vals to the archive. """
        return self.archive.contributing_hypervolume(f_vals)

    def copy(self):
        """return a deep copy of the CMOArchive object. """
        new_cmoa = CMOArchive(reference_point=self.archive.reference_point, tau=self.tau,
                              max_g_vals=self.max_g_vals, n_obj=self.n_obj)
        new_cmoa.archive = self.archive.copy()
        new_cmoa._hypervolume_plus_constr = self._hypervolume_plus_constr
        return new_cmoa

    def distance_to_hypervolume_area(self, f_vals):
        """compute the distance of the objective vector `f_vals` to the hypervolume area. """
        return self.archive.distance_to_hypervolume_area(f_vals)

    def distance_to_pareto_front(self, f_vals, ref_factor=1):
        """compute the distance of the objective vector `f_vals` to the empirical Pareto front. """
        return self.archive.distance_to_pareto_front(f_vals, ref_factor=ref_factor)

    def dominates(self, f_vals):
        """returns True if the vector `f_vals` is dominated by any of the points in the archive. """
        return self.archive.dominates(f_vals)

    def dominators(self, f_vals, number_only=False):
        """returns a list of points in the archive that dominate the objective vector `f_vals`.

        If number_only is True, only the number of dominators is returned. """
        return self.archive.dominators(f_vals, number_only=number_only)

    def hypervolume_improvement(self, f_vals):
        """compute the hypervolume improvement of the archive if objective vector `f_vals` is added.
        """
        return self.archive.hypervolume_improvement(f_vals)

    def hypervolume_plus_constr_improvement(self, f_vals, g_vals):
        """compute the improvement of the indicator if the objective vector f_vals is added.

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
            g_vals = list(g_vals)
        except TypeError:
            g_vals = [g_vals]

        constraint_violation = self._get_normalized_constraint_violation(g_vals)

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
        """returns True if the objective vector f_vals dominates the reference point. """
        return self.archive.in_domain(f_vals, reference_point=reference_point)

    def _get_normalized_constraint_violation(self, g_vals):
        """returns the sum of normalized constraint violation of the constraint vector g_vals,

        with respect to the maximal constraint violations self.max_g_vals. If the maximal constraint
        values are not provided, it returns the sum of the positive constraint violations.
        """
        if self.max_g_vals is None:
            return sum([max(0, g) for g in g_vals])

        if len(self.max_g_vals) != len(g_vals):
            raise ValueError("list of constraint violations `g_vals` must be of same length as "
                             "list of maximal constraint violations `max_g_vals`")

        return sum([min(max(0, g) / g_max, 1) for g, g_max in zip(g_vals, self.max_g_vals)])


if __name__ == "__main__":
    import doctest
    print('doctest.testmod() in constrained_moarchive.py')
    print(doctest.testmod())
