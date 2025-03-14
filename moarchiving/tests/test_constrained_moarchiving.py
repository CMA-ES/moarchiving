""" Test the CMOArchive class """

from moarchiving.get_archive import get_cmo_archive

import unittest
import random


def list_to_set(lst):
    """ Converts a list of lists to a set of tuples """
    return set([tuple(p) for p in lst])


class TestCMOArchiving(unittest.TestCase):
    """ Tests for the CMOArchive class """

    def test_hypervolume_easy(self):
        """ test the hypervolume calculation for a simple case """
        f_vals = [[1, 2, 3], [2, 3, 1], [3, 1, 2]]
        g_vals = [0, 0, 0]
        moa = get_cmo_archive(f_vals, g_vals, reference_point=[4, 4, 4], infos=["A", "B", "C"])
        self.assertEqual(moa.hypervolume, 13)
        self.assertEqual(moa.infos, ["B", "C", "A"])

        g_vals = [[0], [1], [0]]
        moa = get_cmo_archive(f_vals, g_vals, reference_point=[4, 4, 4], infos=["A", "B", "C"])
        self.assertEqual(moa.hypervolume, 10)
        self.assertEqual(moa.infos, ["C", "A"])

    def test_infos_dominated(self):
        """ test if the infos about dominated points are removed """
        f_vals = [[1, 2, 3], [3, 2, 1], [2, 3, 4], [2, 1, 0], [0, 0, 0]]
        g_vals = [[0, 0],  [0, 0], [0, 10], [0, 0], [9, 1]]
        infos = ["A", "B", "C", "D", "E"]

        moa = get_cmo_archive(f_vals, g_vals, [6, 6, 6], infos)
        # assert that only points A and D are stored in the archive
        self.assertSetEqual({"A", "D"}, set(moa.infos))

    def test_add(self):
        """ test if the add_points function works correctly """
        ref_point = [6, 6]
        f_vals = [[1, 2], [3, 4], [5, 1]]
        g_vals = [42, 0, 0]
        moa_ref = get_cmo_archive(f_vals, g_vals, ref_point)
        moa_no_ref = get_cmo_archive(f_vals, g_vals)
        for moa in [moa_ref, moa_no_ref]:
            # add point that is not dominated and does not dominate any other point
            moa.add([1, 5], [0])
            self.assertEqual([[1, 5], [3, 4], [5, 1]], list(moa))

            # add point that is dominated by another point in the archive
            moa.add([4, 4], [0])
            self.assertEqual([[1, 5], [3, 4], [5, 1]], list(moa))

            # add point that dominates another point in the archive
            moa.add([3, 3], [0])
            self.assertEqual([[1, 5], [3, 3], [5, 1]], list(moa))

            # don't add point, because it is not feasible
            moa.add([1, 1], [1])
            self.assertEqual([[1, 5], [3, 3], [5, 1]], list(moa))

            # do not add point with that have any constraint violation > 0
            moa.add([2, 2], [-3, 2])
            self.assertEqual([[1, 5], [3, 3], [5, 1]], list(moa))

    def test_copy_CMOArchive(self):
        """ Test the copy function of the CMOArchive class """
        f_vals = [[1, 2, 3], [2, 3, 1], [3, 1, 2]]
        g_vals = [0, 0, 0]
        moa = get_cmo_archive(f_vals, g_vals, reference_point=[6, 6, 6])
        moa_copy = moa.copy()

        self.assertEqual(moa.hypervolume_plus_constr, moa_copy.hypervolume_plus_constr)

        moa.add([2, 2, 2], 0)

        self.assertEqual(len(moa), 4)
        self.assertEqual(len(moa_copy), 3)
        self.assertFalse(moa.hypervolume_plus_constr == moa_copy.hypervolume_plus_constr)

    def test_remove(self, n_points=100, n_points_remove=50):
        """ Test the remove function, by comparing the archive with 100 points added and then
        50 removed, to the with only the other 50 points added """
        f_vals = [[1, 2, 3], [2, 3, 1], [3, 1, 2]]
        moa_remove = get_cmo_archive(f_vals, [0, 0, 0], reference_point=[6, 6, 6])
        moa_remove.remove([1, 2, 3])
        self.assertEqual(len(moa_remove), 2)
        self.assertSetEqual(list_to_set(list(moa_remove)), list_to_set(f_vals[1:]))

    def test_hypervolume_plus_constr(self):
        """ test the hypervolume_plus_constr indicator """
        moa = get_cmo_archive(reference_point=[1, 1, 1], tau=10)
        self.assertEqual(moa.hypervolume_plus_constr, -float('inf'))

        moa.add([2, 2, 2], 99)
        self.assertEqual(moa.hypervolume_plus_constr, - 99 - 10)

        moa.add_list([[0, 0, 5], [1, 2, 1], [3, 3, 2]], [14, 7, 76])
        self.assertEqual(moa.hypervolume_plus_constr, -7 - 10)

        moa.add([20, 2, 20], 0)
        self.assertEqual(moa.hypervolume_plus_constr, -10)

        moa.add_list([[0, 0, 0], [4, 5, 1]], [3, 0])
        self.assertEqual(moa.hypervolume_plus_constr, -5)

        moa.add([1, 1, 1], 0)
        self.assertEqual(moa.hypervolume_plus_constr, 0)

        moa.add([0.5, 0.5, 0.5], 0)
        self.assertEqual(moa.hypervolume_plus_constr, moa.hypervolume)

        moa = get_cmo_archive(reference_point=[1, 1, 1], tau=1)
        prev_hv_plus_constr = moa.hypervolume_plus_constr
        for i in range(1000):
            f_vals = [10 * random.random(), 5 * random.random(), random.random()]
            g_vals = max(random.random() - 0.3, 0)
            hv_plus_constr_improvement = moa.hypervolume_plus_constr_improvement(f_vals, g_vals)
            moa.add(f_vals, g_vals)
            self.assertLessEqual(prev_hv_plus_constr, moa.hypervolume_plus_constr)
            self.assertAlmostEqual(moa.hypervolume_plus_constr - prev_hv_plus_constr,
                                   hv_plus_constr_improvement, places=8)
            prev_hv_plus_constr = moa.hypervolume_plus_constr


if __name__ == '__main__':
    unittest.main()
