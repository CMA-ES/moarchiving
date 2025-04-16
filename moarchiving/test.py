"""Run all doctests and unit tests of the moarchiving package::

    python -m moarchiving.test

"""

import doctest
import unittest

import moarchiving as moa
import moarchiving.tests

def run_doctests():
    for doctest_suite in [moa.moarchiving,
                        moa.moarchiving3obj,
                        moa.moarchiving4obj,
                        moa.moarchiving_parent,
                        moa.constrained_moarchive]:
        print(f'doctest.testmod({doctest_suite})')
        print(doctest.testmod(doctest_suite))

def run_unittests():
    for unit_test_suite in [moa.tests.test_moarchiving2obj,
                            moa.tests.test_moarchiving3obj,
                            moa.tests.test_moarchiving4obj,
                            moa.tests.test_constrained_moarchiving,
                            moa.tests.test_sorted_list]:
        print(f'unittest.TextTestRunner().run(unittest.TestLoader().loadTestsFromModule({unit_test_suite}))')
        unittest.TextTestRunner().run(unittest.TestLoader().loadTestsFromModule(unit_test_suite))

if __name__ == "__main__":
    tmp = moa.BiobjectiveNondominatedSortedList.make_expensive_asserts
    moa.BiobjectiveNondominatedSortedList.make_expensive_asserts = True
    # print(moa.moarching.BiobjectiveNondominatedSortedList.make_expensive_asserts)

    run_doctests()
    run_unittests()

    moa.BiobjectiveNondominatedSortedList.make_expensive_asserts = tmp
    # print(moa.moarching.BiobjectiveNondominatedSortedList.make_expensive_asserts)
