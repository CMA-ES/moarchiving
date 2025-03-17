""" Run all doctests and unit tests in the moarchiving package. """

import doctest
import unittest

import moarchiving as moa


tmp = moa.BiobjectiveNondominatedSortedList.make_expensive_asserts
moa.BiobjectiveNondominatedSortedList.make_expensive_asserts = True
# print(moa.moarching.BiobjectiveNondominatedSortedList.make_expensive_asserts)

for doctest_suite in [moa.moarchiving,
                      moa.moarchiving3obj,
                      moa.moarchiving4obj,
                      moa.moarchiving_parent,
                      moa.constrained_moarchive]:
    print(f'doctest.testmod({doctest_suite})')
    print(doctest.testmod(doctest_suite))

for unit_test_suite in [moa.tests.test_moarchiving2obj,
                        moa.tests.test_moarchiving3obj,
                        moa.tests.test_moarchiving4obj,
                        moa.tests.test_constrained_moarchiving,
                        moa.tests.test_sorted_list]:
    print(f'unittest.TextTestRunner().run(unittest.TestLoader().loadTestsFromModule({unit_test_suite}))')
    unittest.TextTestRunner().run(unittest.TestLoader().loadTestsFromModule(unit_test_suite))

moa.BiobjectiveNondominatedSortedList.make_expensive_asserts = tmp
# print(moa.moarching.BiobjectiveNondominatedSortedList.make_expensive_asserts)
