""" Run all doctests and unit tests in the moarchiving package. """

import doctest
import unittest

import moarchiving


def run_all_tests():
    """ Run all doctests and unit tests in the moarchiving package. """
    tmp = moarchiving.BiobjectiveNondominatedSortedList.make_expensive_asserts
    moarchiving.BiobjectiveNondominatedSortedList.make_expensive_asserts = True
    # print(moarchiving.moarchiving.BiobjectiveNondominatedSortedList.make_expensive_asserts)

    for doctest_suite in [moarchiving.moarchiving2d, moarchiving.moarchiving3d,
                          moarchiving.moarchiving4d, moarchiving.moarchiving_parent]:
        print(f'doctest.testmod({doctest_suite})')
        print(doctest.testmod(doctest_suite))

    for unit_test_suite in [moarchiving.test_moarchiving2d, moarchiving.test_moarchiving3d,
                            moarchiving.test_moarchiving4d, moarchiving.test_constrained_moarchiving,
                            moarchiving.test_sorted_list]:
        print(f'unittest.TextTestRunner().run(unittest.TestLoader().loadTestsFromModule({unit_test_suite}))')
        unittest.TextTestRunner().run(unittest.TestLoader().loadTestsFromModule(unit_test_suite))

    moarchiving.BiobjectiveNondominatedSortedList.make_expensive_asserts = tmp
    # print(moarchiving.moarchiving.BiobjectiveNondominatedSortedList.make_expensive_asserts)


if __name__ == '__main__':
    run_all_tests()
