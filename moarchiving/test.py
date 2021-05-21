import doctest
import moarchiving

tmp = moarchiving.BiobjectiveNondominatedSortedList.make_expensive_asserts
moarchiving.BiobjectiveNondominatedSortedList.make_expensive_asserts = True
# print(moarchiving.moarchiving.BiobjectiveNondominatedSortedList.make_expensive_asserts)

print('doctest.testmod(moarchiving.moarchiving)')
print(doctest.testmod(moarchiving.moarchiving))

moarchiving.BiobjectiveNondominatedSortedList.make_expensive_asserts = tmp
# print(moarchiving.moarchiving.BiobjectiveNondominatedSortedList.make_expensive_asserts)
