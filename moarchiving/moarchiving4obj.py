# -*- coding: utf-8 -*-
"""
This module contains a MOArchiving4obj class for storing a set of non-dominated points in 4
objective space and calculating hypervolume with respect to the given reference point.
"""


from moarchiving.moarchiving_utils import hv4dplusR, remove_from_z
from moarchiving.moarchiving3obj import MOArchive3obj
from moarchiving.moarchiving_parent import MOArchiveParent

import warnings as _warnings

try:
    import fractions
except ImportError:
    _warnings.warn('`fractions` module not installed, arbitrary precision hypervolume computation not available')


inf = float('inf')


class MOArchive4obj(MOArchiveParent):
    """ Class for storing a set of non-dominated points in 4 objective space and calculating
    hypervolume with respect to the given reference point.

    The archive is implemented as a doubly linked list, and can be modified using functions
    add and remove. Points of the archive can be accessed as a list of points order by the fourth
    coordinate using function points_list.
    >>> from moarchiving.get_archive import get_mo_archive
    >>> moa = get_mo_archive([[1, 2, 3, 4], [4, 3, 2, 1]])
    >>> list(moa) # returns the list of points in the archive sorted by the third coordinate
    [[4, 3, 2, 1], [1, 2, 3, 4]]
    >>> moa.add([2, 2, 2, 2]) # add a new point to the archive
    True
    >>> moa.add([3, 3, 3, 3])
    False
    >>> get_mo_archive.hypervolume_final_float_type = fractions.Fraction
    >>> moa = get_mo_archive([[1, 2, 3, 4], [2, 3, 4, 5], [4, 3, 2, 1]],
    ...                   reference_point=[5, 5, 5, 5], infos=["A", "B", "C"])
    >>> moa.infos # returns the list of infos for each point in the archive
    ['C', 'A']
    >>> moa.hypervolume
    Fraction(44, 1)
    >>> get_mo_archive.hypervolume_final_float_type = float
    >>> get_mo_archive.hypervolume_computation_float_type = float
    >>> moa2 = get_mo_archive([[1, 2, 3, 4], [2, 3, 4, 5], [4, 3, 2, 1]],
    ...                    reference_point=[5, 5, 5, 5])
    >>> moa2.hypervolume
    44.0

    """
    try:
        hypervolume_final_float_type = fractions.Fraction
        hypervolume_computation_float_type = fractions.Fraction
    except:
        hypervolume_final_float_type = float
        hypervolume_computation_float_type = float

    def __init__(self, list_of_f_vals=None, reference_point=None, infos=None,
                 hypervolume_final_float_type=None,
                 hypervolume_computation_float_type=None):
        """ Create a new 4 objective archive object.

        f-vals beyond the `reference_point` are pruned away. The `reference_point` is also used
        to compute the hypervolume.
        infos are an optional list of additional information about the points in the archive.
        """

        hypervolume_final_float_type = MOArchive4obj.hypervolume_final_float_type \
            if hypervolume_final_float_type is None else hypervolume_final_float_type
        hypervolume_computation_float_type = MOArchive4obj.hypervolume_computation_float_type \
            if hypervolume_computation_float_type is None else hypervolume_computation_float_type

        super().__init__(list_of_f_vals=list_of_f_vals,
                         reference_point=reference_point,
                         infos=infos,
                         n_obj=4,
                         hypervolume_final_float_type=hypervolume_final_float_type,
                         hypervolume_computation_float_type=hypervolume_computation_float_type)

        self._hypervolume_already_computed = False
        self.remove_dominated()
        hv = self._set_HV()
        self._length = len(list(self))
        self._hypervolume_already_computed = True
        if hv is not None and hv > 0:
            self._hypervolume_plus = self._hypervolume
        else:
            if list_of_f_vals is None or len(list_of_f_vals) == 0:
                self._hypervolume_plus = -inf
            else:
                self._hypervolume_plus = -min([self.distance_to_hypervolume_area(f)
                                               for f in list_of_f_vals])

    def add(self, f_vals, info=None, update_hypervolume=True):
        """ Add a new point to the archive.

        update_hypervolume should be set to True, unless adding multiple points at once,
        in which case it is slightly more efficient to set it to True only for last point

        >>> from moarchiving.get_archive import get_mo_archive
        >>> moa = get_mo_archive(reference_point=[5, 5, 5, 5])
        >>> moa.add([2, 3, 4, 5])
        False
        >>> moa.add([1, 2, 3, 4])
        True
        >>> list(moa)
        [[1, 2, 3, 4]]
        >>> moa.add([4, 3, 2, 1])
        True
        >>> list(moa)
        [[4, 3, 2, 1], [1, 2, 3, 4]]
        >>> moa.add([2, 2, 2, 2])
        True
        >>> list(moa)
        [[4, 3, 2, 1], [2, 2, 2, 2], [1, 2, 3, 4]]
        """
        if len(f_vals) != self.n_obj:
            raise ValueError(f"argument `f_pair` must be of length {self.n_obj}, was ``{f_vals}``")

        if self.dominates(f_vals):
            return False

        if not self.in_domain(f_vals):
            dist_to_hv_area = self.distance_to_hypervolume_area(f_vals)
            if -dist_to_hv_area > self._hypervolume_plus:
                self._hypervolume_plus = -dist_to_hv_area
            return False

        self.__init__(list(self) + [f_vals], self.reference_point, self.infos + [info])
        return True

    def remove(self, f_vals):
        """ Remove a point from the archive.

        Returns False if the point is not in the archive and it's Info if the point is removed

        >>> from moarchiving.get_archive import get_mo_archive
        >>> moa = get_mo_archive([[1, 2, 3, 4], [2, 2, 2, 2], [4, 3, 2, 1]],
        ...                   reference_point=[5, 5, 5, 5], infos=["A", "B", "C"])
        >>> moa.remove([2, 2, 2, 2])
        'B'
        >>> list(moa)
        [[4, 3, 2, 1], [1, 2, 3, 4]]
        >>> moa.remove([1, 2, 3, 4])
        'A'
        >>> list(moa)
        [[4, 3, 2, 1]]
        """
        points_list = list(self)
        if f_vals not in points_list:
            return False
        point_idx = points_list.index(f_vals)
        point_info = self.infos[point_idx]
        self.__init__([p for p in points_list if p != f_vals], self.reference_point,
                      [info for p, info in zip(points_list, self.infos) if p != f_vals])
        return point_info

    def add_list(self, list_of_f_vals, infos=None):
        """ Add a list of points to the archive.

        >>> from moarchiving.get_archive import get_mo_archive
        >>> moa = get_mo_archive(reference_point=[5, 5, 5, 5])
        >>> moa.add_list([[1, 2, 4, 4], [1, 2, 3, 4]], infos=["A", "B"])
        >>> list(moa), moa.infos
        ([[1, 2, 3, 4]], ['B'])
        >>> moa.add_list([[4, 3, 2, 1], [2, 2, 2, 2], [3, 3, 3, 3]], infos=["C", "D", "E"])
        >>> list(moa), moa.infos
        ([[4, 3, 2, 1], [2, 2, 2, 2], [1, 2, 3, 4]], ['C', 'D', 'B'])
        >>> moa.add_list([[1, 1, 1, 1]])
        >>> list(moa), moa.infos
        ([[1, 1, 1, 1]], [None])
        """
        if infos is None:
            infos = [None] * len(list_of_f_vals)

        self.__init__(list(self) + list_of_f_vals, self.reference_point, self.infos + infos)

    def copy(self):
        """ Return a copy of the archive.

        >>> from moarchiving.get_archive import get_mo_archive
        >>> moa = get_mo_archive([[1, 2, 3, 4], [2, 2, 2, 2], [4, 3, 2, 1]],
        ...                   reference_point=[5, 5, 5, 5], infos=["A", "B", "C"])
        >>> moa2 = moa.copy()
        >>> list(moa2), moa2.infos
        ([[4, 3, 2, 1], [2, 2, 2, 2], [1, 2, 3, 4]], ['C', 'B', 'A'])
        >>> moa.remove([2, 2, 2, 2])
        'B'
        >>> moa2.add([0, 1, 3, 1.5], "D")
        True
        >>> list(moa2), moa2.infos
        ([[4, 3, 2, 1], [0, 1, 3, 1.5], [2, 2, 2, 2]], ['C', 'D', 'B'])
        >>> list(moa), moa.infos
        ([[4, 3, 2, 1], [1, 2, 3, 4]], ['C', 'A'])
        """
        return MOArchive4obj(list(self), self.reference_point, self.infos)

    def _get_kink_points(self):
        """ Function that returns the kink points of the archive.

        Kink point are calculated by making a sweep of the archive, where the state is one
        3 objective archive of all possible kink points found so far, and another 3 objective
        archive which stores the non-dominated points so far in the sweep

        >>> from moarchiving.get_archive import get_mo_archive
        >>> moa = get_mo_archive([[1, 2, 3, 4], [4, 3, 2, 1]], reference_point=[5, 5, 5, 5])
        >>> moa._get_kink_points()
        [[5, 5, 5, 1], [5, 3, 5, 4], [4, 5, 5, 4], [5, 5, 2, 5], [5, 3, 3, 5], [4, 5, 3, 5], [5, 2, 5, 5], [1, 5, 5, 5]]
         """
        if self.reference_point is None:
            max_point = max([max([point[i] for point in self]) for i in range(3)]) + 1
            ref_point = [max_point] * self.n_obj
        else:
            ref_point = self.reference_point

        # initialize the two states, one for points and another for kink points
        points_state = MOArchive3obj(reference_point=ref_point[:3])
        kink_candidates = MOArchive3obj([ref_point[:3]],
                                        reference_point=[r + 1 for r in ref_point[:3]])
        # initialize the point dictionary, which will store the fourth coordinate of the points
        point_dict = {
            tuple(ref_point[:3]): -inf
        }
        kink_points = []

        for point in self:
            # add the point to the kink state to get the dominated kink points, then take it out
            if kink_candidates.add(point[:3]):
                removed = kink_candidates._removed.copy()
                for removed_point in removed:
                    w = point_dict[tuple(removed_point)]
                    if w < point[3]:
                        kink_points.append([removed_point[0], removed_point[1], removed_point[2],
                                            point[3]])
                kink_candidates._removed.clear()
                kink_candidates.remove(point[:3])

            # add the point to the point state, and get two new kink point candidates
            points_state.add(point[:3])
            new_kink_candidates = points_state._get_kink_points()
            new_kink_candidates = [p for p in new_kink_candidates if
                                   (p[0] == point[0] or p[1] == point[1] or p[2] == point[2])]
            for p in new_kink_candidates:
                point_dict[tuple(p)] = point[3]
                kink_candidates.add(p)

        for point in kink_candidates:
            kink_points.append([point[0], point[1], point[2], ref_point[3]])

        return kink_points

    def hypervolume_improvement(self, f_vals):
        """ Returns the hypervolume improvement of adding a point to the archive

        >>> from moarchiving.get_archive import get_mo_archive
        >>> moa = get_mo_archive([[1, 2, 3, 4], [4, 3, 2, 1]], reference_point=[5, 5, 5, 5])
        >>> moa.hypervolume_improvement([2, 2, 2, 2])
        49.0
        >>> moa.hypervolume_improvement([3, 3, 4, 5])
        -1.0
        """
        if f_vals in list(self):
            return 0
        if self.dominates(f_vals):
            return -1 * self.distance_to_pareto_front(f_vals)

        moa_copy = self.copy()
        moa_copy.add(f_vals)
        return self.hypervolume_final_float_type(moa_copy.hypervolume - self.hypervolume)

    def compute_hypervolume(self, reference_point=None):
        """ Compute the hypervolume of the archive.

        >>> from moarchiving.get_archive import get_mo_archive
        >>> moa = get_mo_archive([[1, 2, 3, 4], [4, 3, 2, 1]], reference_point=[5, 5, 5, 5])
        >>> moa.compute_hypervolume()
        44.0
        """
        if reference_point is not None:
            _warnings.warn("Reference point given at the initialization is used "
                           "in 3 objective hypervolume computation")

        if self._hypervolume_already_computed:
            return self._hypervolume
        return self.hypervolume_final_float_type(
            hv4dplusR(self.head, self.hypervolume_computation_float_type))

    def remove_dominated(self):
        """ Preprocessing step to remove dominated points. """
        di = self.n_obj - 1
        current = self.head.next[di]
        stop = self.head.prev[di]

        non_dominated_points = []
        dominated_points = []

        while current != stop:
            dominated = False
            for node in non_dominated_points:
                if node != current and all(node.x[i] <= current.x[i] for i in range(3)) and any(
                        node.x[i] < current.x[i] for i in range(3)):
                    dominated = True
                    break
            if dominated:
                dominated_points.append(current)
            else:
                non_dominated_points.append(current)
            current = current.next[di]

        for point in dominated_points:
            remove_from_z(point, archive_dim=self.n_obj)


if __name__ == "__main__":
    import doctest
    print('doctest.testmod() in moarchiving4obj.py')
    print(doctest.testmod())
