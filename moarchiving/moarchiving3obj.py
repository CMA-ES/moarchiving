# -*- coding: utf-8 -*-
"""
This module contains a MOArchiving3obj class for storing a set of non-dominated points in 3
objective space and efficiently calculating hypervolume with respect to the given reference point.
"""


from moarchiving.moarchiving import BiobjectiveNondominatedSortedList as MOArchive2obj
from moarchiving.moarchiving_utils import (DLNode, ArchiveSortedList, compute_area_simple, remove_from_z,
                                           restart_list_y, lexicographic_less, one_contribution_3_obj,
                                           weakly_dominates, strictly_dominates)
from moarchiving.moarchiving_parent import MOArchiveParent

import math
import warnings as _warnings

try:
    from sortedcontainers import SortedList
except ImportError:
    pass

try:
    import fractions
except ImportError:
    _warnings.warn('`fractions` module not installed, arbitrary precision hypervolume computation not available')

inf = float('inf')


class MOArchive3obj(MOArchiveParent):
    """ Class for storing a set of non-dominated points in 3 objective space and efficiently calculating
    hypervolume with respect to the given reference point.

    The archive is implemented as a doubly linked list, and can be modified using functions
    add and remove. Points of the archive can be accessed as a list of points order by the third
    coordinate using function points_list.

    >>> from moarchiving.get_archive import get_mo_archive
    >>> moa = get_mo_archive([[1, 2, 3], [3, 2, 1]])
    >>> list(moa) # returns the list of points in the archive sorted by the third coordinate
    [[3, 2, 1], [1, 2, 3]]
    >>> moa.add([2, 2, 2]) # add a new point to the archive
    True
    >>> moa.add([3, 3, 3])
    False
    >>> moa = get_mo_archive([[1, 2, 3], [2, 3, 4], [3, 2, 1]],
    ...                   reference_point=[4, 4, 4], infos=["A", "B", "C"])
    >>> moa.infos # returns the list of infos for each point in the archive
    ['C', 'A']
    >>> moa.hypervolume
    Fraction(10, 1)
    >>> get_mo_archive.hypervolume_final_float_type = float
    >>> get_mo_archive.hypervolume_computation_float_type = float
    >>> moa2 = get_mo_archive([[1, 2, 3], [2, 3, 4], [3, 2, 1]], reference_point=[4, 4, 4])
    >>> moa2.hypervolume
    10.0
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
        """ Create a new 3 objective archive object.

        f-vals beyond the `reference_point` are pruned away. The `reference_point` is also used
        to compute the hypervolume.
        infos are an optional list of additional information about the points in the archive.
        """

        hypervolume_final_float_type = MOArchive3obj.hypervolume_final_float_type \
            if hypervolume_final_float_type is None else hypervolume_final_float_type
        hypervolume_computation_float_type = MOArchive3obj.hypervolume_computation_float_type \
            if hypervolume_computation_float_type is None else hypervolume_computation_float_type

        super().__init__(list_of_f_vals=list_of_f_vals,
                         reference_point=reference_point,
                         infos=infos,
                         n_obj=3,
                         hypervolume_final_float_type=hypervolume_final_float_type,
                         hypervolume_computation_float_type=hypervolume_computation_float_type)

        self._removed = []
        self.preprocessing()
        hv = self._set_HV()
        self._length = len(list(self))
        if hv is not None and hv > 0:
            self._hypervolume_plus = self._hypervolume
        else:
            if list_of_f_vals is None or len(list_of_f_vals) == 0:
                self._hypervolume_plus = -inf
            else:
                self._hypervolume_plus = -min([self.distance_to_hypervolume_area(f)
                                               for f in list_of_f_vals])

    def add(self, f_vals, info=None, update_hypervolume=True):
        """ Adds a new point to the archive, and updates the hypervolume if needed.

        Returns True if the point was added, False if it was dominated
        by another point in the archive

        >>> from moarchiving.get_archive import get_mo_archive
        >>> moa = get_mo_archive(reference_point=[4, 4, 4])
        >>> moa.add([2, 3, 4])
        False
        >>> moa.add([1, 2, 3])
        True
        >>> list(moa)
        [[1, 2, 3]]
        >>> moa.add([3, 2, 1])
        True
        >>> list(moa)
        [[3, 2, 1], [1, 2, 3]]
        >>> moa.add([2, 2, 2])
        True
        >>> list(moa)
        [[3, 2, 1], [2, 2, 2], [1, 2, 3]]
        """
        if len(f_vals) != self.n_obj:
            raise ValueError(f"argument `f_vals` must be of length {self.n_obj}, was ``{f_vals}``")

        if self.reference_point is not None and self.hypervolume_plus is not None:
            dist_to_hv_area = self.distance_to_hypervolume_area(f_vals)
            if -dist_to_hv_area > self._hypervolume_plus:
                self._hypervolume_plus = -dist_to_hv_area

        # q is the current point (so that we are consistent with the paper),
        # stop is the head of the list, and first_iter is a flag to check if we are at the
        # first iteration (since the first and last points are the same)
        q = self.head
        stop = self.head
        first_iter = True

        # Add 0.0 for 3d points so that it matches the original C code and create a new node object
        if self.n_obj == 3:
            f_vals = f_vals + [0.0]
        u = DLNode(x=f_vals, info=info)
        di = self.n_obj - 1

        # loop over all the points in the archive and save the best candidates for cx and cy,
        # and check if the new point is dominated by any of the points in the archive
        dominated = False
        best_cx_candidates = None
        best_cy_candidates = None
        inserted = False
        removed = []

        while q != stop or first_iter:
            first_iter = False

            # check if the new point is dominated by the current point
            if all(q.x[i] <= u.x[i] for i in range(self.n_obj)):
                dominated = True
                break
            # check if the new point dominates the current point
            if all(u.x[i] <= q.x[i] for i in range(self.n_obj)):
                q_next = q.next[di]
                remove_from_z(q, archive_dim=self.n_obj)
                removed.append(q.x[:3])
                q = q_next
                continue

            """
            1) Set u.cx to the point q ∈ Q with the smallest q_x > u_x
            such that q_y < u_y and q <L u. If such a point is not
            unique, the alternative with the smallest q_y is preferred
            """
            if lexicographic_less(q.x, u.x) and q.x[0] > u.x[0] and q.x[1] < u.x[1]:
                if best_cx_candidates is None or q.x[0] < best_cx_candidates.x[0]:
                    best_cx_candidates = q
                elif q.x[0] == best_cx_candidates.x[0] and q.x[1] < best_cx_candidates.x[1]:
                    best_cx_candidates = q
            if lexicographic_less(q.x, u.x) and q.x[0] < u.x[0] and q.x[1] > u.x[1]:
                if best_cy_candidates is None or q.x[1] < best_cy_candidates.x[1]:
                    best_cy_candidates = q
                elif q.x[1] == best_cy_candidates.x[1] and q.x[0] < best_cy_candidates.x[0]:
                    best_cy_candidates = q

            """
            2) For q ∈ Q, set q.cx to u iff u_y < q_y and u <L q, and
            either q_x < u_x < (q.cx)_x or u_x = (q.cx)_x and u_y ≤
            (q.cx)_y.
            """
            if u.x[1] < q.x[1] and lexicographic_less(u.x, q.x):
                if (q.x[0] < u.x[0] < q.closest[0].x[0] or
                        (u.x[0] == q.closest[0].x[0] and u.x[1] <= q.closest[0].x[1])):
                    q.closest[0] = u
            if u.x[0] < q.x[0] and lexicographic_less(u.x, q.x):
                if (q.x[1] < u.x[1] < q.closest[1].x[1] or
                        (u.x[1] == q.closest[1].x[1] and u.x[0] <= q.closest[1].x[0])):
                    q.closest[1] = u
            """
            3) Insert u into Q immediately before the point q ∈ Q with
            the lexicographically smallest q such that u <L q.
            """
            # If the point is not dominated by any other point in the archive so far,
            # then it also won't be dominated by the points that come after it in the archive,
            # as the points are sorted in lexicographic order
            if lexicographic_less(u.x, q.x) and not inserted and not dominated:
                u.next[di] = q
                u.prev[di] = q.prev[di]
                q.prev[di].next[di] = u
                q.prev[di] = u
                inserted = True

            q = q.next[di]

        if not dominated:
            u.closest[0] = best_cx_candidates
            u.closest[1] = best_cy_candidates
            self._length += 1 - len(removed)

        self._removed = removed
        self._kink_points = None

        if update_hypervolume and not dominated:
            self._set_HV()

        return not dominated

    def remove(self, f_vals):
        """ Removes a point from the archive, and updates the hypervolume.
        If the point is not found, it raises a ValueError.

        Returns the info of the removed point.

        >>> from moarchiving.get_archive import get_mo_archive
        >>> moa = get_mo_archive([[1, 2, 3], [2, 2, 2], [3, 2, 1]], reference_point=[4, 4, 4],
        ...                   infos=["A", "B", "C"])
        >>> moa.remove([2, 2, 2])
        'B'
        >>> list(moa)
        [[3, 2, 1], [1, 2, 3]]
        >>> moa.remove([1, 2, 3])
        'A'
        >>> list(moa)
        [[3, 2, 1]]
        """

        di = self.n_obj - 1  # Dimension index for sorting (z-axis in 3D)
        current = self.head.next[di]
        stop = self.head.prev[di]

        # Using SortedList to manage nodes by their y-coordinate, supporting custom sorting needs
        T = SortedList(key=lambda node: (node.x[1], node.x[0]))

        # Include sentinel nodes to manage edge conditions
        T.add(self.head)  # self.head is a left sentinel
        T.add(self.head.prev[di])  # right sentinel
        remove_node = None

        while current != stop:
            if current.x[:3] == f_vals:
                remove_node = current
                current = current.next[di]
                continue
            T.add(current)

            # Remove nodes dominated by the current node
            nodes_to_remove = [node for node in T if node != current and
                               strictly_dominates(current.x, node.x, n_obj=2)]
            for node in nodes_to_remove:
                T.remove(node)

            if current.closest[0].x[:3] == f_vals:
                # For every p ∈ Q \ {u} such that p.cx = u, set p.cx to the
                #         point q ∈ Q \ {u} with the smallest q_x > p_x such that
                #         q_y < p_y and q <L p
                current.closest[1] = current.closest[1]
                cx_candidates = [node for node in T if node.x[0] > current.x[0] and node.x[1] < current.x[1]]
                if cx_candidates:
                    current.closest[0] = min(cx_candidates, key=lambda node: node.x[0])
                else:
                    current.closest[0] = self.head

            if current.closest[1].x[:3] == f_vals:
                # For every p ∈ Q \ {u} such that p.cy = u, set p.cy to the
                #         point q ∈ Q \ {u} with the smallest q_y > p_y such that
                #         q_x < p_x and q <L p
                current.closest[1] = current.closest[1]
                cy_candidates = [node for node in T if node.x[1] > current.x[1] and node.x[0] < current.x[0]]
                if cy_candidates:
                    current.closest[1] = min(cy_candidates, key=lambda node: node.x[1])
                else:
                    current.closest[1] = self.head.prev[di]

            current = current.next[di]

        if remove_node is not None:
            remove_from_z(remove_node, archive_dim=self.n_obj)
            self._kink_points = None
            self._set_HV()
            self._length -= 1
            return remove_node.info
        else:
            raise ValueError(f"Point {f_vals} not found in the archive")

    def add_list(self, list_of_f_vals, infos=None, add_method="compare"):
        """ Adds a list of points to the archive, and updates the hypervolume.

        points are added with the `add_method` method:

            - compare: compares the number of points to add with the number of points in the archive
              and uses the most efficient method based on that
            - one_by_one: adds the points one by one to the archive
            - reinit: reinitializes the archive with the new points

        >>> from moarchiving.get_archive import get_mo_archive
        >>> moa = get_mo_archive(reference_point=[4, 4, 4])
        >>> moa.add_list([[2, 3, 3], [1, 2, 3]], infos=["A", "B"])
        >>> list(moa), moa.infos
        ([[1, 2, 3]], ['B'])
        >>> moa.add_list([[3, 2, 1], [2, 2, 2], [3, 3, 3]], infos=["C", "D", "E"])
        >>> list(moa), moa.infos
        ([[3, 2, 1], [2, 2, 2], [1, 2, 3]], ['C', 'D', 'B'])
        >>> moa.add_list([[1, 1, 1]])
        >>> list(moa), moa.infos
        ([[1, 1, 1]], [None])
        """
        s = len(list_of_f_vals)
        if add_method == "compare":
            n = len(self)
            add_method = "one_by_one" if s == 1 or (n > 0 and s < math.log2(n) / 2) else "reinit"

        if infos is None:
            infos = [None] * s

        if add_method == "one_by_one":
            for f_val, info in zip(list_of_f_vals, infos):
                self.add(f_val, info=info, update_hypervolume=False)
            self._set_HV()
        elif add_method == "reinit":
            self.__init__(list(self) + list_of_f_vals, self.reference_point, self.infos + infos)
        else:
            raise ValueError(f"Unknown add method: {add_method}, "
                             f"should be one of: 'compare', 'one_by_one', 'reinit'")

    def copy(self):
        """ Returns a copy of the archive

        >>> from moarchiving.get_archive import get_mo_archive
        >>> moa = get_mo_archive([[1, 2, 3], [2, 2, 2], [3, 2, 1]], reference_point=[4, 4, 4],
        ...                   infos=["A", "B", "C"])
        >>> moa2 = moa.copy()
        >>> list(moa2), moa2.infos
        ([[3, 2, 1], [2, 2, 2], [1, 2, 3]], ['C', 'B', 'A'])
        >>> moa.remove([2, 2, 2])
        'B'
        >>> moa2.add([1.5, 1.5, 1.5], "D")
        True
        >>> list(moa2), moa2.infos
        ([[3, 2, 1], [1.5, 1.5, 1.5], [1, 2, 3]], ['C', 'D', 'A'])
        >>> list(moa), moa.infos
        ([[3, 2, 1], [1, 2, 3]], ['C', 'A'])
        """
        return MOArchive3obj(list(self), self.reference_point, self.infos)

    def _get_kink_points(self):
        """ Function that returns the kink points of the archive.

        Kink point are calculated by making a sweep of the archive, where the state is one
        2 objective archive of all possible kink points found so far, and another 2 objective
        archive which stores the non-dominated points so far in the sweep

        >>> from moarchiving.get_archive import get_mo_archive
        >>> moa = get_mo_archive([[1, 2, 3], [2, 2, 2], [3, 2, 1]], reference_point=[4, 4, 4])
        >>> moa._get_kink_points()
        [[4, 4, 1], [3, 4, 2], [2, 4, 3], [1, 4, 4], [4, 2, 4]]
         """
        if self.reference_point is None:
            ref_point = [inf] * self.n_obj
        else:
            ref_point = self.reference_point

        # initialize the two states, one for points and another for kink points
        points_state = MOArchive2obj([[ref_point[0], -inf], [-inf, ref_point[1]]])
        kink_candidates = MOArchive2obj([ref_point[:2]])
        # initialize the point dictionary, which will store the third coordinate of the points
        point_dict = {
            tuple(ref_point[:2]): -inf
        }
        kink_points = []

        for point in self:
            # add the point to the kink state to get the dominated kink points, then take it out
            if kink_candidates.add(point[:2]) is not None:
                removed = kink_candidates._removed.copy()
                for removed_point in removed:
                    z = point_dict[tuple(removed_point)]
                    if z < point[2] and point[0] < removed_point[0] and point[1] < removed_point[1]:
                        kink_points.append([removed_point[0], removed_point[1], point[2]])
                kink_candidates._removed.clear()
                kink_candidates.remove(point[:2])

            # add the point to the point state, and get two new kink point candidates
            idx = points_state.add(point[:2])
            for i in range(2):
                p = [points_state[idx + i][0], points_state[idx - 1 + i][1]]
                point_dict[tuple(p)] = point[2]
                kink_candidates.add(p)

        # add all the remaining kink points to the list
        for point in kink_candidates:
            kink_points.append([point[0], point[1], ref_point[2]])

        return kink_points

    def hypervolume_improvement(self, f_vals):
        """ Returns the hypervolume improvement of adding a point to the archive

        >>> from moarchiving.get_archive import get_mo_archive
        >>> moa = get_mo_archive([[1, 2, 3], [3, 2, 1]], reference_point=[4, 4, 4])
        >>> moa.hypervolume_improvement([2, 2, 2])
        2.0
        >>> moa.hypervolume_improvement([3, 3, 4])
        -1.0
        """
        if f_vals in self:
            return 0
        if self.dominates(f_vals):
            return -1 * self.distance_to_pareto_front(f_vals)

        return one_contribution_3_obj(self.head, DLNode(x=f_vals),
                                      self.hypervolume_computation_float_type)

    def compute_hypervolume(self, reference_point=None):
        """ Compute the hypervolume of the current state of archive

        >>> from moarchiving.get_archive import get_mo_archive
        >>> moa = get_mo_archive([[1, 2, 3], [3, 2, 1]], reference_point=[4, 4, 4])
        >>> moa.compute_hypervolume()
        10.0
        """
        if reference_point is not None:
            _warnings.warn("Reference point given at the initialization is used")

        Fc = self.hypervolume_computation_float_type
        p = self.head
        area = Fc(0)
        volume = Fc(0)

        restart_list_y(self.head)
        p = p.next[2].next[2]
        stop = self.head.prev[2]

        while p != stop:
            if p.ndomr < 1:
                p.cnext[0] = p.closest[0]
                p.cnext[1] = p.closest[1]

                area += compute_area_simple(p.x, 1, p.cnext[0], p.cnext[0].cnext[1], Fc)

                p.cnext[0].cnext[1] = p
                p.cnext[1].cnext[0] = p
            else:
                remove_from_z(p, archive_dim=self.n_obj)

            volume += area * (Fc(p.next[2].x[2]) - Fc(p.x[2]))
            p = p.next[2]

        return self.hypervolume_final_float_type(volume)

    def preprocessing(self):
        """ Preprocessing step to determine the closest points in x and y directions,
        as described in the paper and implemented in the original C code. """
        di = self.n_obj - 1
        t = ArchiveSortedList(iterable=[self.head, self.head.next[di]],
                              key=lambda node: (node.x[1], node.x[0]))

        p = self.head.next[di].next[di]
        stop = self.head.prev[di]

        while p != stop:
            s = t.outer_delimiter_x(p)
            if weakly_dominates(s.x, p.x, self.n_obj) or weakly_dominates(t.next_y(s).x, p.x, self.n_obj):
                p.ndomr = 1
                p = p.next[di]
                continue

            t.remove_dominated_y(p, s)
            p.closest[0] = s
            p.closest[1] = t.next_y(s)
            t.add_y(p, s)
            p = p.next[di]

        t.clear()


if __name__ == "__main__":
    import doctest
    print('doctest.testmod() in moarchiving3obj.py')
    print(doctest.testmod())
