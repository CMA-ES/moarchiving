""" Test the BiobjectiveNondominatedSortedList class """

from moarchiving.moarchiving import BiobjectiveNondominatedSortedList

import unittest
import random
import math

inf = float('inf')


def list_to_set(lst):
    """ Converts a list of lists to a set of tuples """
    return set([tuple(p) for p in lst])


class TestMOArchiving2obj(unittest.TestCase):
    """ Tests for the BiobjectiveNondominatedSortedList class """
    def test_hypervolume_easy(self):
        """ test the hypervolume calculation for a simple case """
        points = [[1, 2], [2, 1]]
        moa = BiobjectiveNondominatedSortedList(points, reference_point=[3, 3], infos=["A", "B"])
        self.assertEqual(moa.hypervolume, 3)

    def test_infos_non_dominated(self):
        """ test if the infos are stored correctly - if the points are non dominated,
        the infos should be the same"""
        points = [
            [1, 2],
            [2, 1],
            [1.3, 1.7],
            [1.5, 1.5]
        ]
        infos = [str(p) for p in points]

        moa = BiobjectiveNondominatedSortedList(points, [3, 3], infos=infos)
        # assert that the infos are stored in the same order as the points
        self.assertEqual([str(p[:2]) for p in moa], moa.infos)
        # assert that all the points in the archive are non dominated and thus have the same info
        self.assertSetEqual(set([str(p) for p in points]), set(moa.infos))

        moa_add = BiobjectiveNondominatedSortedList(reference_point=[3, 3])
        moa_add.add_list(points, infos=infos)
        self.assertEqual([str(p[:2]) for p in moa_add], moa_add.infos)
        self.assertSetEqual(set([str(p) for p in points]), set(moa_add.infos))

    def test_infos_dominated(self):
        """ test if the infos about dominated points are removed """
        points = [
            [1, 3],
            [3, 2],
            [2, 3],
            [3, 1]
        ]
        infos = ["A", "B", "C", "D"]

        moa = BiobjectiveNondominatedSortedList(points, [6, 6], infos=infos)
        # assert that only points A and D are stored in the archive
        self.assertSetEqual({"A", "D"}, set(moa.infos))

        moa_add = BiobjectiveNondominatedSortedList(reference_point=[6, 6])
        moa_add.add_list(points, infos=infos)
        self.assertSetEqual({"A", "D"}, set(moa_add.infos))

    def test_add(self):
        """ test if the add_points function works correctly """
        ref_point = [6, 6]
        start_points = [[1, 3], [5, 1]]
        moa_ref = BiobjectiveNondominatedSortedList(start_points, ref_point, infos=["A", "B"])
        moa_no_ref = BiobjectiveNondominatedSortedList(start_points, infos=["A", "B"])

        for moa in [moa_ref, moa_no_ref]:
            # add point that is not dominated and does not dominate any other point
            u1 = [3, 2]
            moa.add(u1, info="C")
            self.assertSetEqual(list_to_set(start_points + [u1]), list_to_set(moa))
            self.assertSetEqual({"A", "B", "C"}, set(moa.infos))

            # add point that is dominated by another point in the archive
            u2 = [4, 4]
            moa.add(u2, info="D")
            self.assertSetEqual(list_to_set(start_points + [u1]), list_to_set(moa))
            self.assertSetEqual({"A", "B", "C"}, set(moa.infos))

            # add point that dominates another point in the archive
            u3 = [2, 2]
            moa.add(u3, info="E")
            self.assertSetEqual(list_to_set(start_points + [u3]), list_to_set(moa))
            self.assertSetEqual({"A", "B", "E"}, set(moa.infos))

    def test_copy_MOArchive(self):
        """ Test the copy function of the MOArchive3obj class """
        points = [[1, 3], [2, 2], [3, 1]]
        moa = BiobjectiveNondominatedSortedList(points, reference_point=[6, 6])
        moa_copy = moa.copy()

        self.assertEqual(moa.hypervolume, moa_copy.hypervolume)

        moa.add([1.5, 1.5])
        moa_copy.add([0.5, 5])

        self.assertNotEqual(moa.hypervolume, moa_copy.hypervolume)
        self.assertEqual(len(moa), 3)
        self.assertEqual(len(moa_copy), 4)

    def test_hypervolume_plus(self):
        """ test the hypervolume_plus indicator """
        moa = BiobjectiveNondominatedSortedList(reference_point=[1, 1])
        self.assertEqual(moa.hypervolume_plus, -inf)

        moa.add([2, 2])
        self.assertEqual(moa.hypervolume_plus, -math.sqrt(2))

        moa.add_list([[0, 5], [1, 2], [3, 2]])
        self.assertEqual(moa.hypervolume_plus, -1)

        moa.add([1, 1])
        self.assertEqual(moa.hypervolume_plus, 0)

        moa.add([0.5, 0.5])
        self.assertEqual(moa.hypervolume_plus, moa.hypervolume)

        moa = BiobjectiveNondominatedSortedList(reference_point=[1, 1])
        prev_hv_plus = moa.hypervolume_plus
        for i in range(1000):
            point = [10 * random.random(), 10 * random.random()]
            moa.add(point)
            self.assertLessEqual(prev_hv_plus, moa.hypervolume_plus)
            prev_hv_plus = moa.hypervolume_plus


if __name__ == '__main__':
    unittest.main()
