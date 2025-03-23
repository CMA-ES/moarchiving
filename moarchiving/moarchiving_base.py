# -*- coding: utf-8 -*-
"""Base class for functionality used with any number of objectives.
"""

import math
import warnings as _warnings

from moarchiving.moarchiving_utils import true_fraction

inf = float('inf')


class MOArchiveBase:
    """Provide functionality used with any number of objectives"""

    hypervolume_final_float_type = true_fraction
    """HV computation takes increasingly longer with increasing precision (number of iterations).

        Set ``BiobjectiveNondominatedSortedList.hypervolume_final_float_type = float``
        when speed is an issue.
        """ # lambda x: x is marginally faster than float
    hypervolume_computation_float_type = true_fraction
    """HV computation takes increasingly longer with increasing precision (number of iterations).

        Precision may be less relevant here than for
        `hypervolume_final_float_type`.

        Set ``BiobjectiveNondominatedSortedList.hypervolume_computation_float_type = float``
        here first when speed is an issue.
        """

    def __init__(self,
                 reference_point=None,
                 ideal_point=None,
                 weights=None,
                 n_obj=None,
                 hypervolume_final_float_type=None,
                 hypervolume_computation_float_type=None):
        """ Create a new MOArchiveBase object.

        Used for normalization and methods that are common to all MOArchive classes.
        """
        if hypervolume_final_float_type is None:
            self.hypervolume_final_float_type = MOArchiveBase.hypervolume_final_float_type
        else:
            self.hypervolume_final_float_type = hypervolume_final_float_type

        if hypervolume_computation_float_type is None:
            self.hypervolume_computation_float_type = MOArchiveBase.hypervolume_computation_float_type
        else:
            self.hypervolume_computation_float_type = hypervolume_computation_float_type

        self.n_obj = n_obj

        # set the reference point
        if reference_point is not None:
            self.reference_point = list(reference_point)
        else:
            self.reference_point = reference_point

        self._hypervolume_plus = -inf
        self._hypervolume = 0

        # set the ideal point and weights used for normalization
        self._weights = [1] * self.n_obj
        self._ideal_point = None
        self._weights_ideal_point = [1] * self.n_obj
        self._hv_factor = 1

        self.weights(weights)
        self.ideal_point(ideal_point)

    def in_domain(self, f_vals, reference_point=None):
        """return `True` if `f_vals` is dominating the reference point,

        `False` otherwise. `True` means that `f_vals` contributes to
        the hypervolume if not dominated by other elements.

        `f_vals` may also be an index in `self` in which case
        ``self[f_vals]`` is tested to be in-domain.

        >>> from moarchiving import BiobjectiveNondominatedSortedList as NDA
        >>> a = NDA([[2.2, 0.1], [0.5, 1]], reference_point=[2, 2])
        >>> assert len(a) == 1
        >>> a.in_domain([0, 0])
        True
        >>> a.in_domain([2, 1])
        False
        >>> all(a.in_domain(ai) for ai in a)
        True
        >>> a.in_domain(0)
        True
        >>> from moarchiving.get_archive import get_mo_archive
        >>> archive3obj = get_mo_archive(reference_point=[3, 3, 3])
        >>> archive3obj.in_domain([2, 2, 2])
        True
        >>> archive3obj.in_domain([0, 0, 3])
        False
        >>> archive4obj = get_mo_archive(reference_point=[3, 3, 3, 3])
        >>> archive4obj.in_domain([2, 2, 2, 2])
        True
        >>> archive4obj.in_domain([0, 0, 0, 3])
        False

        TODO: improve name?
        """
        if reference_point is None:
            reference_point = self.reference_point
        if reference_point is None:
            return True
        try:
            if self.n_obj == 2:
                f_vals = self[f_vals]
            else:
                f_vals = list(self)[f_vals]
        except TypeError:
            pass
        except IndexError:
            raise  # return None
        if any(f_vals[i] >= reference_point[i] for i in range(self.n_obj)):
            return False
        return True

    def distance_to_hypervolume_area(self, f_vals):
        """return the distance to the hypervolume area of the archive

        >>> from moarchiving.get_archive import get_mo_archive
        >>> moa = get_mo_archive(reference_point=[1, 1, 1])
        >>> moa.distance_to_hypervolume_area([1, 2, 1])
        1.0
        >>> moa.distance_to_hypervolume_area([1, 1, 1])
        0.0
        >>> moa.distance_to_hypervolume_area([0, 0, 0])
        0.0
        >>> moa.distance_to_hypervolume_area([4, 5, 1])
        5.0
        """
        if self.reference_point is None:
            return 0
        return sum([(max((0, f_vals[i] - self.reference_point[i])) *
                     self._weights_ideal_point[i] * self._weights[i]) ** 2
                    for i in range(self.n_obj)]) ** 0.5

    def weights(self, value=None):
        """return hypervolume weights, set to `value` when ``value is not None`` and return previous value

        >>> from moarchiving.get_archive import get_mo_archive
        >>> moa = get_mo_archive(reference_point=[1, 1, 1])
        >>> moa.weights([1, 2, 3])
        [1, 1, 1]
        >>> moa.weights()
        [1, 2, 3]
        """
        if value is None:
            try:
                return self._weights
            except AttributeError:
                self._weights = None
            return None
        if len(value) != self.n_obj:
            raise ValueError("{0} are not eligible weights when n_obj={1}".format(value, self.n_obj))
        value, self._weights = self._weights, value

        self._update_weights()
        return value

    def ideal_point(self, value=None):
        """return ideal point, set to `value` when ``value is not None`` and return previous value

        >>> from moarchiving.get_archive import get_mo_archive
        >>> moa = get_mo_archive(reference_point=[1, 1, 1])
        >>> moa.ideal_point([0, 0, 0])
        >>> moa.ideal_point()
        [0, 0, 0]
        """
        if value is None:
            try:
                return self._ideal_point
            except AttributeError:
                self._ideal_point = None
            return None
        if len(value) != self.n_obj:
            ValueError("{0} is not an eligible ideal point when n_obj={1}".format(value, self.n_obj))
        if self.reference_point is None:
            raise ValueError("Ideal point can't be defined without the reference point")
        if any(self.reference_point[i] <= value[i] for i in range(len(value))):
            raise ValueError("{0} is not an eligible ideal point when reference_point={1}"
                             "(it must be smaller in all objectives)".format(value, self.reference_point))

        value, self._ideal_point = self._ideal_point, value
        self._weights_ideal_point = [1 / (self.reference_point[i] - self._ideal_point[i])
                                     for i in range(self.n_obj)]
        self._update_weights()
        return value

    def _update_weights(self):
        """recalculates the hv_factor when weights or ideal point change.

        Also warns if the hypervolume_plus is not updated after changing weights or ideal point.
        """
        self._hv_factor = math.prod(self._weights) * math.prod(self._weights_ideal_point)

        if (hasattr(self, '_hypervolume_plus') and self._hypervolume_plus and
                -inf < self._hypervolume_plus < 0):
            _warnings.warn("hypervolume_plus indicator was not updated after changing "
                           "weights or ideal point")

    def _set_HV(self):
        """set current hypervolume value using `self.reference_point`.

        Also sets the hypervolume_plus indicator when hypervolume > 0.

        TODO: we may need to store the list of _contributing_ hypervolumes
        to handle numerical rounding errors later.
        """
        if self.reference_point is None:
            return None
        if self.n_obj == 2:
            self._hypervolume = self._compute_hypervolume(self.reference_point)
        else:
            self._hypervolume = self._compute_hypervolume()

        if self._hypervolume > 0:
            self._hypervolume_plus = self._hypervolume
        return self._hypervolume

    def _compute_hypervolume(self, reference_point=None):
        raise NotImplementedError("This method should be overridden in subclasses")

    def _update_hv_plus(self, list_of_f_vals):
        """updates the hypervolume plus indicator with the new list of solutions `list_of_f_vals`.

        Needed when ``hypervolume == 0``.
        """
        if self.reference_point is None:
            self._hypervolume_plus = None
            return None

        if self._hypervolume > 0:
            self._hypervolume_plus = self._hypervolume
        else:
            for f in list_of_f_vals:
                d = self.distance_to_hypervolume_area(f)
                if d < - self._hypervolume_plus:
                    self._hypervolume_plus = -d

    @staticmethod
    def _convert_and_validate_f_vals(list_of_f_vals, n_obj):
        """converts `list_of_f_vals` to a list, ensures that the inner lists have correct length
        """
        if list_of_f_vals is None or len(list_of_f_vals) == 0:
            return []

        try:
            list_of_f_vals = list_of_f_vals.tolist()
        except:
            pass
        list_of_f_vals = [list(f_vals) for f_vals in list_of_f_vals]
        if len(list_of_f_vals[0]) != n_obj:
            raise ValueError(f"need elements of length {n_obj}, got {list_of_f_vals[0]} as first element")
        return list_of_f_vals
