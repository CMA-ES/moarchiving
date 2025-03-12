"""This module contains various utility functions and classes for the MOArchiving package."""
import warnings as _warnings
try:
    from sortedcontainers import SortedKeyList
except ImportError:
    _warnings.warn('`sortedcontainers` module not installed, moarchiving for 3 and 4 objectives will not work')
    SortedKeyList = list


class DLNode:
    """ A class to represent a node in a doubly linked list. """
    def __init__(self, x=None, info=None):
        """ Initialize a node with the given x-coordinate and info. """
        self.x = x if x else [None, None, None, None]
        self.closest = [None, None]  # closest in x coordinate, closest in y coordinate
        self.cnext = [None, None]  # current next
        self.next = [None, None, None, None]
        self.prev = [None, None, None, None]
        self.ndomr = 0  # number of dominators
        self.info = info

    def copy(self):
        """ copy the node """
        new_node = DLNode()
        for var in self.__dict__:
            if isinstance(getattr(self, var), list):
                setattr(new_node, var, getattr(self, var).copy())
            else:
                setattr(new_node, var, getattr(self, var))
        return new_node


class ArchiveSortedList(SortedKeyList):
    """ A class to represent a sorted list of nodes, together with additional methods that
     follow the definition in the paper."""
    def __init__(self, iterable=None, key=lambda node: node.x[1]):
        """ Initialize the sorted list with the given iterable and key function. """
        if SortedKeyList is list:
            raise ImportError("`MySortedList `requires `sortedcontainers` to be installed")
        super().__init__(iterable=iterable, key=key)

    def __str__(self):
        """ Return a string representation of the sorted list. """
        return str([node.x for node in self])

    def head_y(self):
        """ Return the point q from the list, with the smallest q_y """
        return self[0]

    def head_x(self):
        """ Return the point q from the list, with the smallest q_x """
        return self[-1]

    def next_y(self, s):
        """ Return the point q from the list, with the smallest q_y > s_y, for a given point s
        from the list """
        return self[self.index(s) + 1]

    def next_x(self, s):
        """ Return the point q from the list, with the smallest q_x > s_x, for a given point s
        from the list """
        return self[self.index(s) - 1]

    def outer_delimiter_y(self, p):
        """ Return the point q from the list, with the smallest q_y > p_y, such that q_x < p_x """
        i = self.bisect_left(p)
        while i < len(self) and self[i].x[0] >= p.x[0]:
            i += 1
        return self[i]

    def outer_delimiter_x(self, p):
        """ Return the point q from the list, with the smallest q_x > p_x, such that q_y < p_y """
        i = self.bisect_left(p) - 1
        while i > 0 and self[i].x[1] >= p.x[1]:
            i -= 1
        return self[i]

    def remove_dominated_y(self, p, s):
        """ For s = outer_delimiter_x(p), remove all points q, such that p* <= q* from the list,
        and return them sorted by ascending order of q_y """
        e = self.next_y(s)
        points_to_remove = []
        while p.x[0] <= e.x[0]:
            points_to_remove.append(e)
            e = self.next_y(e)

        for q in points_to_remove:
            self.remove(q)

        return points_to_remove

    def remove_dominated_x(self, p, s):
        """ For s = outer_delimiter_y(p), remove all points q, such that p* <= q* from the list,
        and return them sorted by ascending order of q_x """
        e = self.next_x(s)
        points_to_remove = []
        while p.x[1] <= e.x[1]:
            points_to_remove.append(e)
            e = self.next_x(e)

        for q in points_to_remove:
            self.remove(q)

        return points_to_remove

    def add_y(self, p, s):
        """ Insert point p into the list, if s_y < p_y < next_y(s)_y or p_y < head_y_y """
        if len(self) == 0:
            self.add(p)
        elif s.x[1] < p.x[1] < self.next_y(s).x[1]:
            self.add(p)
        elif p.x[1] < self.head_y().x[1] and s is None:
            self.add(p)

    def add_x(self, p, s):
        """ Insert point p into the list, if s_x < p_x < next_x(s)_x or p_x < head_x_x """
        if len(self) == 0:
            self.add(p)
        elif s.x[0] < p.x[0] < self.next_x(s).x[0]:
            self.add(p)
        elif p.x[0] < self.head_x().x[0] and s is None:
            self.add(p)


def my_lexsort(keys):
    """ Sort an array of keys in lexicographic order and return the indices.
    Equivalent to np.lexsort """
    idk_key_tuple = list(enumerate([list(x)[::-1] for x in zip(*keys)]))
    idk_key_tuple.sort(key=lambda x: x[1])
    return [x[0] for x in idk_key_tuple]


# --------------- Auxiliary Functions ---------------------


def lexicographic_less(a, b):
    """ Returns True if a is lexicographically less than b, False otherwise """
    return a[2] < b[2] or (a[2] == b[2] and (a[1] < b[1] or (a[1] == b[1] and a[0] <= b[0])))


def init_sentinels_new(list_nodes, ref, dim):
    """ Initialize the sentinel nodes for the list of nodes given
    the reference point and the dimensionality """
    s1, s2, s3 = list_nodes[0], list_nodes[1], list_nodes[2]

    # Initialize s1 node
    s1.x = [float('-inf'), ref[1], float('-inf'), float('-inf')]
    s1.closest = [s2, s1]
    s1.next = [None, None, s2, s2]
    s1.cnext = [None, None]
    s1.prev = [None, None, s3, s3]
    s1.ndomr = 0

    # Initialize s2 node
    s2.x = [ref[0], float('-inf'), float('-inf'), float('-inf')]
    s2.closest = [s2, s1]
    s2.next = [None, None, s3, s3]
    s2.cnext = [None, None]
    s2.prev = [None, None, s1, s1]
    s2.ndomr = 0

    # Initialize s3 node
    s3.x = [float('-inf'), float('-inf'), ref[2], ref[3] if dim == 4 else float('-inf')]
    s3.closest = [s2, s1]
    s3.next = [None, None, s1, None]
    s3.cnext = [None, None]
    s3.prev = [None, None, s2, s2]
    s3.ndomr = 0

    return s1


def add_to_z(new):
    """ Add a new node to the list sorted by z """
    new.next[2] = new.prev[2].next[2]
    new.next[2].prev[2] = new
    new.prev[2].next[2] = new


def remove_from_z(old, archive_dim):
    """ Remove a node from the list sorted by z """
    di = archive_dim - 1
    old.prev[di].next[di] = old.next[di]
    old.next[di].prev[di] = old.prev[di]


def setup_z_and_closest(head, new):
    """ Sets up the closest[0] and closest[1] pointers for the new node """
    closest1 = head
    closest0 = head.next[2]

    q = head.next[2].next[2]
    newx = new.x

    while q and lexicographic_less(q.x, newx):
        if q.x[0] <= newx[0] and q.x[1] <= newx[1]:
            new.ndomr += 1
        elif q.x[1] < newx[1] and (
                q.x[0] < closest0.x[0] or (q.x[0] == closest0.x[0] and q.x[1] < closest0.x[1])):
            closest0 = q
        elif q.x[0] < newx[0] and (
                q.x[1] < closest1.x[1] or (q.x[1] == closest1.x[1] and q.x[0] < closest1.x[0])):
            closest1 = q

        q = q.next[2]

    new.closest[0] = new.cnext[0] = closest0
    new.closest[1] = new.cnext[1] = closest1
    new.prev[2] = q.prev[2] if q else None
    new.next[2] = q


def update_links(head, new, p):
    stop = head.prev[2]
    ndom = 0
    all_delimiters_visited = False

    while p != stop and not all_delimiters_visited:
        if p.x[0] <= new.x[0] and p.x[1] <= new.x[1] and (p.x[0] < new.x[0] or p.x[1] < new.x[1]):
            all_delimiters_visited = True
        else:
            if new.x[0] <= p.x[0]:
                if new.x[1] <= p.x[1]:
                    p.ndomr += 1
                    ndom += 1
                    remove_from_z(p, 3)
                elif new.x[0] < p.x[0] and (new.x[1] < p.closest[1].x[1] or (
                        new.x[1] == p.closest[1].x[1] and (new.x[0] < p.closest[1].x[0] or (
                        new.x[0] == p.closest[1].x[0] and new.x[2] < p.closest[1].x[2])))):
                    p.closest[1] = new
            elif new.x[1] < p.x[1] and (new.x[0] < p.closest[0].x[0] or (
                    new.x[0] == p.closest[0].x[0] and (new.x[1] < p.closest[0].x[1] or (
                    new.x[1] == p.closest[0].x[1] and new.x[2] < p.closest[0].x[2])))):
                p.closest[0] = new
        p = p.next[2]
    return ndom


def restart_list_y(head):
    """ Resets the cnext pointers for the y-dimension."""
    head.next[2].cnext[1] = head
    head.cnext[0] = head.next[2]


def compute_area_simple(p, di, s, u, Fc):
    """ Computes the area as described in the paper """
    dj = 1 - di
    area = Fc(0)
    q = s
    area += (Fc(q.x[dj]) - Fc(p[dj])) * (Fc(u.x[di]) - Fc(p[di]))

    while p[dj] < u.x[dj]:
        q = u
        u = u.cnext[di]
        area += (Fc(q.x[dj]) - Fc(p[dj])) * (Fc(u.x[di]) - Fc(q.x[di]))

    return area


def restart_base_setup_z_and_closest(head, new):
    # Sets up closest[0] and closest[1] for the new node
    p = head.next[2].next[2]
    closest1 = head
    closest0 = head.next[2]

    newx = new.x

    restart_list_y(head)

    while p and lexicographic_less(p.x, newx):
        p.cnext[0] = p.closest[0]
        p.cnext[1] = p.closest[1]

        p.cnext[0].cnext[1] = p
        p.cnext[1].cnext[0] = p

        if p.x[0] <= newx[0] and p.x[1] <= newx[1]:
            new.ndomr += 1
        elif p.x[1] < newx[1] and (
                p.x[0] < closest0.x[0] or (p.x[0] == closest0.x[0] and p.x[1] < closest0.x[1])):
            closest0 = p
        elif p.x[0] < newx[0] and (
                p.x[1] < closest1.x[1] or (p.x[1] == closest1.x[1] and p.x[0] < closest1.x[0])):
            closest1 = p

        p = p.next[2]

    new.closest[0] = closest0
    new.closest[1] = closest1
    new.prev[2] = p.prev[2] if p else None
    new.next[2] = p


def one_contribution_3_obj(head, new, Fc):
    """ Computes the contribution of adding a new point to the archive in three dimensions """
    restart_base_setup_z_and_closest(head, new)
    if new.ndomr > 0:
        return 0

    new.cnext[0] = new.closest[0]
    new.cnext[1] = new.closest[1]
    area = compute_area_simple(new.x, 1, new.cnext[0], new.cnext[0].cnext[1], Fc)

    p = new.next[2]
    lastz = Fc(new.x[2])
    volume = Fc(0)

    while p and (p.x[0] > new.x[0] or p.x[1] > new.x[1]):
        volume += area * (Fc(p.x[2]) - lastz)
        p.cnext[0] = p.closest[0]
        p.cnext[1] = p.closest[1]

        if p.x[0] >= new.x[0] and p.x[1] >= new.x[1]:
            area -= compute_area_simple(p.x, 1, p.cnext[0], p.cnext[0].cnext[1], Fc)
            p.cnext[1].cnext[0] = p
            p.cnext[0].cnext[1] = p
        elif p.x[0] >= new.x[0]:
            if p.x[0] <= new.cnext[0].x[0]:
                x = [p.x[0], new.x[1], p.x[2]]
                area -= compute_area_simple(x, 1, new.cnext[0], new.cnext[0].cnext[1], Fc)
                p.cnext[0] = new.cnext[0]
                p.cnext[1].cnext[0] = p
                new.cnext[0] = p
        else:
            if p.x[1] <= new.cnext[1].x[1]:
                x = [new.x[0], p.x[1], p.x[2]]
                area -= compute_area_simple(x, 0, new.cnext[1], new.cnext[1].cnext[0], Fc)
                p.cnext[1] = new.cnext[1]
                p.cnext[0].cnext[1] = p
                new.cnext[1] = p

        lastz = p.x[2]
        p = p.next[2]

    if p:
        volume += area * (Fc(p.x[2]) - Fc(lastz))
    return volume


def setup_cdllist(n_obj, points, ref, infos):
    """ Set up a circular doubly linked list from the given data and reference point """
    points = [p for p in points if strictly_dominates(p, ref, n_obj)]
    n = len(points)

    head = [DLNode(info=info) for info in ["s1", "s2", "s3"] + [None] * n]
    # init_sentinels_new accepts a list at the beginning, therefore we use head[0:3]
    init_sentinels_new(head[0:3], ref, n_obj)
    di = n_obj - 1  # Dimension index for sorting (z-axis in 3D)

    if n > 0:
        # Convert data to a structured format suitable for sorting and linking
        if n_obj == 3:
            # Using lexsort to sort by z, y, x in ascending order
            sorted_indices = my_lexsort(([p[0] for p in points], [p[1] for p in points],
                                         [p[2] for p in points]))
        elif n_obj == 4:
            # Using lexsort to sort by w, z, y, x in ascending order
            sorted_indices = my_lexsort(([p[0] for p in points], [p[1] for p in points],
                                         [p[2] for p in points], [p[3] for p in points]))
        else:
            raise ValueError("Only 3D and 4D points are supported")

        # Create nodes from sorted points
        for i, index in enumerate(sorted_indices):
            head[i + 3].x = points[index]
            head[i + 3].info = infos[index]
            if n_obj == 3:
                # Add 0.0 for 3d points so that it matches the original C code
                head[i + 3].x.append(0.0)

        # Link nodes
        s = head[0].next[di]
        s.next[di] = head[3]
        head[3].prev[di] = s

        for i in range(3, n + 2):
            head[i].next[di] = head[i + 1] if i + 1 < len(head) else head[0]
            head[i + 1].prev[di] = head[i]

        s = head[0].prev[di]
        s.prev[di] = head[n + 2]
        head[n + 2].next[di] = s

    return head[0]


def weakly_dominates(a, b, n_obj):
    """ Return True if a weakly dominates b, False otherwise

    >>> weakly_dominates([1, 2, 3], [2, 3, 3], n_obj=3)
    True
    >>> weakly_dominates([1, 2, 3], [2, 2, 2], n_obj=3)
    False
    >>> weakly_dominates([1, 2, 3], [1, 2, 3], n_obj=3)
    True
    """
    return all(a[i] <= b[i] for i in range(n_obj))


def strictly_dominates(a, b, n_obj):
    """ Return True if a strictly dominates b, False otherwise

    >>> strictly_dominates([1, 2, 3], [2, 3, 3], n_obj=3)
    True
    >>> strictly_dominates([1, 2, 3], [2, 2, 2], n_obj=3)
    False
    >>> strictly_dominates([1, 2, 3], [1, 2, 3], n_obj=3)
    False
    """
    return (all(a[i] <= b[i] for i in range(n_obj)) and
            any(a[i] < b[i] for i in range(n_obj)))


def hv3dplus(head, Fc):
    """ Computes the hypervolume indicator in d=3 in linear time """
    p = head
    area = Fc(0)
    volume = Fc(0)

    restart_list_y(head)
    p = p.next[2].next[2]

    stop = head.prev[2]

    while p != stop:
        if p.ndomr < 1:
            p.cnext[0] = p.closest[0]
            p.cnext[1] = p.closest[1]

            area += compute_area_simple(p.x, 1, p.cnext[0], p.cnext[0].cnext[1], Fc)
            p.cnext[0].cnext[1] = p
            p.cnext[1].cnext[0] = p
        else:
            remove_from_z(p, 3)

        volume += area * (Fc(p.next[2].x[2]) - Fc(p.x[2]))
        p = p.next[2]

    return volume


def hv4dplusR(head, Fc):
    """ Compute the hypervolume indicator in d=4 by iteratively
    computing the hypervolume indicator in d=3 (using hv3d+) """
    hv = Fc(0)

    stop = head.prev[3]
    new = head.next[3].next[3]

    while new != stop:
        setup_z_and_closest(head, new)  # Compute cx and cy of 'new' and determine next and prev in z
        add_to_z(new)  # Add 'new' to list sorted by z
        update_links(head, new, new.next[2])  # Update cx and cy of the points above 'new' in z
        # and remove dominated points

        volume = hv3dplus(head, Fc)  # Compute hv indicator in d=3 in linear time

        height = Fc(new.next[3].x[3]) - Fc(new.x[3])
        hv += volume * height  # Update hypervolume in d=4

        new = new.next[3]

    return hv


def hv4dplusU(head, Fc):
    """ Compute the hypervolume indicator in d=4 by iteratively
    computing the one contribution problem in d=3.
    """
    volume = Fc(0)
    hv = Fc(0)

    last = head.prev[3]
    new = head.next[3].next[3]

    while new != last:
        volume += one_contribution_3_obj(head, new, Fc)
        add_to_z(new)
        update_links(head, new, new.next[2])

        height = Fc(new.next[3].x[3]) - Fc(new.x[3])
        hv += volume * height

        new = new.next[3]

    return hv
