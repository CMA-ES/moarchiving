""" Run all doctests and unit tests in the moarchiving package. """

import doctest
import unittest

import moarchiving


tmp = moarchiving.BiobjectiveNondominatedSortedList.make_expensive_asserts
moarchiving.BiobjectiveNondominatedSortedList.make_expensive_asserts = True
# print(moarchiving.moarchiving.BiobjectiveNondominatedSortedList.make_expensive_asserts)

for doctest_suite in [moarchiving.moarchiving, moarchiving.moarchiving3obj,
                      moarchiving.moarchiving4obj, moarchiving.moarchiving_parent]:
    print(f'doctest.testmod({doctest_suite})')
    print(doctest.testmod(doctest_suite))

for unit_test_suite in [moarchiving.test_moarchiving2obj, moarchiving.test_moarchiving3obj,
                        moarchiving.test_moarchiving4obj, moarchiving.test_constrained_moarchiving,
                        moarchiving.test_sorted_list]:
    print(f'unittest.TextTestRunner().run(unittest.TestLoader().loadTestsFromModule({unit_test_suite}))')
    unittest.TextTestRunner().run(unittest.TestLoader().loadTestsFromModule(unit_test_suite))

moarchiving.BiobjectiveNondominatedSortedList.make_expensive_asserts = tmp
# print(moarchiving.moarchiving.BiobjectiveNondominatedSortedList.make_expensive_asserts)
