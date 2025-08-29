""" Test the MOArchive3obj class """
import math

from moarchiving.get_archive import get_mo_archive, get_cmo_archive
from moarchiving.tests.point_sampling import get_non_dominated_points

import unittest
import random


class TestNormalization(unittest.TestCase):
    def test_weights_ideal_point_easy_2dim(self):
        """ test the hypervolume after changing weights and ideal point in 2D """
        points = [[2, 1], [1, 4]]
        moa = get_mo_archive(points, reference_point=[5, 5])
        self.assertEqual(moa.hypervolume, 13)

        moa.ideal_point([0, 0])
        self.assertAlmostEqual(moa.hypervolume, 13 / 25)

        moa.weights([0.5, 2])
        self.assertAlmostEqual(moa.hypervolume, 13 / 25)

        moa.weights([2, 3])
        self.assertAlmostEqual(moa.hypervolume, (13 / 25) * 6)

        moa.ideal_point([1, 1])
        self.assertAlmostEqual(moa.hypervolume, (13 / 16) * 6)

    def test_weights_ideal_point_easy_3dim(self):
        """ test the hypervolume after changing weights and ideal point in 3D """
        points = [[1, 2, 3], [3, 2, 1]]
        moa = get_mo_archive(points, reference_point=[4, 4, 4])
        self.assertEqual(moa.hypervolume, 10)

        moa.ideal_point([0, 0, 0])
        self.assertAlmostEqual(moa.hypervolume, 10 / (4 * 4 * 4))

        moa.weights([0.5, 2, 1])
        self.assertAlmostEqual(moa.hypervolume, 10 / (4 * 4 * 4))

        moa.weights([2, 3, 0.5])
        self.assertAlmostEqual(moa.hypervolume, (10 / (4 * 4 * 4)) * 3)

        moa.ideal_point([1, 1, 1])
        self.assertAlmostEqual(moa.hypervolume, (10 / (3 * 3 * 3)) * 3)

    def test_weights_ideal_point_easy_4dim(self):
        """ test the hypervolume after changing weights and ideal point in 4D """
        points = [[1, 2, 3, 4], [4, 3, 2, 1]]
        moa = get_mo_archive(points, reference_point=[5, 5, 5, 5])
        self.assertEqual(moa.hypervolume, 44)

        moa.ideal_point([0, 0, 0, 0])
        self.assertAlmostEqual(moa.hypervolume, 44 / (5 ** 4))

        moa.weights([0.5, 2, 3, 1/3])
        self.assertAlmostEqual(moa.hypervolume, (44 / (5 ** 4)))

        moa.weights([0.2, 3, 0.5, 5])
        self.assertAlmostEqual(moa.hypervolume, (44 / (5 ** 4)) * 1.5)

        moa.ideal_point([1, 1, 1, 1])
        self.assertAlmostEqual(moa.hypervolume, (44 / (4 ** 4)) * 1.5)

    def test_hypervolume_after_weights_change(self):
        """ test the hypervolume after weights update """
        for dim in [2, 3, 4]:
            points = get_non_dominated_points(100, n_dim=dim)
            moa = get_mo_archive(points, reference_point=[1] * dim)
            hv = moa.hypervolume
            moa.weights([2] * dim)
            self.assertAlmostEqual(moa.hypervolume, hv * (2 ** dim))
            moa.weights([0.5] * dim)
            self.assertAlmostEqual(moa.hypervolume, hv / (2 ** dim))

            random_weights = [random.random() for _ in range(dim)]
            moa.weights(random_weights)

            moa2 = get_mo_archive(points, reference_point=[1] * dim, weights=random_weights)
            self.assertAlmostEqual(moa2.hypervolume, moa.hypervolume)

    def test_hypervolume_after_ideal_point_change(self):
        """ test the hypervolume after ideal point update """
        for dim in [2, 3, 4]:
            points = get_non_dominated_points(100, n_dim=dim)
            moa = get_mo_archive(points, reference_point=[1] * dim)
            hv = moa.hypervolume
            moa.ideal_point([-1] * dim)
            self.assertEqual(moa.hypervolume, hv / (2 ** dim))

    def test_hypervolume_improvement(self):
        """test the hypervolume improvement of a point, when using weights and ideal point"""
        # 2D
        moa = get_mo_archive([[1, 3], [3, 1]], reference_point=[4, 4])
        self.assertAlmostEqual(moa.hypervolume_improvement([2, 2]), 1)
        self.assertAlmostEqual(moa.hypervolume_improvement([3.5, 3.5]), -math.sqrt(0.5))

        moa.weights([2, 1])
        self.assertAlmostEqual(moa.hypervolume_improvement([2, 2]), 2)
        self.assertAlmostEqual(moa.hypervolume_improvement([3.5, 3.5]), -math.sqrt(1.25))

        moa.ideal_point([0, 0])
        self.assertAlmostEqual(moa.hypervolume_improvement([2, 2]), 2 / 16)
        self.assertAlmostEqual(moa.hypervolume_improvement([3.5, 3.5]), -math.sqrt((1/8)**2 + (1/4)**2))

        # 3D
        moa = get_mo_archive([[1, 2, 3], [3, 2, 1]], reference_point=[4, 4, 4])
        self.assertAlmostEqual(moa.hypervolume_improvement([2, 2, 2]), 2)
        self.assertAlmostEqual(moa.hypervolume_improvement([3.5, 3.5, 3.5]), -math.sqrt(0.5))

        moa.weights([2, 3, 5])
        self.assertAlmostEqual(moa.hypervolume_improvement([2, 2, 2]), 2 * (2 * 3 * 5))
        self.assertAlmostEqual(moa.hypervolume_improvement([3.5, 3.5, 3.5]), -math.sqrt((2/2)**2 + (5/2)**2))

        moa.ideal_point([0, 0, 0])
        self.assertAlmostEqual(moa.hypervolume_improvement([2, 2, 2]), 2 * (2 * 3 * 5) / (4 ** 3))
        self.assertAlmostEqual(moa.hypervolume_improvement([3.5, 3.5, 3.5]), -math.sqrt((2/8)**2 + (5/8)**2))

        # 4D
        moa = get_mo_archive([[1, 2, 3, 4], [4, 3, 2, 1]], reference_point=[5, 5, 5, 5])
        self.assertAlmostEqual(moa.hypervolume_improvement([2, 2, 2, 2]), 49)
        self.assertAlmostEqual(moa.hypervolume_improvement([4.5, 4.5, 4.5, 4.5]), -math.sqrt(0.5))

        moa.weights([2, 3, 5, 7])
        self.assertAlmostEqual(moa.hypervolume_improvement([2, 2, 2, 2]), 49 * (2 * 3 * 5 * 7))
        self.assertAlmostEqual(moa.hypervolume_improvement([4.5, 4.5, 4.5, 4.5]), -math.sqrt((2/2)**2 + (7/2)**2))

        moa.ideal_point([0, 0, 0, 0])
        self.assertAlmostEqual(moa.hypervolume_improvement([2, 2, 2, 2]), 49 * (2 * 3 * 5 * 7) / (5 ** 4))
        self.assertAlmostEqual(moa.hypervolume_improvement([4.5, 4.5, 4.5, 4.5]), -math.sqrt((2/10)**2 + (7/10)**2))


    def test_contributing_hypervolume(self):
        """test the contributing_hypervolume function with different weights and ideal points"""
        # 2D
        moa = get_mo_archive([[1, 3], [2, 2], [3, 1]], reference_point=[4, 4])
        self.assertAlmostEqual(moa.contributing_hypervolume([2, 2]), 1)
        self.assertAlmostEqual(moa.contributing_hypervolume(1), 1)
        self.assertAlmostEqual(moa.contributing_hypervolume([1, 1]), 3)

        moa.weights([3, 5])
        self.assertAlmostEqual(moa.contributing_hypervolume([2, 2]), 15)
        self.assertAlmostEqual(moa.contributing_hypervolume(1), 15)
        self.assertAlmostEqual(moa.contributing_hypervolume([1, 1]), 45)

        moa.ideal_point([0, 0])
        self.assertAlmostEqual(moa.contributing_hypervolume([2, 2]), 15/16)
        self.assertAlmostEqual(moa.contributing_hypervolume(1), 15/16)
        self.assertAlmostEqual(moa.contributing_hypervolume([1, 1]), 45/16)

        # 3D
        moa = get_mo_archive([[1, 2, 3], [3, 1, 2], [2, 3, 1]], reference_point=[4, 4, 4])
        self.assertAlmostEqual(moa.contributing_hypervolume([1, 2, 3]), 3)
        self.assertAlmostEqual(moa.contributing_hypervolume([1, 1, 1]), 14)

        moa.weights([2, 3, 5])
        self.assertAlmostEqual(moa.contributing_hypervolume([1, 2, 3]), 3 * 2 * 3 * 5)
        self.assertAlmostEqual(moa.contributing_hypervolume([1, 1, 1]), 14 * 2 * 3 * 5)

        moa.ideal_point([0, 0, 0])
        self.assertAlmostEqual(moa.contributing_hypervolume([1, 2, 3]), 3 * 2 * 3 * 5 / 64)
        self.assertAlmostEqual(moa.contributing_hypervolume([1, 1, 1]), 14 * 2 * 3 * 5 / 64)

        # 4D
        moa = get_mo_archive([[1, 2, 3, 4], [3, 4, 1, 2], [2, 3, 4, 1], [4, 1, 2, 3]],
                             reference_point=[5, 5, 5, 5])
        self.assertAlmostEqual(moa.contributing_hypervolume([1, 2, 3, 4]), 13)
        self.assertAlmostEqual(moa.contributing_hypervolume([2, 2, 2, 2]), 34)

        moa.weights([2, 3, 5, 0.1])
        self.assertAlmostEqual(moa.contributing_hypervolume([1, 2, 3, 4]), 13 * 3)
        self.assertAlmostEqual(moa.contributing_hypervolume([2, 2, 2, 2]), 34 * 3)

        moa.ideal_point([0, 0, 0, 0])
        self.assertAlmostEqual(moa.contributing_hypervolume([1, 2, 3, 4]), 13 * 3 / 625)
        self.assertAlmostEqual(moa.contributing_hypervolume([2, 2, 2, 2]), 34 * 3 / 625)

    def test_hypervolume_plus(self):
        """ test the hypervolume_plus indicator with different weights and ideal points  """
        for get_archive, kwargs in zip([get_mo_archive, get_cmo_archive],
                                       [{}, {"list_of_g_vals": [0, 0]}]):
            # test weights only
            moa = get_archive([[2, 2], [1, 4]], reference_point=[1, 1], weights=[1, 1],
                              **kwargs)
            self.assertEqual(moa.hypervolume_plus, -math.sqrt(2))

            moa = get_archive([[2, 2], [1, 4]], reference_point=[1, 1], weights=[3, 1],
                              **kwargs)
            self.assertEqual(moa.hypervolume_plus, -3)

            moa = get_archive([[2, 2], [1, 4]], reference_point=[1, 1], weights=[1, 3],
                              **kwargs)
            self.assertEqual(moa.hypervolume_plus, -math.sqrt(10))

            moa.add_list([[0, 5], [3, 1.5]], **kwargs)
            self.assertEqual(moa.hypervolume_plus, -math.sqrt(2 ** 2 + 1.5 ** 2))

            moa.add_list([[1, 3], [0.4, 1]], **kwargs)
            self.assertEqual(moa.hypervolume_plus, 0)

            moa.add_list([[0.5, 0.5], [0.8, 0.7]], **kwargs)
            self.assertEqual(moa.hypervolume_plus, 0.5 ** 2 * 3)

            # test ideal point only
            moa = get_archive([[2, 2], [1, 4]], reference_point=[1, 1],
                              ideal_point=[-1, -1], **kwargs)
            self.assertEqual(moa.hypervolume_plus, -math.sqrt(0.5))

            moa = get_archive([[2, 2], [1, 4]], reference_point=[1, 1],
                              ideal_point=[-3, -1], **kwargs)
            self.assertEqual(moa.hypervolume_plus, -math.sqrt(0.5**2 + 0.25**2))

            moa = get_archive([[2, 2], [1, 4]], reference_point=[1, 1],
                              ideal_point=[-1, -3], **kwargs)
            self.assertEqual(moa.hypervolume_plus, -math.sqrt(0.5**2 + 0.25**2))

            moa.add_list([[3, 1.5], [0, 3]], **kwargs)
            self.assertEqual(moa.hypervolume_plus, -0.5)

            moa.add_list([[1, 3], [0.4, 1]], **kwargs)
            self.assertEqual(moa.hypervolume_plus, 0)

            moa.add_list([[0.5, 0.5], [0.8, 0.7]], **kwargs)
            self.assertEqual(moa.hypervolume_plus, 0.5 ** 2 / 8)

            # test both weights and ideal point
            moa = get_archive([[2, 2], [1, 4]], reference_point=[1, 1], ideal_point=[-1, -2],
                              weights=[7, 2], **kwargs)
            self.assertEqual(moa.hypervolume_plus, -2)

            moa.add_list([[0, 5], [1.5, 1.5]], **kwargs)
            self.assertEqual(moa.hypervolume_plus, -math.sqrt((1/4 * 7) ** 2 + (1/6 * 2) ** 2))

            moa.add_list([[1, 3], [0.4, 1]], **kwargs)
            self.assertEqual(moa.hypervolume_plus, 0)

            moa.add_list([[0.5, 0.5], [0.8, 0.7]], **kwargs)
            self.assertEqual(moa.hypervolume_plus, (1/4 * 1/6) * 2 * 7)

    def test_hypervolume_plus_constr(self):
        """test the hypervolume_plus_constr indicator with different weights and ideal points"""
        moa = get_cmo_archive([[2, 2], [1, 4]], list_of_g_vals=[[5, 3], [1, 2]],
                              reference_point=[1, 1], weights=[1, 1])
        self.assertAlmostEqual(moa.hypervolume_plus_constr, -(1 + (1 + 2)))

        moa.add([0, 5], [1, 0])
        self.assertAlmostEqual(moa.hypervolume_plus_constr, -(1 + 1))

        moa.add([3, 1], [0, 0])
        self.assertAlmostEqual(moa.hypervolume_plus_constr, -(1 + 0))

        moa.add([0.5, 0.5], [0, 0])
        self.assertAlmostEqual(moa.hypervolume_plus_constr, 0.25)

        moa = get_cmo_archive([[11, 7], [8, 9]], list_of_g_vals=[[0.5, 30], [0.1, 100]],
                              reference_point=[10, 10], ideal_point=[4, 2], weights=[7, 2],
                              tau=2, max_g_vals=[1, 100])
        self.assertAlmostEqual(moa.hypervolume_plus_constr, -(2 + 0.8))

        moa.add([4, 14], [0.2, 30])
        self.assertAlmostEqual(moa.hypervolume_plus_constr, -(2 + 0.5))

        moa.add([30, 50], [0, 0])
        self.assertAlmostEqual(moa.hypervolume_plus_constr, -2)

        moa.add([11, 5], [0, 0])
        self.assertAlmostEqual(moa.hypervolume_plus_constr, -7/6)

        moa.add([1, 11], [0, 0])
        self.assertAlmostEqual(moa.hypervolume_plus_constr, -1/4)

        moa.add([10.1, 10.1], [0, 0])
        self.assertAlmostEqual(moa.hypervolume_plus_constr, -((0.7/6) ** 2 + (0.2/8) ** 2) ** 0.5)

        moa.add([3, 3], [-6, 0.2])
        self.assertAlmostEqual(moa.hypervolume_plus_constr, -((0.7/6) ** 2 + (0.2/8) ** 2) ** 0.5)

        moa.add([5, 7], [0, 0])
        self.assertAlmostEqual(moa.hypervolume_plus_constr, (15/48) * (2 * 7))


if __name__ == '__main__':
    unittest.main()
