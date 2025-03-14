""" Test the MOArchive4obj class """

from moarchiving.moarchiving3obj import MOArchive3obj
from moarchiving.moarchiving4obj import MOArchive4obj
from moarchiving.moarchiving import BiobjectiveNondominatedSortedList as MOArchive2obj
from moarchiving.tests.point_sampling import (get_non_dominated_points, get_stacked_points,
                                              get_random_points, permute_points)

import unittest
import random
import math


def list_to_set(lst):
    """ Converts a list of lists to a set of tuples """
    return set([tuple(p) for p in lst])


def get_small_test_archive():
    """ Returns a small test archive """
    points = [[1, 2, 3, 4], [4, 1, 2, 3], [3, 4, 1, 2], [2, 3, 4, 1]]
    infos = [str(p) for p in points]
    return MOArchive4obj(points, [6, 6, 6, 6], infos)


class TestMOArchiving4obj(unittest.TestCase):
    """ Tests for the MOArchive4obj class """
    def test_hypervolume_easy(self):
        """ test the hypervolume calculation for a 'simple' case """
        points = [[0, 1, 2, 3], [1, 2, 3, 0], [2, 3, 0, 1], [3, 0, 1, 2]]
        moa = MOArchive4obj(points, reference_point=[4, 4, 4, 4], infos=["A", "B", "C", "D"])
        self.assertEqual(71, moa.hypervolume)

    def test_infos_non_dominated(self):
        """ test if the infos are stored correctly - if the points are non dominated,
        the infos should be the same"""
        moa = get_small_test_archive()
        # assert that the infos are stored in the same order as the points
        self.assertEqual([str(p) for p in moa], moa.infos)

    def test_infos_dominated(self):
        """ test if the infos about dominated points are removed """
        points = [[1, 2, 3, 4], [2, 2, 3, 5], [5, 4, 3, 2], [5, 5, 5, 5]]
        infos = [str(p) for p in points]
        moa = MOArchive4obj(points, [6, 6, 6, 6], infos)

        non_dominated_points = [[1, 2, 3, 4], [5, 4, 3, 2]]
        self.assertSetEqual(set([str(p) for p in non_dominated_points]), set(moa.infos))
        self.assertEqual([str(p) for p in moa], moa.infos)

    def test_in_domain(self):
        """ test if the in_domain function works correctly for 3obj points"""
        moa = get_small_test_archive()

        # test if the points are in the domain
        self.assertTrue(moa.in_domain([1, 2, 3, 4]))
        self.assertTrue(moa.in_domain([5.9, 5.9, 5.9, 5.9]))
        self.assertTrue(moa.in_domain([-1, -1, -1, -1]))
        self.assertTrue(moa.in_domain([-1, 1, -1, 1]))
        self.assertTrue(moa.in_domain([0, 0, 0, 0]))
        # test if the point is not in the domain
        self.assertFalse(moa.in_domain([7, 8, 9, 10]))
        self.assertFalse(moa.in_domain([6, 6, 6, 6]))
        self.assertFalse(moa.in_domain([0, 0, 6, 0]))

    def test_add(self):
        """ test if the add_points function works correctly for 4obj points"""
        ref_point = [6, 6, 6, 6]
        start_points = [[1, 2, 5, 4], [2, 3, 5, 1], [3, 5, 1, 4]]
        moa_ref = MOArchive4obj(start_points, ref_point, infos=["A", "B", "C"])
        moa_no_ref = MOArchive4obj(start_points, infos=["A", "B", "C"])

        for moa in [moa_ref, moa_no_ref]:
            # add point that is not dominated and does not dominate any other point
            u1 = [3, 3, 3, 3]
            moa.add(u1, "D")
            self.assertSetEqual(list_to_set(start_points + [u1]), list_to_set(list(moa)))

            # add point that is dominated by another point in the archive
            u2 = [4, 5, 2, 4]
            moa.add(u2, "E")
            self.assertSetEqual(list_to_set(start_points + [u1]), list_to_set(list(moa)))

            # add point that dominates another point in the archive
            u3 = [2, 3, 1, 4]
            moa.add(u3, "F")
            self.assertSetEqual(list_to_set(start_points[:2] + [u1, u3]), list_to_set(list(moa)))

    def test_hypervolume_after_add(self):
        """ test if the hypervolume is calculated correctly after adding points """
        ref_point = [1, 1, 1, 1]

        pop_size = 20
        n_gen = 4
        points = get_non_dominated_points(pop_size * n_gen, n_dim=4)

        for gen in range(1, n_gen + 1):
            moa_true = MOArchive4obj(points[:(gen * pop_size)], ref_point)
            true_hv = moa_true.hypervolume

            moa_add = MOArchive4obj([], ref_point)
            for i in range(gen * pop_size):
                moa_add.add(points[i])

            moa_add_list = MOArchive4obj([], ref_point)
            for i in range(gen):
                moa_add_list.add_list(points[i * pop_size:(i + 1) * pop_size])

            self.assertAlmostEqual(moa_add.hypervolume, true_hv, places=6)
            self.assertAlmostEqual(moa_add_list.hypervolume, true_hv, places=6)
            self.assertEqual(len(moa_add), len(moa_true))
            self.assertEqual(len(moa_add_list), len(moa_true))

    def test_length(self):
        """ Test that the length of the archive is correct after adding and removing points """
        ref_point = [1, 1, 1, 1]

        n_points_add = 100
        points = get_stacked_points(n_points_add, ['random', 'random', 'random', 'random'])
        moa = MOArchive4obj([], ref_point)

        # add points one by one
        for point in points:
            moa.add(point)
            self.assertEqual(len(moa), len(list(moa)))

        # remove points one by one
        points = list(moa)
        for point in points:
            moa.remove(point)
            self.assertEqual(len(moa), len(list(moa)))

    def test_dominates(self):
        """ test the dominates function """
        moa = get_small_test_archive()

        # test that the points that are already in the archive are dominated
        for p in moa:
            self.assertTrue(moa.dominates(p))

        # test other dominated points
        self.assertTrue(moa.dominates([5, 5, 5, 5]))
        self.assertTrue(moa.dominates([2, 3, 4, 5]))
        self.assertTrue(moa.dominates([4, 5, 2, 3]))

        # test non dominated points
        self.assertFalse(moa.dominates([3, 3, 3, 3]))
        self.assertFalse(moa.dominates([5, 3, 3, 2]))
        self.assertFalse(moa.dominates([0, 5, 5, 5]))

    def test_dominators(self):
        """ test the dominators function """
        moa = get_small_test_archive()

        # test that the points that are already in the archive are dominated by itself
        for p in moa:
            self.assertEqual([p], moa.dominators(p))
            self.assertEqual(1, moa.dominators(p, number_only=True))

        # test other dominated points
        pass

    def test_distance_to_hypervolume_area(self):
        """ test the distance_to_hypervolume_area function """
        moa = MOArchive4obj()
        self.assertEqual(0, moa.distance_to_hypervolume_area([1, 1, 1, 1]))

        moa.reference_point = [2, 2, 2, 2]
        # for points in the hypervolume area, the distance should be 0
        self.assertEqual(0, moa.distance_to_hypervolume_area([0, 0, 0, 0]))
        self.assertEqual(0, moa.distance_to_hypervolume_area([1, 1, 1, 1]))
        self.assertEqual(0, moa.distance_to_hypervolume_area([2, 2, 2, 2]))
        self.assertEqual(0, moa.distance_to_hypervolume_area([0, 1, 2, 2]))

        # for points outside the hypervolume area, the distance should be the Euclidean distance
        # to the hypervolume area
        self.assertEqual(1, moa.distance_to_hypervolume_area([2, 2, 3, 2]))
        self.assertEqual(1, moa.distance_to_hypervolume_area([2, 0, 3, 2]))
        self.assertEqual(10, moa.distance_to_hypervolume_area([0, 0, 0, 12]))

        self.assertAlmostEqual(math.sqrt(2),
                               moa.distance_to_hypervolume_area([0, 3, 3, 0]), places=6)
        self.assertAlmostEqual(math.sqrt(2),
                               moa.distance_to_hypervolume_area([2, 3, 3, 2]), places=6)
        self.assertAlmostEqual(math.sqrt(4),
                               moa.distance_to_hypervolume_area([3, 3, 3, 3]), places=6)
        self.assertAlmostEqual(math.sqrt(7**2 * 4),
                               moa.distance_to_hypervolume_area([9, 9, 9, 9]), places=6)

    def test_distance_to_pareto_front_compare_2obj(self):
        """ test the distance_to_pareto_front function, by comparing it to the 2obj pareto front """
        # first make a pseudo 4obj pareto front and compare it to 2obj pareto front
        n_points = 100
        n_test_points = 100
        # set random seed
        points = get_stacked_points(n_points, ['random', 'random', 0, 0])

        moa4obj = MOArchive4obj(points, reference_point=[1, 1, 1, 1])
        moa2obj = MOArchive2obj([[p[0], p[1]] for p in points], reference_point=[1, 1])

        permutations = [[0, 1, 2, 3], [1, 2, 0, 3], [2, 0, 1, 3], [3, 2, 1, 0], [2, 3, 0, 1]]
        for permutation in permutations:
            perm_points = permute_points(points, permutation)
            moa4obj_perm = MOArchive4obj(perm_points, reference_point=[1, 1, 1, 1])

            new_points = get_stacked_points(n_test_points, ['random', 'random', 1, 1])
            for point in new_points:
                d2 = moa2obj.distance_to_pareto_front(point[:2])
                d4 = moa4obj.distance_to_pareto_front(point)
                d4_perm = moa4obj_perm.distance_to_pareto_front(permute_points([point],
                                                                             permutation)[0])
                self.assertAlmostEqual(d2, d4, places=8)
                self.assertAlmostEqual(d4, d4_perm, places=8)

    def test_distance_to_pareto_front_compare_3obj(self):
        """ test the distance_to_pareto_front function, by comparing it to the 3obj pareto front """
        # first make a pseudo 4obj pareto front and compare it to 3obj pareto front
        n_points = 100
        n_test_points = 10
        # set random seed
        points = get_stacked_points(n_points, ['random', 'random', 'random', 0])

        moa4obj = MOArchive4obj(points, reference_point=[1, 1, 1, 1])
        moa3obj = MOArchive3obj([[p[0], p[1], p[2]] for p in points], reference_point=[1, 1, 1])

        permutations = [[0, 1, 2, 3], [1, 2, 3, 0], [2, 0, 1, 3], [3, 2, 1, 0], [2, 3, 0, 1]]
        for permutation in permutations:
            perm_points = permute_points(points, permutation)
            moa4obj_perm = MOArchive4obj(perm_points, reference_point=[1, 1, 1, 1])

            new_points = get_stacked_points(n_test_points, ['random', 'random', 'random', 1])
            for point in new_points:
                d3 = moa3obj.distance_to_pareto_front(point[:3])
                d4 = moa4obj.distance_to_pareto_front(point)
                d4_perm = moa4obj_perm.distance_to_pareto_front(permute_points([point],
                                                                             permutation)[0])
                self.assertAlmostEqual(d3, d4, places=8)
                self.assertAlmostEqual(d4, d4_perm, places=8)

    def test_distance_to_pareto_front(self):
        """ test the distance_to_pareto_front function, by randomly sampling points and
        computing the distance to the selected point """
        n_points_archive = 100
        n_test_points = 50
        n_points_sampled = 1000
        # set random seed
        points = get_non_dominated_points(n_points_archive, n_dim=4)
        moa = MOArchive4obj(points, reference_point=[1, 1, 1, 1])

        for i in range(n_test_points):
            point = get_random_points(1, 4)[0]
            while not moa.dominates(point):
                point = get_random_points(1, 4)[0]
            distance = moa.distance_to_pareto_front(point)

            min_dist = 2
            for j in range(n_points_sampled):
                sample = [p + random.gauss(0, distance) for p in point]
                while moa.dominates(sample):
                    sample = [p + random.gauss(0, distance) for p in point]

                dist = math.sqrt(sum([(p - s) ** 2 for p, s in zip(point, sample)]))
                if dist < min_dist:
                    min_dist = dist
                self.assertTrue(distance <= dist)

    def test_remove(self, n_points=100, n_points_remove=50):
        """ Test the remove function, by comparing the archive with 100 non-dominated points added
        and then 50 removed, to the one with only the other 50 points added """
        points = [[1, 2, 3, 4], [2, 3, 4, 1], [3, 4, 1, 2]]
        moa_remove = MOArchive4obj(points, reference_point=[6, 6, 6, 6])
        moa_remove.remove([1, 2, 3, 4])
        self.assertEqual(len(list(moa_remove)), 2)
        self.assertSetEqual(list_to_set(list(moa_remove)), list_to_set(points[1:]))
        self.assertEqual(moa_remove.hypervolume,
                         MOArchive4obj(points[1:], reference_point=[6, 6, 6, 6]).hypervolume)

        points = get_non_dominated_points(n_points, n_dim=4)

        remove_idx = list(range(n_points_remove))
        keep_idx = [i for i in range(n_points) if i not in remove_idx]

        moa_true = MOArchive4obj([points[i] for i in keep_idx], reference_point=[1, 1, 1, 1])
        moa_remove = MOArchive4obj(points, reference_point=[1, 1, 1, 1])
        for i in remove_idx:
            moa_remove.remove(points[i])
            self.assertEqual(len(list(moa_remove)), len(moa_remove))

        moa_add = MOArchive4obj([], reference_point=[1, 1, 1, 1])
        for i in keep_idx:
            moa_add.add(points[i])

        # assert that the points are the same in all archives and the hypervolume is the same
        self.assertEqual(len(list(moa_add)), len(list(moa_true)))
        self.assertEqual(len(list(moa_remove)), len(list(moa_true)))

        self.assertSetEqual(list_to_set(list(moa_remove)), list_to_set(list(moa_true)))
        self.assertSetEqual(list_to_set(list(moa_add)), list_to_set(list(moa_true)))

        self.assertEqual(moa_remove.hypervolume, moa_true.hypervolume)
        self.assertEqual(moa_add.hypervolume, moa_true.hypervolume)

        moa = MOArchive4obj([[1, 2, 3, 4], [2, 3, 4, 1], [3, 4, 1, 2]],
                            reference_point=[6, 6, 6, 6])
        moa.add([1, 1, 1, 1])
        moa.remove([1, 1, 1, 1])
        self.assertEqual(len(list(moa)), 0)

    def test_contributing_hypervolume(self):
        """ test the contributing_hypervolume function, by comparing it to the 3obj result """
        points = [[1, 2, 3, 4], [1, 2, 4, 3], [1, 3, 2, 4], [1, 3, 4, 2], [1, 4, 2, 3],
                  [1, 4, 3, 2], [2, 1, 3, 4], [2, 1, 4, 3], [2, 3, 1, 4], [2, 3, 4, 1],
                  [2, 4, 1, 3], [2, 4, 3, 1], [3, 1, 2, 4], [3, 1, 4, 2], [3, 2, 1, 4],
                  [3, 2, 4, 1], [3, 4, 1, 2], [3, 4, 2, 1], [4, 1, 2, 3], [4, 1, 3, 2],
                  [4, 2, 1, 3], [4, 2, 3, 1], [4, 3, 1, 2], [4, 3, 2, 1]]
        moa = MOArchive4obj(points, reference_point=[5, 5, 5, 5])
        for p in points:
            self.assertEqual(moa.contributing_hypervolume(list(p)), 1)

        points = get_stacked_points(100, [0, 'random', 'random', 'random'])

        moa = MOArchive4obj(points, reference_point=[1, 1, 1, 1])
        moa3obj = MOArchive3obj([[p[1], p[2], p[3]] for p in points], reference_point=[1, 1, 1])
        for p in moa3obj:
            self.assertAlmostEqual(moa.contributing_hypervolume([0] + p),
                                   moa3obj.contributing_hypervolume(p), places=8)

    def test_hypervolume_improvement(self):
        """ test the hypervolume_improvement function, by comparing it to the 3obj result """
        points = [[1, 2, 3, 4], [1, 2, 4, 3], [1, 3, 2, 4], [1, 3, 4, 2], [1, 4, 2, 3],
                  [1, 4, 3, 2], [2, 1, 3, 4], [2, 1, 4, 3], [2, 3, 1, 4], [2, 3, 4, 1],
                  [2, 4, 1, 3], [2, 4, 3, 1], [3, 1, 2, 4], [3, 1, 4, 2], [3, 2, 1, 4],
                  [3, 2, 4, 1], [3, 4, 1, 2], [3, 4, 2, 1], [4, 1, 2, 3], [4, 1, 3, 2],
                  [4, 2, 1, 3], [4, 2, 3, 1], [4, 3, 1, 2], [4, 3, 2, 1]]
        moa = MOArchive4obj(points, reference_point=[5, 5, 5, 5])
        self.assertEqual(moa.hypervolume_improvement([1, 2, 3, 4]), 0)
        self.assertEqual(moa.hypervolume_improvement([2, 3, 4, 1]), 0)
        self.assertEqual(moa.hypervolume_improvement([3, 4, 1, 2]), 0)
        self.assertEqual(moa.hypervolume_improvement([4, 4, 4, 4]),
                         -moa.distance_to_pareto_front([4, 4, 4, 4]))

        self.assertEqual(moa.hypervolume_improvement([1, 1, 1, 1]), 131)
        self.assertEqual(moa.hypervolume_improvement([2, 2, 2, 2]), 20)
        self.assertEqual(moa.hypervolume_improvement([3, 3, 3, 3]), 1)

        points = get_stacked_points(100, [0, 'random', 'random', 'random'])
        new_points = get_random_points(100, 3)
        moa = MOArchive4obj(points, reference_point=[1, 1, 1, 1])
        moa3obj = MOArchive3obj([[p[1], p[2], p[3]] for p in points], reference_point=[1, 1, 1])

        for p in new_points:
            hv_imp2obj = float(moa3obj.hypervolume_improvement(p))
            if hv_imp2obj > 0:
                self.assertAlmostEqual(hv_imp2obj, moa.hypervolume_improvement([0] + p), places=8)
            else:
                self.assertAlmostEqual(hv_imp2obj, moa.hypervolume_improvement([1] + p), places=8)

    def test_hypervolume_plus(self):
        """ test the hypervolume_plus indicator """
        moa = MOArchive4obj(reference_point=[1, 1, 1, 1])
        self.assertEqual(moa.hypervolume_plus, -float('inf'))

        moa.add([2, 2, 2, 2])
        self.assertEqual(moa.hypervolume_plus, -math.sqrt(4))

        moa.add_list([[0, 0, 0, 5], [1, 1, 2, 1], [0, 3, 3, 2]])
        self.assertEqual(moa.hypervolume_plus, -1)

        moa.add([1, 1, 1, 1])
        self.assertEqual(moa.hypervolume_plus, 0)

        moa.add([0.5, 0.5, 0.5, 0.5])
        self.assertEqual(moa.hypervolume_plus, moa.hypervolume)

        moa = MOArchive4obj(reference_point=[2, 2, 2, 2])
        prev_hv_plus = moa.hypervolume_plus
        for i in range(1000):
            point = [10 * random.random(), 10 * random.random(), 10 * random.random(),
                     10 * random.random()]
            moa.add(point)
            self.assertLessEqual(prev_hv_plus, moa.hypervolume_plus)
            prev_hv_plus = moa.hypervolume_plus

    def test_hypervolume(self):
        """ test the hypervolume calculation, by comparing to the result of original
        implementation in C"""
        points = [
            [1.0, 2.0, 3.0, 1.0],
            [4.0, 5.0, 6.0, 0.5],
            [7.0, 8.0, 9.0, 0.7],
            [2.0, 1.0, 0.5, 0.6],
            [3.0, 4.0, 5.0, 0.8],
            [6.0, 7.0, 8.0, 0.3],
            [9.0, 1.0, 2.0, 0.9],
            [5.0, 6.0, 7.0, 0.2],
            [8.0, 9.0, 1.0, 0.4],
            [0.0, 1.0, 2.0, 0.1]
        ]
        moa = MOArchive4obj(points, reference_point=[10, 10, 10, 10])
        self.assertEqual(8143.6, float(moa.hypervolume))
        self.assertEqual(moa.hypervolume_plus, moa.hypervolume)

        points = [
            [0.6394267984578837, 0.025010755222666936, 0.27502931836911926, 0.22321073814882275],
            [0.7364712141640124, 0.6766994874229113, 0.8921795677048454, 0.08693883262941615],
            [0.4219218196852704, 0.029797219438070344, 0.21863797480360336, 0.5053552881033624],
            [0.026535969683863625, 0.1988376506866485, 0.6498844377795232, 0.5449414806032167],
            [0.2204406220406967, 0.5892656838759087, 0.8094304566778266, 0.006498759678061017],
            [0.8058192518328079, 0.6981393949882269, 0.3402505165179919, 0.15547949981178155],
            [0.9572130722067812, 0.33659454511262676, 0.09274584338014791, 0.09671637683346401],
            [0.8474943663474598, 0.6037260313668911, 0.8071282732743802, 0.7297317866938179],
            [0.5362280914547007, 0.9731157639793706, 0.3785343772083535, 0.552040631273227],
            [0.8294046642529949, 0.6185197523642461, 0.8617069003107772, 0.577352145256762]
        ]
        moa = MOArchive4obj(points, reference_point=[1, 1, 1, 1])
        self.assertAlmostEqual(0.37037902191204, float(moa.hypervolume), places=8)
        self.assertEqual(moa.hypervolume_plus, moa.hypervolume)

        points = [
            [0.6394267984578837, 0.025010755222666936, 0.27502931836911926, 0.22321073814882275],
            [0.7364712141640124, 0.6766994874229113, 0.8921795677048454, 0.08693883262941615],
            [0.4219218196852704, 0.029797219438070344, 0.21863797480360336, 0.5053552881033624],
            [0.026535969683863625, 0.1988376506866485, 0.6498844377795232, 0.5449414806032167],
            [0.2204406220406967, 0.5892656838759087, 0.8094304566778266, 0.006498759678061017],
            [0.8058192518328079, 0.6981393949882269, 0.3402505165179919, 0.15547949981178155],
            [0.9572130722067812, 0.33659454511262676, 0.09274584338014791, 0.09671637683346401],
            [0.8474943663474598, 0.6037260313668911, 0.8071282732743802, 0.7297317866938179],
            [0.5362280914547007, 0.9731157639793706, 0.3785343772083535, 0.552040631273227],
            [0.8294046642529949, 0.6185197523642461, 0.8617069003107772, 0.577352145256762],
            [0.7045718362149235, 0.045824383655662215, 0.22789827565154686, 0.28938796360210717],
            [0.0797919769236275, 0.23279088636103018, 0.10100142940972912, 0.2779736031100921],
            [0.6356844442644002, 0.36483217897008424, 0.37018096711688264, 0.2095070307714877],
            [0.26697782204911336, 0.936654587712494, 0.6480353852465935, 0.6091310056669882],
            [0.171138648198097, 0.7291267979503492, 0.1634024937619284, 0.3794554417576478],
            [0.9895233506365952, 0.6399997598540929, 0.5569497437746462, 0.6846142509898746],
            [0.8428519201898096, 0.7759999115462448, 0.22904807196410437, 0.03210024390403776],
            [0.3154530480590819, 0.26774087597570273, 0.21098284358632646, 0.9429097143350544],
            [0.8763676264726689, 0.3146778807984779, 0.65543866529488, 0.39563190106066426],
            [0.9145475897405435, 0.4588518525873988, 0.26488016649805246, 0.24662750769398345],
            [0.5613681341631508, 0.26274160852293527, 0.5845859902235405, 0.897822883602477],
            [0.39940050514039727, 0.21932075915728333, 0.9975376064951103, 0.5095262936764645],
            [0.09090941217379389, 0.04711637542473457, 0.10964913035065915, 0.62744604170309],
            [0.7920793643629641, 0.42215996679968404, 0.06352770615195713, 0.38161928650653676],
            [0.9961213802400968, 0.529114345099137, 0.9710783776136181, 0.8607797022344981],
            [0.011481021942819636, 0.7207218193601946, 0.6817103690265748, 0.5369703304087952],
            [0.2668251899525428, 0.6409617985798081, 0.11155217359587644, 0.434765250669105],
            [0.45372370632920644, 0.9538159275210801, 0.8758529403781941, 0.26338905075109076],
            [0.5005861130502983, 0.17865188053013137, 0.9126278393448205, 0.8705185698367669],
            [0.2984447914486329, 0.6389494948660052, 0.6089702114381723, 0.1528392685496348],
            [0.7625108000751513, 0.5393790301196257, 0.7786264786305582, 0.5303536721951775],
            [0.0005718961279435053, 0.3241560570046731, 0.019476742385832302, 0.9290986162646171],
            [0.8787218778231842, 0.8316655293611794, 0.30751412540266143, 0.05792516649418755],
            [0.8780095992040405, 0.9469494452979941, 0.08565345206787878, 0.4859904633166138],
            [0.06921251846838361, 0.7606021652572316, 0.7658344293069878, 0.1283914644997628],
            [0.4752823780987313, 0.5498035934949439, 0.2650566289400591, 0.8724330410852574],
            [0.4231379402008869, 0.21179820544208205, 0.5392960887794583, 0.7299310690899762],
            [0.2011510633896959, 0.31171629130089495, 0.9951493566608947, 0.6498780576394535],
            [0.43810008391450406, 0.5175758410355906, 0.12100419586826572, 0.22469733703155736],
            [0.33808556214745533, 0.5883087184572333, 0.230114732596577, 0.22021738445155947],
            [0.07099308600903254, 0.6311029572700989, 0.22894178381115438, 0.905420013006128],
            [0.8596354002537465, 0.07085734988865344, 0.23800463436899522, 0.6689777782962806],
            [0.2142368073704386, 0.132311848725025, 0.935514240580671, 0.5710430933252845],
            [0.47267102631179414, 0.7846194242907534, 0.8074969977666434, 0.1904099143618777],
            [0.09693081422882333, 0.4310511824063775, 0.4235786230199208, 0.467024668036675],
            [0.7290758494598506, 0.6733645472933015, 0.9841652113659661, 0.09841787115195888],
            [0.4026212821022688, 0.33930260539496315, 0.8616725363527911, 0.24865633392028563],
            [0.1902089084408115, 0.4486135478331319, 0.4218816398344042, 0.27854514466694047],
            [0.2498064478821005, 0.9232655992760128, 0.44313074505345695, 0.8613491047618306],
            [0.5503253124498481, 0.05058832952488124, 0.9992824684127266, 0.8360275850799519],
            [0.9689962572847513, 0.9263669830081276, 0.8486957344143055, 0.16631111060391401],
            [0.48564112545071847, 0.21374729919918167, 0.4010402925494526, 0.058635399972178925],
            [0.3789731189769161, 0.9853088437797259, 0.26520305817215195, 0.7840706019485694],
            [0.4550083673391433, 0.4230074859901629, 0.9573176408596732, 0.9954226894927138],
            [0.5557683234056182, 0.718408275296326, 0.15479682527406413, 0.2967078254945642],
            [0.9687093649691588, 0.5791802908162562, 0.5421952013742742, 0.7479755603790641],
            [0.05716527290748308, 0.5841775944589712, 0.5028503829195136, 0.8527198920482854],
            [0.15743272793948326, 0.9607789032744504, 0.08011146524058688, 0.1858249609807232],
            [0.5950351064500277, 0.6752125536040902, 0.2352038950009312, 0.11988661394712419],
            [0.8902873141294375, 0.24621534778862486, 0.5945191535334412, 0.6193815103321031],
            [0.4192249153358725, 0.5836722892912247, 0.5227827155319589, 0.9347062577364272],
            [0.20425919942353643, 0.7161918007894148, 0.23868595261584602, 0.3957858467912545],
            [0.6716902229599713, 0.2999970797987622, 0.31617719627185403, 0.7518644924144021],
            [0.07254311449315731, 0.4582855226185861, 0.9984544408544423, 0.9960964478550944],
            [0.073260721099633, 0.2131543122670404, 0.26520041475040135, 0.9332593779937091],
            [0.8808641736864395, 0.8792702424845428, 0.36952708873888396, 0.15774683235723197],
            [0.833744954639807, 0.703539925087371, 0.6116777657259501, 0.9872330636315043],
            [0.6539763177107326, 0.007823107152157949, 0.8171041351154616, 0.2993787521999779],
            [0.6633887149660773, 0.9389300039271039, 0.13429111439336772, 0.11542867041910221],
            [0.10703597770941764, 0.5532236408848159, 0.2723482123148163, 0.6048298270302239],
            [0.7176121871387979, 0.20359731232745293, 0.6342379588850797, 0.2639839016304094],
            [0.48853185214937656, 0.9053364910793232, 0.8461037132948555, 0.09229846771273342],
            [0.42357577256372636, 0.27668022397225167, 0.0035456890877823, 0.7711192230196271],
            [0.6371133773013796, 0.2619552624343482, 0.7412309083479308, 0.5516804211263913],
            [0.42768691898067934, 0.009669699608339966, 0.07524386007376704, 0.883106393300143],
            [0.9039285715598931, 0.5455902892055223, 0.8345950198860167, 0.582509566489794],
            [0.14809378556748265, 0.12744551928213876, 0.3082583499301337, 0.89898148874259],
            [0.7961223048880417, 0.8607025820009028, 0.8989246365264746, 0.21007653833975404],
            [0.24952973922292443, 0.10279362167178563, 0.7801162418714427, 0.8841347014510089],
            [0.4063773898321168, 0.6206615101507128, 0.15455333833220464, 0.9298810156936744],
            [0.864605696219964, 0.9762060329309629, 0.8107717199403969, 0.8814162046633244],
            [0.024786361898188725, 0.7365644717550821, 0.33218546794642867, 0.9308158860483255],
            [0.8022351389371389, 0.8640640283752794, 0.810749316574389, 0.26680570959447203],
            [0.7873745091354711, 0.10809562640295711, 0.8721667829060897, 0.8585932513377816],
            [0.22243371754566443, 0.816586605596929, 0.4603032346789421, 0.30519086733860057],
            [0.7953454991528618, 0.22759548740777036, 0.02366443470145152, 0.19312978832770866],
            [0.3282619511977065, 0.8643529420302863, 0.9668891040483611, 0.2791249927218714],
            [0.6414817386076277, 0.39967838436006087, 0.9811496871982601, 0.5362157324787219],
            [0.9392371403247157, 0.11534175185142759, 0.970400611022228, 0.17856781617246364],
            [0.9625343157615555, 0.2654663625229686, 0.1084025472147111, 0.43456375856464435],
            [0.7285450606527043, 0.31367731419499123, 0.6062088533061433, 0.5114230596694781],
            [0.38519543334472717, 0.5765880434965995, 0.25472250613858194, 0.7087852838341706],
            [0.0016912782186294661, 0.9255751654990827, 0.5384519970927919, 0.7194299991448455],
            [0.7419500778394765, 0.6706285044329995, 0.3642214717812642, 0.06997381112631018],
            [0.6642376849112723, 0.3302000360425964, 0.31391564505835967, 0.8480152795063355],
            [0.7197542630139502, 0.3003222682112642, 0.30928466220865325, 0.40839290861921684],
            [0.40240038705772463, 0.295655202525947, 0.12728779905915322, 0.4204463337729083],
            [0.940363670730183, 0.6773179452727329, 0.9028055457325826, 0.6155149159513805],
            [0.3009498745655653, 0.5479372131356982, 0.0004059396972875273, 0.2869137168689272],
            [0.4298881499898346, 0.579984781195682, 0.6547056237030716, 0.4649881902470142]
        ]

        moa = MOArchive4obj(points, reference_point=[1, 1, 1, 1])
        self.assertAlmostEqual(0.666453313693048, float(moa.hypervolume), places=8)
        moa = MOArchive4obj([[p[0] - 1, p[1] - 1, p[2] - 1, p[3] - 1] for p in points],
                            reference_point=[0, 0, 0, 0])
        self.assertAlmostEqual(0.666453313693048, float(moa.hypervolume), places=8)
        moa = MOArchive4obj(points, reference_point=[1, 2, 3, 4])
        self.assertAlmostEqual(22.4083467226742, float(moa.hypervolume), places=8)
        self.assertEqual(moa.hypervolume_plus, moa.hypervolume)


if __name__ == '__main__':
    unittest.main()
