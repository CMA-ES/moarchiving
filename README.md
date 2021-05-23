
# Introduction

The [Python](https://www.python.org/) `class` `moarchiving.BiobjectiveNondominatedSortedList` implements a bi-objective non-dominated archive with `list` as parent class. It is heavily based on the [`bisect`](https://docs.python.org/3/library/bisect.html) module. It provides easy and fast access to the overall hypervolume, the contributing hypervolume of each element, and to the [uncrowded hypervolume improvement](https://arxiv.org/abs/1904.08823/) of any given point in objective space.

## Installation

Either simply via

```
pip install moarchiving
```

or from [GitHub](https://github.com/CMA-ES/moarchiving/) via

```
pip install git+https://github.com/CMA-ES/moarchiving.git@master
```

The single file [`moarchiving.py`](https://github.com/CMA-ES/moarchiving/moarchiving/moarchiving.py) (from the `moarchiving/` folder) can also be directly used by itself when copied in the current folder or in a path visible to Python (e.g. a path contained in `sys.path`).

## Testing

```
python -m moarchiving.test
```

on a system shell should output something like

```
doctest.testmod(moarchiving.moarchiving)
TestResults(failed=0, attempted=77)
```
 ## Usage

 ```python
from moarchiving import BiobjectiveNondominatedSortedList as NDA

nda = NDA()  # a new empty non-dominated archive
# add a pair to the list if non-dominated and removed dominated entries
nda.add([2, 1], info={'f': [2, 1], 'x': "don't know"})
nda == [[2, 1], ]  # is True
nda.add([1, 1])  # dominates previous entry
nda.discarded == [[2, 1]]  # just now removed element(s)
nda == [[1, 1]]  # is True
```

## Details

`moarchiving` uses the [`fractions.Fraction`](https://docs.python.org/3/library/fractions.html) type to avoid rounding errors when computing hypervolume differences, but its usage can also easily be switched off by assigning the class attribute `hypervolume_computation_float_type` and `hypervolume_final_float_type` to `float`.
The `Fraction` type can become prohibitively computationally expensive with increasing
precision.

## Releases

- 0.6.0 the `infos` attribute is a `list` with corresponding (arbitrary) information, e.g. for keeping the respective solutions.
- 0.5.3 fixed assertion error when not using `fractions.Fraction`
- 0.5.2 first published version

## Links

- [Code on Github](https://github.com/CMA-ES/moarchiving/)
- Documentation (possibly slightly outdated) in
  - [performance test examples from a notebook](https://cma-es.github.io/moarchiving/)
  - [apidocs format](https://cma-es.github.io/moarchiving/moarchiving-apidocs/index.html)
  - [epydocs format](https://cma-es.github.io/moarchiving/moarchiving-epydocs/index.html)


