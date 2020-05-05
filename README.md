
# Introduction

The [Python](https://www.python.org/) `class` `moarchiving.BiobjectiveNondominatedSortedList` implements a bi-objective non-dominated archive with `list` as parent class. It is heavily based on the [`bisect`](https://docs.python.org/3/library/bisect.html) module. It provides easy and fast access to the overall hypervolume, the contributing hypervolume of each element, and to the [uncrowded hypervolume improvement](https://arxiv.org/abs/1904.08823) of any given point in objective space.

## Installation

Either via

```
pip install git+https://github.com/CMA-ES/moarchiving.git@master
```

or simply via

```
pip install moarchiving
```

The single file [`moarchiving.py`](https://github.com/CMA-ES/moarchiving/moarchiving/moarchiving.py) (from the `moarchiving/` folder) can also be directly used by itself when copied in the current folder or in a path visible to Python (e.g. a path contained in `sys.path`).

## Details

`moarchiving` uses the [`fractions.Fraction`](https://docs.python.org/3/library/fractions.html) type to avoid rounding errors when computing hypervolume differences, but its usage can also easily switched off by assigning the respective class attribute.
The `Fraction` type may become prohibitively computationally expensive with increasing
precision.

## Releases

- 0.5.3 fixed assertion error when not using `fractions.Fraction`
- 0.5.2 first published version

## Links

- [Code on Github](https://github.com/CMA-ES/moarchiving)
- Documentation (possibly slightly outdated) in
  - [this page plus performance test examples](https://cma-es.github.io/moarchiving/)
  - [apidocs format](https://cma-es.github.io/moarchiving/moarchiving-apidocs/index.html)
  - [epydocs format](https://cma-es.github.io/moarchiving/moarchiving-epydocs/index.html)


