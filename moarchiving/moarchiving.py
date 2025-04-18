# -*- coding: utf-8 -*-
"""A bi-objective nondominated archive,

implemented as sorted list and with incremental update in logarithmic time.
"""
from __future__ import division, print_function, unicode_literals
import warnings as _warnings
# from collections import deque  # does not support deletion of slices!?
import bisect as _bisect # to find the insertion index efficiently
try:
    import fractions
except ImportError:
    _warnings.warn(
    '`fractions` module not installed, arbitrary precision hypervolume computation not available')
del division, print_function, unicode_literals

inf = float('inf')


def _debug_trace(*args, **kwargs):
    """return a string like printing the calling trace stack"""
    try:
        import traceback
    except:
        s = ''
    else:
        s = ''.join(traceback.format_stack(*args, **kwargs))
    return s


def true_fraction(val, copy=False):
    """return a `fractions.Fraction` object from `val`.

    Fixes the issue that `Fraction` does not convert an `np.intc` or
    `np.int32` type to infinite representation `int`.
    """
    try:
        fractions.Fraction
    except NameError:
        return val
    if isinstance(val, fractions.Fraction):
        if copy:  # Fraction(.) is almost 20 times slower than float(.)
            return fractions.Fraction(val)
        return val
    if not isinstance(val, (int, float)):
        val = float(val)
    return fractions.Fraction(val)


class BiobjectiveNondominatedSortedList(list):
    """A sorted list of non-dominated unique objective-pairs.

    Non-domination here means smaller in at least one objective. The list is
    sorted (naturally) by the first objective. No equal entries in either
    objective exist in the list (assuming it is in a consistent state).

    The operation

    >>> from moarchiving import BiobjectiveNondominatedSortedList
    >>> any_list = BiobjectiveNondominatedSortedList(any_list)  # doctest:+SKIP

    sorts and prunes the pair list `any_list` to become a consistent
    nondominated sorted archive.

    Afterwards, the methods `add` and `add_list` keep the list always
    in a consistent state. If a reference point was given on initialization,
    also the hypervolume of the archive is computed and updated.

    The `contributing_hypervolume` and `hypervolume_improvement` methods
    give the uncrowded hypervolume improvement, with or without removing
    the input from the archive before the computation, respectively, see
    https://arxiv.org/abs/1904.08823

    Removing elements with `pop` or `del` keeps the archive sorted and
    non-dominated but does not update the hypervolume, which hence
    becomes inconsistent.

    >>> a = BiobjectiveNondominatedSortedList([[1,0.9], [0,1], [0,2]])
    >>> a
    [[0, 1], [1, 0.9]]
    >>> a.add([0, 1])  # doesn't change anything, [0, 1] is not duplicated
    >>> BiobjectiveNondominatedSortedList(
    ...     [[-0.749, -1.188], [-0.557, 1.1076],
    ...     [0.2454, 0.4724], [-1.146, -0.110]])
    [[-1.146, -0.11], [-0.749, -1.188]]
    >>> a._asserts()  # consistency assertions

    Details: This list doesn't prevent the user to insert a new element
    anywhere and hence get into an inconsistent state. Inheriting from
    `sortedcontainers.SortedList` would ensure that the `list` remains
    at least sorted.

    See also:
    https://pypi.org/project/sortedcontainers
    https://code.activestate.com/recipes/577197-sortedcollection/
    https://pythontips.com/2016/04/24/python-sorted-collections/

"""
    # DONE: implement large-precision hypervolume computation.
    # DONE (method remove): implement a `delete` method that also updates the hypervolume.
    # TODO (DONE): implement a copy method
    # TODO: compute a hypervolume also without a reference point. Using the
    # two extreme points as reference should just work fine also for
    # hypervolume improvement, as making them more extreme improves
    # the volume. This is not equivalent with putting the reference
    # to infty, as the contribution from a new extreme could be small.
    # TODO (discarded): currently, points beyond the reference point (which do not contribute
    # to the hypervolume) are discarded. We may want to keep them, for simplicity
    # in a separate list?

    # Default Values for meta control attributes
    make_expensive_asserts = False

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

    maintain_contributing_hypervolumes = False

    def __init__(self,
                 list_of_f_pairs=None,
                 reference_point=None,
                 sort=sorted,
                 infos=None,
                 hypervolume_final_float_type=None,
                 hypervolume_computation_float_type=None):
        """`list_of_f_pairs` does not need to be sorted.

        f-pairs beyond the `reference_point` are pruned away. The
        `reference_point` is also used to compute the hypervolume.

        `sort` is a sorting function and ``sort=None`` will prevent a sort,
        which can be useful if the `list_of_f_pairs` is already sorted.

        CAVEAT: the interface, in particular the positional interface
        may change in future versions.
        """
        if hypervolume_final_float_type is None:
            self.hypervolume_final_float_type = BiobjectiveNondominatedSortedList.hypervolume_final_float_type
        else:
            self.hypervolume_final_float_type = hypervolume_final_float_type

        if hypervolume_computation_float_type is None:
            self.hypervolume_computation_float_type = BiobjectiveNondominatedSortedList.hypervolume_computation_float_type
        else:
            self.hypervolume_computation_float_type = hypervolume_computation_float_type

        self.make_expensive_asserts = BiobjectiveNondominatedSortedList.make_expensive_asserts
        self.maintain_contributing_hypervolumes = BiobjectiveNondominatedSortedList.maintain_contributing_hypervolumes
        self.n_obj = 2

        if list_of_f_pairs is not None and len(list_of_f_pairs):
            try:
                list_of_f_pairs = list_of_f_pairs.tolist()
            except:
                pass
            if len(list_of_f_pairs[0]) != 2:
                raise ValueError("need elements of len 2, got %s"
                                 " as first element" % str(list_of_f_pairs[0]))
            if sort is None:
                list.__init__(self, list_of_f_pairs)
            else:
                if infos is not None:
                    f_pair2info = dict(zip([tuple(f_pair) for f_pair in list_of_f_pairs], infos))
                    list.__init__(self, sort(list_of_f_pairs))
                    infos = [f_pair2info[tuple(f_pair)] for f_pair in self]
                else:
                    list.__init__(self, sort(list_of_f_pairs))

            # super(BiobjectiveNondominatedSortedList, self).__init__(sort(list_of_f_pairs))
        if reference_point is not None:
            self.reference_point = list(reference_point)
        else:
            self.reference_point = reference_point

        if infos is not None:
            if len(infos) != len(list_of_f_pairs):
                raise ValueError(f"need as many infos as f_pairs, got "
                                 f"{len(infos)} infos and {len(list_of_f_pairs)} f_pairs")
            self._infos = infos
        else:
            self._infos = None

        self.prune()  # remove dominated entries, uses in_domain, hence ref-point
        if self.maintain_contributing_hypervolumes:
            self._contributing_hypervolumes = self.contributing_hypervolumes
            raise NotImplementedError('update of _contributing_hypervolumes in _add_HV and _subtract_HV not implemented')
        else:
            self._contributing_hypervolumes = []
        self._set_HV()

        if reference_point is not None:
            if self._hypervolume > 0:
                self._hypervolume_plus = self._hypervolume
            else:
                if list_of_f_pairs is None or len(list_of_f_pairs) == 0:
                    self._hypervolume_plus = -inf
                else:
                    self._hypervolume_plus = -min([self.distance_to_hypervolume_area(f)
                                                   for f in list_of_f_pairs])
        else:
            self._hypervolume_plus = None
        self.make_expensive_asserts and self._asserts()

    def _debug_info(self):
        """return debug info as a list of (key, value) tuples"""
        def cut_list(l, n=100):
            n2 = int(n/2) - 2
            try:
                if len(l) > n:
                    return l[:n2] + ['...'] + [l[int(len(l) / 2)]] + ['...'] + l[-n2:]
            except:
                pass
            return l
        return [('len', len(self)),
                ('attributes', dict((k, cut_list(v)) for k, v in self.__dict__.items())),
                ('self', cut_list(self)),
               ]

    def add(self, f_pair, info=None):
        """insert `f_pair` in `self` if it is not (weakly) dominated.

        Return index at which the insertion took place or `None`. The
        list remains sorted in the process.

        The list remains non-dominated with unique elements, which
        means that some or many or even all of its present elements may
        be removed.

        `info` is added to the `infos` `list`. It can be an arbitrary object,
        e.g. a list or dictionary. It can in particular contain (or be) the
        solution ``x`` such that ``f_pair == fun(info['x'])``.

        Implementation detail: For performance reasons, `insert` is
        avoided in favor of `__setitem__`, if possible.

        >>> from moarchiving import BiobjectiveNondominatedSortedList
        >>> arch = BiobjectiveNondominatedSortedList()
        >>> len(arch.infos) == len(arch) == 0
        True
        >>> len(arch), arch.add([2, 2]), len(arch), arch.infos
        (0, 0, 1, [None])
        >>> arch.add([3, 1], info={'x': [-1, 2, 3], 'note': 'rocks'})
        1
        >>> len(arch.infos) == len(arch) == 2
        True
        >>> arch.infos[0], sorted(arch.infos[1].items())
        (None, [('note', 'rocks'), ('x', [-1, 2, 3])])
        >>> arch.infos[arch.index([3, 1])]['x']
        [-1, 2, 3]

        """
        f_pair = list(f_pair)  # convert array to list
        if len(f_pair) != 2:
            raise ValueError("argument `f_pair` must be of length 2, was"
                             " ``%s``" % str(f_pair))
        if not self.in_domain(f_pair):
            if self.hypervolume_plus is not None and self.hypervolume_plus < 0:
                self._hypervolume_plus = max((self._hypervolume_plus,
                                              -self.distance_to_hypervolume_area(f_pair)))
            self._removed = [f_pair]
            return None
        idx = self.bisect_left(f_pair)
        if self.dominates_with(idx - 1, f_pair) or self.dominates_with(idx, f_pair):
            if f_pair not in self[idx - 1:idx + 1]:
                self._removed = [f_pair]
            return None
        assert idx == len(self) or not f_pair == self[idx]
        # here f_pair now is non-dominated
        self._add_at(idx, f_pair, info)
        # self.make_expensive_asserts and self._asserts()
        return idx

    def _add_at(self, idx, f_pair, info=None):
        """add `f_pair` at position `idx` and remove dominated elements.

        This method assumes that `f_pair` is not weakly dominated by
        `self` and that `idx` is the correct insertion place e.g.
        acquired by `bisect_left`.
        """
        if self._infos is None and info is not None:  # prepare for inserting info
            self._infos = len(self) * [None]  # `_infos` and `self` are in a consistent state now
        if idx == len(self) or f_pair[1] > self[idx][1]:
            self.insert(idx, f_pair)
            if self._infos is not None:  # if the list exists it needs to be updated
                self._infos.insert(idx, info)  # also insert None, otherwise lists get out of sync
            self._add_HV(idx)
            # self.make_expensive_asserts and self._asserts()
            return
        # here f_pair now dominates self[idx]
        idx2 = idx + 1
        while idx2 < len(self) and f_pair[1] <= self[idx2][1]:
            # f_pair also dominates self[idx2]
            # self.pop(idx)  # slow
            # del self[idx]  # slow
            idx2 += 1  # delete later in a chunk
        self._subtract_HV(idx, idx2)
        self._removed = self[idx:idx2]
        self[idx] = f_pair  # on long lists [.] is much cheaper than insert
        if self._infos is not None:  # if the list exists it needs to be updated
            self._infos[idx] = info
        del self[idx + 1:idx2]  # can make `add` 20x faster
        if self._infos:
            del self._infos[idx + 1:idx2]
        self._add_HV(idx)
        assert len(self) >= 1
        assert self._infos is None or len(self) == len(self.infos) == len(self._infos), (
            self._infos, len(self._infos), len(self.infos))
        # assert len(self) == len(self.infos), (self._infos, self.infos, len(self.infos), len(self))
        # caveat: len(self.infos) creates a list if self._infos is None
        # self.make_expensive_asserts and self._asserts()

    def remove(self, f_pair):
        """remove element `f_pair`.

        Raises a `ValueError` (like `list`) if ``f_pair is not in self``.
        To avoid the error, checking ``if f_pair is in self`` first is a
        possible coding solution, like

        >>> from moarchiving import BiobjectiveNondominatedSortedList
        >>> nda = BiobjectiveNondominatedSortedList([[2, 3]])
        >>> f_pair = [1, 2]
        >>> assert [2, 3] in nda and f_pair not in nda
        >>> if f_pair in nda:
        ...     nda.remove(f_pair)
        >>> nda = BiobjectiveNondominatedSortedList()
        >>> nda.add_list([[6, 6], [5, 7], [4, 8], [3, 9]])
        >>> nda.remove(nda[-1])
        >>> _ = nda.add([2, 10])
        >>> nda = BiobjectiveNondominatedSortedList._random_archive(p_ref_point=1)
        >>> for t in [None, float]:
        ...     if t:
        ...         nda.hypervolume_final_float_type = t
        ...         nda.hypervolume_computation_float_type = t
        ...     for pair in list(nda):
        ...         len_ = len(nda)
        ...         state = nda._state()
        ...         nda.remove(pair)
        ...         assert len(nda) == len_ - 1
        ...         if 100 * pair[0] - int(100 * pair[0]) < 0.7:
        ...             res = nda.add(pair)
        ...             assert all(state[i] == nda._state()[i] for i in (
        ...                [0, 3] if nda.hypervolume_final_float_type is float else [0, 2, 3]))

        Return `None` (like `list.remove`).
        """
        idx = self.index(f_pair)
        self._subtract_HV(idx)
        if hasattr(self, '_hypervolume'):
            self._hypervolume_plus = self._hypervolume if self._hypervolume > 0 else -inf
        self._removed = [self[idx]]
        del self[idx]  # == list.remove(self, f_pair)
        if self._infos:
            del self._infos[idx]

    def add_list(self, list_of_f_pairs, infos=None):
        """insert a list of f-pairs which doesn't need to be sorted.

        This is just a shortcut for looping over `add`, but `discarded`
        now contains the discarded elements from all `add` operations.

        >>> from moarchiving import BiobjectiveNondominatedSortedList
        >>> arch = BiobjectiveNondominatedSortedList()
        >>> list_of_f_pairs = [[1, 2], [0, 3]]
        >>> for f_pair in list_of_f_pairs:
        ...     arch.add(f_pair)  # return insert index or None
        0
        0
        >>> arch == sorted(list_of_f_pairs)  # both entries are nondominated
        True
        >>> arch.compute_hypervolume([3, 4]) == 5.0
        True
        >>> arch.infos  # to have infos use `add` instead
        [None, None]

        Return `None`.

        Details: discarded does not contain elements of `list_of_f_pairs`.
        When `list_of_pairs` is already sorted, `merge` may have
        a small performance benefit.
        """
        removed = []
        if infos is None:
            infos = len(list_of_f_pairs) * [None]
        # should we better create a non-dominated list and do a merge?
        for f_pair, info in zip(list_of_f_pairs, infos):
            if self.add(f_pair, info=info) is not None:
                removed += [self._removed]  # slightly faster than .extend
        self._removed = removed  # could contain elements of `list_of_f_pairs`
        self.make_expensive_asserts and self._asserts()

    def merge(self, list_of_f_pairs):
        """obsolete and replaced by `add_list`. merge in a sorted list of f-pairs.

        The list can contain dominated pairs, which are discarded during
        the merge.

        Return `None`.

        Details: merging 200 into 100_000 takes 3e-4s vs 4e-4s with
        `add_list`. The `discarded` property is not consistent with the
        overall merge.
        """
        raise NotImplementedError()
        """
        # _warnings.warn("merge was never thoroughly tested, use `add_list`")
        for f_pair in list_of_f_pairs:
            if not self.in_domain(f_pair):
                continue
            f_pair = list(f_pair)  # convert array to list
            idx = self.bisect_left(f_pair, idx)
            if self.dominates_with(idx - 1, f_pair) or self.dominates_with(idx, f_pair):
                continue
            self._add_at(idx, f_pair)
        self.make_expensive_asserts and self._asserts()
        """

    def copy(self):
        """return a "deep" copy of `self`"""
        nda = BiobjectiveNondominatedSortedList()
        for d in self.__dict__:
            setattr(nda, d, getattr(self, d))
        # now fix all mutable references as a true copy
        list.__init__(nda, (p[:] for p in self))
        nda.reference_point = [xi for xi in self.reference_point]
        nda._hypervolume = self.hypervolume_final_float_type(self._hypervolume)  # with Fraction not necessary
        nda._contributing_hypervolumes = [hv for hv in self._contributing_hypervolumes]
        return nda

    def bisect_left(self, f_pair, lowest_index=0):
        """return index where `f_pair` may need to be inserted.

        Smaller indices have a strictly better f1 value or they have
        equal f1 and better f2 value.

        `lowest_index` restricts the search from below.

        Details: This method does a binary search in `self` using
        `bisect.bisect_left`.
        """
        try:
            return _bisect.bisect_left(self, f_pair, lowest_index)
        except Exception:
            pass
        try:
            f_pair = f_pair.tolist()
        except Exception:
            f_pair = list(f_pair)
        return _bisect.bisect_left(self, f_pair, lowest_index)

    def dominates(self, f_pair):
        """return `True` if any element of `self` dominates or is equal to `f_pair`.

        Otherwise return `False`.

        >>> from moarchiving import BiobjectiveNondominatedSortedList as NDA
        >>> a = NDA([[0.39, 0.075], [0.0087, 0.14]])
        >>> a.dominates(a[0])  # is always True if `a` is not empty
        True
        >>> a.dominates([-1, 33]) or a.dominates([33, -1])
        False
        >>> a._asserts()

        See also `bisect_left` to find the closest index.
        """
        if len(self) == 0:
            return False
        idx = self.bisect_left(f_pair)
        if self.dominates_with(idx - 1, f_pair) or self.dominates_with(idx, f_pair):
            return True
        return False

    def dominates_with(self, idx, f_pair):
        """return `True` if ``self[idx]`` dominates or is equal to `f_pair`.

        Otherwise return `False` or `None` if `idx` is out-of-range.

        >>> from moarchiving import BiobjectiveNondominatedSortedList as NDA
        >>> NDA().dominates_with(0, [1, 2]) is None  # empty NDA
        True

        """
        if idx < 0 or idx >= len(self):
            return None
        if self[idx][0] <= f_pair[0] and self[idx][1] <= f_pair[1]:
            return True
        return False

    def dominators(self, f_pair, number_only=False):
        """return the list of all `f_pair`-dominating elements in `self`,

        including an equal element. ``len(....dominators(...))`` is
        hence the number of dominating elements which can also be obtained
        without creating the list with ``number_only=True``.

        >>> from moarchiving import BiobjectiveNondominatedSortedList as NDA
        >>> a = NDA([[1.2, 0.1], [0.5, 1]])
        >>> len(a)
        2
        >>> a.dominators([2, 3]) == a
        True
        >>> a.dominators([0.5, 1])
        [[0.5, 1]]
        >>> len(a.dominators([0.6, 3])), a.dominators([0.6, 3], number_only=True)
        (1, 1)
        >>> a.dominators([0.5, 0.9])
        []

        """
        idx = self.bisect_left(f_pair)
        if idx < len(self) and self[idx] == f_pair:
            res = 1 if number_only else [self[idx]]
        else:
            res = 0 if number_only else []
        idx -= 1
        while idx >= 0 and self[idx][1] <= f_pair[1]:
            if number_only:
                res += 1
            else:
                res.insert(0, self[idx])  # keep sorted
            idx -= 1
        return res

    def in_domain(self, f_pair, reference_point=None):
        """return `True` if `f_pair` is dominating the reference point,

        `False` otherwise. `True` means that `f_pair` contributes to
        the hypervolume if not dominated by other elements.

        `f_pair` may also be an index in `self` in which case
        ``self[f_pair]`` is tested to be in-domain.

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

        TODO: improve name?
        """
        if reference_point is None:
            reference_point = self.reference_point
        if reference_point is None:
            return True
        try:
            f_pair = self[f_pair]
        except TypeError:
            pass
        except IndexError:
            raise  # return None
        if (f_pair[0] >= reference_point[0] or
            f_pair[1] >= reference_point[1]):
            return False
        return True

    @property
    def infos(self):
        """`list` of complementary information corresponding to each archive entry"""
        return self._infos or len(self) * [None]  # tuple is slower for len >= 1000

    @property
    def hypervolume(self):
        """hypervolume of the entire list w.r.t. the "initial" reference point.

        Raise `ValueError` when no reference point was given initially.

        >>> from moarchiving import BiobjectiveNondominatedSortedList as NDA
        >>> a = NDA([[0.5, 0.4], [0.3, 0.7]], [2, 2.1])
        >>> a._asserts()
        >>> a.reference_point == [2, 2.1]
        True
        >>> abs(a.hypervolume - a.compute_hypervolume(a.reference_point)) < 1e-11
        True
        >>> a.add([0.2, 0.8])
        0
        >>> a._asserts()
        >>> abs(a.hypervolume - a.compute_hypervolume(a.reference_point)) < 1e-11
        True
        >>> a.add([0.3, 0.6])
        1
        >>> a._asserts()
        >>> abs(a.hypervolume - a.compute_hypervolume(a.reference_point)) < 1e-11
        True

        """
        if self.reference_point is None:
            raise ValueError("to compute the hypervolume a reference"
                             " point is needed (must be given initially)")
        if self.make_expensive_asserts:
            assert abs(self._hypervolume - self.compute_hypervolume(self.reference_point)) < 1e-12
        return self._hypervolume

    @property
    def hypervolume_plus(self):
        """uncrowded hypervolume of the entire list w.r.t. the "initial" reference point.

        `hypervolume_plus` equals to the hypervolume when the archive is
        nonempty, otherwise it is the smallest Euclidean distance to the
        hypervolume area (AKA reference domain) times -1 of any element
        that was previously added but rejected because it did not dominate
        the reference point.

        Raise `ValueError` when no reference point was given initially.

        Details: conceptually, the distance computation is based on the
        nondominated archive as if it was not pruned by the reference
        point.

        >>> from moarchiving import BiobjectiveNondominatedSortedList as NDA
        >>> a = NDA(reference_point=[1, 1])
        >>> a.hypervolume_plus
        -inf
        >>> a.add([1, 2])
        >>> a.hypervolume_plus
        -1.0
        >>> a.add([1, 1])
        >>> a.hypervolume_plus
        -0.0
        >>> a.add([0.5, 0.5])
        0
        >>> float(a.hypervolume_plus)
        0.25
        """
        if self.reference_point is None:
            raise ValueError("to compute the hypervolume_plus a reference"
                             " point is needed (must be given initially)")
        return self._hypervolume_plus


    @property
    def contributing_hypervolumes(self):
        """`list` of contributing hypervolumes.

        Elements in the list are of type
        `self.hypervolume_computation_float_type`.
        Conversion to `float` in a list comprehension should always be
        possible.

        Changing this list will have unexpected consequences if
        `self.maintain_contributing_hypervolumes`,

        Details: The "initial" reference point is used for the outer
        points. If none is given, `inf` is used as reference.
        For the time being, the contributing hypervolumes are
        computed each time from scratch.

        :See also: `contributing_hypervolume`
        """
        if self.maintain_contributing_hypervolumes:
            if not hasattr(self, '_contributing_hypervolumes'):
                self._contributing_hypervolumes = [
                    self.contributing_hypervolume(i)
                    for i in range(len(self))]
            if len(self._contributing_hypervolumes) == len(self):
                return self._contributing_hypervolumes
            _warnings.warn("contributing hypervolumes seem not consistent")
        return [self.contributing_hypervolume(i)
                for i in range(len(self))]

    def contributing_hypervolume(self, idx):
        """return contributing hypervolume of element `idx`.

        If `idx` is an `f_pair`, return contributing hypervolume of element
        with value `f_pair`. If `f_pair` is not in `self`, return
        `hypervolume_improvement(f_pair)`, i.e., its uncrowded contributing
        hypervolume (which can be negative).

        The return type is ``self.hypervolume_computation_float_type` and
        by default `fractions.Fraction`, which can be converted to `float`
        like ``float(....contributing_hypervolume(idx))``.
        """
        try:
            len(idx)
        except TypeError:
            pass
        else:  # idx is a pair
            if idx in self:
                idx = self.index(idx)
            else:
                return self.hypervolume_improvement(idx)
        if idx == 0:
            y = self.reference_point[1] if self.reference_point else inf
        else:
            y = self[idx - 1][1]
        if idx in (len(self) - 1, -1):
            x = self.reference_point[0] if self.reference_point else inf
        else:
            x = self[idx + 1][0]
        if inf in (x, y):
            return inf
        Fc = self.hypervolume_computation_float_type
        dHV = (Fc(x) - Fc(self[idx][0])) * (Fc(y) - Fc(self[idx][1]))
        assert dHV >= 0
        return dHV

    def distance_to_pareto_front(self, f_pair, ref_factor=1):
        """of a dominated `f_pair` also considering the reference domain.

        Non-dominated points have (by definition) a distance of zero,
        unless the archive is empty and the point does not dominate the
        reference point.

        The implementation assumes that all points of the archive are in
        the reference domain (and more extreme points have been pruned, as
        it is the default behavior).

        Details: the distance for dominated points is computed by
        iterating over the relevant kink points ``(self[i+1][0],
        self[i][1])``. In case of minimization, the boundary with two
        non-dominated points can be depicted like::

            ...______.      . <- reference point
                     |
                     x__. <- kink point
                        |
                        x___. <- kink point
                            |
                            |
                            :
                            :

        The three kink points which are possibly used for the computations
        are denoted by a dot. The outer kink points use one coordinate of
        the reference point.
        """
        if self.in_domain(f_pair) and not self.dominates(f_pair):
            return 0  # return minimum distance

        if self.reference_point:
            ref_d0 = ref_factor * max((0, f_pair[0] - self.reference_point[0]))
            ref_d1 = ref_factor * max((0, f_pair[1] - self.reference_point[1]))
        else:
            ref_d0 = 0
            ref_d1 = 0

        if len(self) == 0:  # otherwise we get an index error below
            return (ref_d0**2 + ref_d1**2)**0.5

        # distances to the two outer kink points, given by the extreme
        # points and the respective the reference point coordinate, for
        # the left (and up) most point:
        squared_distances = [max((0, f_pair[0] - self[0][0]))**2 +
                              ref_d1**2]
        # and the right most (and lowest) point
        squared_distances += [ref_d0**2 +
                             max((0, f_pair[1] - self[-1][1]))**2]
        if len(self) == 1:
            return min(squared_distances)**0.5
        for idx in range(self.bisect_left(f_pair), 0, -1):
            if idx == len(self):
                continue
            squared_distances.append(
                max((0, f_pair[1] - self[idx - 1][1]))**2 +
                max((0, f_pair[0] - self[idx][0]))**2)
            if self[idx][1] >= f_pair[1] or idx == 1:
                break
        if self.make_expensive_asserts and len(squared_distances) > 2:
            assert min(squared_distances[2:]) == min(
                        [max((0, f_pair[0] - self[i + 1][0]))**2 +
                         max((0, f_pair[1] - self[i][1]))**2
                         for i in range(len(self) - 1)])
        return min(squared_distances)**0.5

    def distance_to_hypervolume_area(self, f_pair):
        return (max((0, f_pair[0] - self.reference_point[0]))**2
                + max((0, f_pair[1] - self.reference_point[1]))**2)**0.5 \
               if self.reference_point else 0

    def _hypervolume_improvement0(self, f_pair):
        """deprecated and only used for testing: return how much `f_pair` would improve the hypervolume.

        If dominated, return the distance to the empirical pareto front
        multiplied by -1.
        Else if not in domain, return distance to the reference point
        dominating area times -1.

        Overall this amounts to the uncrowded hypervolume improvement,
        see https://arxiv.org/abs/1904.08823
        """
        save_infos = self._infos.copy() if self._infos is not None else None
        save_hypervolume_plus = self._hypervolume_plus
        dist = self.distance_to_pareto_front(f_pair)
        if dist:
            return -dist
        hv0 = self.hypervolume
        state = self._state()
        removed = self.discarded  # to get back previous state
        added = self.add(f_pair) is not None
        if added and self.discarded is not removed:
            add_back = self.discarded
        else:
            add_back = []
        assert len(add_back) + len(self) - added == state[0]
        hv1 = self.hypervolume
        if added:
            self.remove(f_pair)
        if add_back:
            self.add_list(add_back)
        self._removed = removed
        if self.hypervolume_computation_float_type is not float and (
            self.hypervolume_final_float_type is not float):
            assert state == self._state()
        if hv0 != self.hypervolume:
            _warnings.warn("HV changed from %f to %f while computing hypervolume_improvement" %
                           (hv0, self.hypervolume))
        self._infos = save_infos
        self._hypervolume_plus = save_hypervolume_plus
        return self.hypervolume_computation_float_type(hv1) - self.hypervolume

    def hypervolume_improvement(self, f_pair):
        """return how much `f_pair` would improve the hypervolume.

        If dominated, return the distance to the empirical pareto front
        multiplied by -1.
        Else if not in domain, return distance to the reference point
        dominating area times -1.

        Overall this amounts to the uncrowded hypervolume improvement,
        see https://arxiv.org/abs/1904.08823

        Details: when ``self.reference_point is None`` and `f_pair` is
        a new extreme point, the returned hypervolume improvement is
        ``float('inf')``.

        This method extracts a sublist first and thereby tries
        to circumentvent to compute small differences between large
        hypervolumes.
        """
        dist = self.distance_to_pareto_front(f_pair)
        if dist:
            return -dist
        if self.reference_point is None:
            if f_pair[0] < self[0][0] or f_pair[1] < self[-1][1]:
                return inf
        # find sublist that suffices to get the contributing volume
        i0 = self.bisect_left(f_pair)
        i1 = i0
        while i1 < len(self) and f_pair[1] <= self[i1][1]:
            # f_pair also dominates self[i1]
            i1 += 1
        r0 = self[i1][0] if i1 < len(self) else self.reference_point[0]
        r1 = self[i0-1][1] if i0 > 0 else self.reference_point[1]
        assaved = BiobjectiveNondominatedSortedList.make_expensive_asserts
        BiobjectiveNondominatedSortedList.make_expensive_asserts = False  # prevent infinite recursion
        sub = BiobjectiveNondominatedSortedList(self[i0:i1], reference_point=[r0, r1], sort=None)
        BiobjectiveNondominatedSortedList.make_expensive_asserts = assaved
        hv0 = sub.hypervolume
        sub.add(f_pair)
        res = self.hypervolume_computation_float_type(sub.hypervolume) - hv0
        if BiobjectiveNondominatedSortedList.make_expensive_asserts:
            assert abs(res - self._hypervolume_improvement0(f_pair)) < 1e-9 * (0.1 + res), (
                        res, self._hypervolume_improvement0(f_pair))
        return res

    def _set_HV(self):
        """set current hypervolume value using `self.reference_point`.

        Raise `ValueError` if `self.reference_point` is `None`.

        TODO: we may need to store the list of _contributing_ hypervolumes
        to handle numerical rounding errors later.
        """
        if self.reference_point is None:
            return None
        self._hypervolume = self.compute_hypervolume(self.reference_point)
        if self._hypervolume > 0:
            self._hypervolume_plus = self._hypervolume
        return self._hypervolume

    def compute_hypervolume(self, reference_point):
        """return hypervolume w.r.t. `reference_point`"""
        if reference_point is None:
            raise ValueError("to compute the hypervolume a reference"
                             " point is needed (was `None`)")
        Fc = self.hypervolume_computation_float_type
        Ff = self.hypervolume_final_float_type
        hv = Ff(0.0)
        idx = 0
        while idx < len(self) and not self.in_domain(self[idx], reference_point):
            idx += 1
        if idx < len(self):
            hv += Ff((Fc(reference_point[0]) - Fc(self[idx][0])) * (Fc(reference_point[1]) - Fc(self[idx][1])))
            idx += 1
        while idx < len(self) and self.in_domain(self[idx], reference_point):
            hv += Ff((Fc(reference_point[0]) - Fc(self[idx][0])) * (Fc(self[idx - 1][1]) - Fc(self[idx][1])))
            idx += 1
        return hv

    def compute_hypervolumes(self, reference_point):
        """depricated, subject to removal, see `compute_hypervolume` and `contributing_hypervolumes`.

        Never implemented: return list of contributing hypervolumes w.r.t.
        reference_point
        """
        # Old/experimental code (in a string to suppress pylint warnings):
        """
        # construct self._hypervolumes_list
        # keep sum of different size elements separate,
        # say, a dict of index lists as indices[1e12] indices[1e6], indices[1], indices[1e-6]...
        hv = {}
        for key in indices:
            hv[key] = sum(_hypervolumes_list[i] for i in indices[key])
        # we may use decimal.Decimal to compute the sum of hv
        decimal.getcontext().prec = 88
        hv_sum = sum([decimal.Decimal(hv[key]) for key in hv])
        """
        raise NotImplementedError()

    def _subtract_HV(self, idx0, idx1=None):
        """remove contributing hypervolumes of elements ``self[idx0] to self[idx1 - 1]``.

        TODO: also update list of contributing hypervolumes in case.
        """
        if self.maintain_contributing_hypervolumes:
            """Old or experimental:
            del self._contributing_hypervolumes[idx]
            # we also need to update the contributing HVs of the neighbors
            """
            raise NotImplementedError("update list of hypervolumes")
        if self.reference_point is None:
            return None
        if idx1 is None:
            idx1 = idx0 + 1
        if idx1 - idx0 == len(self):  # subtract HV of all points
            assert idx0 == 0
            dHV = -self._hypervolume
            self._hypervolume *= 0  # keep type
            return dHV
        if idx0 == 0:
            y = self.reference_point[1]
        else:
            y = self[idx0 - 1][1]
        Fc = self.hypervolume_computation_float_type
        Ff = self.hypervolume_final_float_type
        dHV = Fc(0.0)
        for idx in range(idx0, idx1):
            if idx == len(self) - 1:
                assert idx < len(self)
                x = self.reference_point[0]
            else:
                x = self[idx + 1][0]
            dHV -= (Fc(x) - Fc(self[idx][0])) * (Fc(y) - Fc(self[idx][1]))
        assert dHV <= 0  # and without loss of precision strictly smaller
        if ((Ff in (float, int) or isinstance(self._hypervolume, (float, int)))
                and self._hypervolume != 0 and abs(dHV) / self._hypervolume < 1e-9):
            _warnings.warn("_subtract_HV: subtracting {:.16e} from {:.16e} loses many digits of precision"
                          "\nSelf info: {}\nTraceback: {}".format(
                               -dHV,
                               self._hypervolume,
                               self._debug_info(),
                               _debug_trace()))
        self._hypervolume += Ff(dHV)
        if self._hypervolume < 0:
            _warnings.warn("subtracting {:.16e} from the hypervolume lead to a"
                          " negative hypervolume value of {:.16e}"
                          "\nSelf info: {}\nTraceback: {}".format(
                               -dHV,
                               self._hypervolume,
                               self._debug_info(),
                               _debug_trace()))
        # assert self._hypervolume >= 0
        return dHV

    def _add_HV(self, idx):
        """add contributing hypervolume of ``self[idx]`` to hypervolume.

        TODO: also update list of contributing hypervolumes in case.
        """
        if self.maintain_contributing_hypervolumes:
            """Exerimental code:
            self._contributing_hypervolumes.insert(idx, dHV)
            if idx > 0:
                self._contributing_hypervolumes[idx - 1] = self.contributing_hypervolume(idx - 1)
            if idx < len(self) - 1:
                self._contributing_hypervolumes[idx + 1] = self.contributing_hypervolume(idx + 1)
            # TODO: proof read
            """
            raise NotImplementedError("update list of hypervolumes")
        if self.reference_point is None:
            return None
        dHV = self.contributing_hypervolume(idx)
        Ff = self.hypervolume_final_float_type
        if self._hypervolume and (
                        Ff in (float, int) or isinstance(self._hypervolume, (float, int))) \
                and abs(dHV) / self._hypervolume < 1e-9:
            _warnings.warn("_add_HV: adding {} to HV={} loses many digits of precision"
                           "\nSelf info: {}\nTraceback: {}".format(
                               dHV,
                               self._hypervolume,
                               self._debug_info(),
                               _debug_trace()))
        self._hypervolume += Ff(dHV)
        self._hypervolume_plus = self._hypervolume
        return dHV

    def prune(self):
        """remove dominated or equal entries assuming that the list is sorted.

        Return number of dropped elements.

        Implementation details: pruning from right to left may be
        preferable, because list.insert(0) is O(n) while list.append is
        O(1), however it is not possible with the given sorting: in
        principle, the first element may dominate all others, which can
        only be discovered in the last step when traversing from right
        to left. This suggests that reverse sort may be better for
        pruning or we should inherit from `collections.deque` instead
        from `list`, but `deque` seems not to support deletion of slices.
        """
        nb = len(self)
        removed = []
        i = 0
        while i < len(self):
            if self.in_domain(self[i]):
                break
            i += 1
        removed += self[0:i]
        del self[0:i]
        if self._infos:
            del self._infos[0:i]
        i = 1
        while i < len(self):
            i0 = i
            while i < len(self) and (self[i][1] >= self[i0 - 1][1] or
                                         not self.in_domain(self[i])):
                i += 1
                # self.pop(i + 1)  # about 10x slower in notebook test
            # prepare indices for the removed list
            i0r = i0
            if i0 > 0:
                while i0r < i:
                    if self[i0r] == self[i0 - 1]:
                        i0r += 1  # skip self[i0r] as removed because it is still in self
                    else:
                        break
            ir = i
            if i + 1 < len(self):
                while ir > i0r:
                    if self[ir] == self[i + 1]:
                        ir -= 1  # skip self[ir] as removed as it is in self
                    else:
                        break
            removed += self[i0r:ir]
            del self[i0:i]
            if self._infos:
                del self._infos[i0:i]
            i = i0 + 1
        self._removed = removed  # [p for p in removed if p not in self]
        if self.maintain_contributing_hypervolumes:
            # Old or experimental code:
            """
            ::

                self._contributing_hypervolumes = [  # simple solution
                    self.contributing_hypervolume(i)
                    for i in range(len(self))]

            """
            raise NotImplementedError
        return nb - len(self)

    @property
    def discarded(self):
        """`list` of f-pairs discarded in the last relevant method call.

        Methods covered are `__init__`, `prune`, `add`, and `add_list`.
        Removed duplicates are not element of the discarded list except with
        `__init__`. When not inserted and not already in `self` also the
        input argument(s) show(s) up in `discarded`.

        Example to create a list of rank-k-non-dominated fronts:

        >>> from moarchiving import BiobjectiveNondominatedSortedList as NDA
        >>> all_ = [[0.1, 1], [-2, 3], [-4, 5], [-4, 5], [-4, 4.9]]
        >>> nda_list = NDA(all_)  # rank-0-non-dominated
        >>> assert nda_list.discarded == [[-4, 5], [-4, 5]]

        """
        try:
            return self._removed
        except AttributeError:
            return []

    def _state(self):
        return len(self), self.discarded, self.hypervolume, self.reference_point

    @staticmethod
    def _random_archive(max_size=500, p_ref_point=0.5):
        from numpy import random as npr
        N = npr.randint(max_size)
        ref_point = list(npr.randn(2) + 1) if npr.rand() < p_ref_point else None
        return BiobjectiveNondominatedSortedList(
            [list(0.01 * npr.randn(2) + npr.rand(1) * [i, -i])
             for i in range(N)],
            reference_point=ref_point)

    def _asserts(self):
        """make all kind of consistency assertions.

        >>> import moarchiving
        >>> a = moarchiving.BiobjectiveNondominatedSortedList(
        ...    [[-0.749, -1.188], [-0.557, 1.1076],
        ...    [0.2454, 0.4724], [-1.146, -0.110]], [10, 10])
        >>> a._asserts()
        >>> for i in range(len(a)):
        ...    assert a.contributing_hypervolume(i) == a.contributing_hypervolumes[i]
        >>> assert all(map(lambda x, y: x - 1e-9 < y < x + 1e-9,
        ...               a.contributing_hypervolumes,
        ...               [4.01367, 11.587422]))
        >>> len(a), a.add([-0.8, -1], info={'solution': None}), len(a)
        (2, 1, 3)
        >>> len(a) == len(a.infos) == 3
        True
        >>> for i, p in enumerate(list(a)):
        ...     a.remove(p)
        ...     assert len(a) == len(a.infos) == 2 - i
        >>> assert len(a) == len(a.infos) == 0
        >>> try: a.remove([0, 0])
        ... except ValueError: pass
        ... else: raise AssertionError("remove did not raise ValueError")

        >>> import numpy as np
        >>> randn = np.random.randn
        >>> for _ in range(120):
        ...     a = moarchiving.BiobjectiveNondominatedSortedList._random_archive()
        ...     a.make_expensive_asserts = True
        ...     if a.reference_point:
        ...         for i, f_pair in enumerate([randn(2) + [i, -i] for i in range(10)] +
        ...                                    [randn(2) / randn(2) + [i, -i] for i in range(10)]):
        ...             if i % 4 == 1:
        ...                 _ = a.add(f_pair)
        ...             h0 = a.hypervolume
        ...             hi = a.hypervolume_improvement(list(f_pair))
        ...             hi_org = a._hypervolume_improvement0(list(f_pair))
        ...             assert hi == hi_org  # didn't raise with rand instead of randn
        ...             assert a.hypervolume == h0, (a.hypervolume, h0)  # works OK with Fraction
        ...             a._asserts()

        """
        assert sorted(self) == self
        for pair in self:
            assert self.count(pair) == 1
        tmp = BiobjectiveNondominatedSortedList.make_expensive_asserts
        BiobjectiveNondominatedSortedList.make_expensive_asserts = False
        assert BiobjectiveNondominatedSortedList(self) == self
        BiobjectiveNondominatedSortedList.make_expensive_asserts = tmp
        for pair in self:
            assert self.dominates(pair)
            assert not self.dominates([v - 0.001 for v in pair])
        if self.reference_point is not None:
            assert abs(self._hypervolume - self.compute_hypervolume(self.reference_point)) < 1e-11
            assert sum(self.contributing_hypervolumes) < self.hypervolume + 1e-11
        if self.maintain_contributing_hypervolumes:
            assert len(self) == len(self._contributing_hypervolumes)
        assert len(self) == len(self.contributing_hypervolumes)
        # for i in range(len(self)):
        #     assert self.contributing_hypervolume(i) == self.contributing_hypervolumes[i]

        if self.reference_point:
            tmp, self.make_expensive_asserts = self.make_expensive_asserts, False
            self.hypervolume_improvement([0, 0])  # does state assert
            self.make_expensive_asserts = tmp

        assert self._infos is None or len(self._infos) == len(self.infos) == len(self), (
            self._infos, len(self._infos), len(self))
        # assert len(self.infos) == len(self), (len(self.infos), len(self), self.infos, self._infos)
        # caveat: len(self.infos) creates a list if self._infos is None

        # asserts using numpy for convenience
        try:
            import numpy as np
        except ImportError:
            _warnings.warn("asserts using numpy omitted")
        else:
            if len(self) > 1:
                diffs = np.diff(self, 1, 0)
                assert all(diffs[:, 0] > 0)
                assert all(diffs[:, 1] < 0)


if __name__ == "__main__":
    import doctest
    print('doctest.testmod() in moarchiving.py')
    print(doctest.testmod())
