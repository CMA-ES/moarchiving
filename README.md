
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
The [`moarchiving.py`](https://github.com/CMA-ES/moarchiving/moarchiving.py) file (from the `moarchiving/` folder) can also be used by itself when copied in the current folder or in a path visible for Python (e.g. a path contained in `sys.path`).


## Links

- [Code on Github](https://github.com/CMA-ES/moarchiving)
- Documentation (possibly slighly outdated) in
  - [apidocs format](https://cma-es.github.io/morachiving/moarchiving-apidocs/index.html)
  - [epydocs format](https://cma-es.github.io/morachiving/moarchiving-epydocs/index.html)


## Testing and timing of `moarchiving.BiobjectiveNondominatedSortedList`


```python
import doctest
import moarchiving
NA = moarchiving.BiobjectiveNondominatedSortedList
doctest.testmod(moarchiving.moarchiving)
# NA.make_expensive_asserts = True
```




    TestResults(failed=0, attempted=66)




```python
import numpy as np
def nondom_arch(n):
    return np.abs(np.linspace(-1, 1, 2 * n).reshape(2, n).T).tolist()
# nondom_arch(3)
```


```python
import fractions
id_ = lambda x: x
rg = np.arange(0.1, 1000)
```

### Timing of `Fraction`


```python
%timeit [id_(i) for i in rg]  # expect 120mics
```

    100 µs ± 456 ns per loop (mean ± std. dev. of 7 runs, 10000 loops each)



```python
%timeit [float(i) for i in rg]  # expect 170mics
```

    130 µs ± 4.55 µs per loop (mean ± std. dev. of 7 runs, 10000 loops each)



```python
%timeit [fractions.Fraction(i) for i in rg]  # expect 2.7ms
```

    1.59 ms ± 123 µs per loop (mean ± std. dev. of 7 runs, 1000 loops each)


### Various


```python
a = moarchiving.BiobjectiveNondominatedSortedList(
    [[-0.749, -1.188], [-0.557, 1.1076],
     [0.2454, 0.4724], [-1.146, -0.110]], [10, 10])
a._asserts()
a
```




    [[-1.146, -0.11], [-0.749, -1.188]]




```python
>>> for i in range(len(a)):
...    assert a.contributing_hypervolume(i) == a.contributing_hypervolumes[i]
>>> assert all(map(lambda x, y: x - 1e-9 < y < x + 1e-9,
...               a.contributing_hypervolumes,
...               [4.01367, 11.587422]))
```


```python
a.dominators([1, 3]) == a
```




    True




```python
a.add([-1, -3])  # return index where the element was added
```




    1




```python
a
```




    [[-1.146, -0.11], [-1, -3]]




```python
a.add([-1.5, 44])
```


```python
a
```




    [[-1.146, -0.11], [-1, -3]]




```python
a.dominates(a[0])
```




    True




```python
a.dominates([-1.2, 1])
```




    False




```python
a._asserts()
```


```python
NA.merge = NA.add_list  # merge disappeared
b = NA(a)
b.merge([[-1.2, 1]])
# print(b)
a.add_list([[-1.2, 1]])
# print(a)
assert b == a
a.merge(b)
assert b == a
```


```python
r = np.random.randn(100_000, 2).tolist()
r2 = sorted(np.random.randn(200, 2).tolist())
assert NA(r).add_list(r2) == NA(r).merge(r2)
```


```python
%%timeit a = NA(r)  # expect 390mics
a.add_list(r2)
```

    331 µs ± 5.94 µs per loop (mean ± std. dev. of 7 runs, 1000 loops each)



```python
%%timeit a = NA(r)  # expect 290mics
a.merge(r2)
```

    338 µs ± 4.27 µs per loop (mean ± std. dev. of 7 runs, 1000 loops each)


## Timing of initialization


```python
%timeit nondom_arch(1_000)
%timeit nondom_arch(10_000)
%timeit nondom_arch(100_000)  # just checking baseline, expect 16ms
```

    96.6 µs ± 1.06 µs per loop (mean ± std. dev. of 7 runs, 10000 loops each)
    761 µs ± 12.2 µs per loop (mean ± std. dev. of 7 runs, 1000 loops each)
    10.4 ms ± 1.2 ms per loop (mean ± std. dev. of 7 runs, 100 loops each)



```python
%timeit NA(nondom_arch(1_000))
%timeit NA(nondom_arch(10_000))  # expect 10ms
%timeit NA(nondom_arch(100_000))  # expect 112ms, nondom_arch itself takes about 25%
```

    964 µs ± 8.49 µs per loop (mean ± std. dev. of 7 runs, 1000 loops each)
    9.34 ms ± 186 µs per loop (mean ± std. dev. of 7 runs, 100 loops each)
    95.3 ms ± 873 µs per loop (mean ± std. dev. of 7 runs, 10 loops each)



```python
randars = {}  # prepare input lists
for n in [1_000, 10_000, 100_000]:
    randars[n] = np.random.rand(n, 2).tolist()
len(NA(nondom_arch(100_000))), len(NA(randars[100_000]))
```




    (100000, 13)




```python
%timeit NA(randars[1_000])
%timeit NA(randars[10_000])  # expect 9ms
%timeit NA(randars[100_000])  # expect 180 ms
```

    535 µs ± 2.8 µs per loop (mean ± std. dev. of 7 runs, 1000 loops each)
    7.16 ms ± 68.6 µs per loop (mean ± std. dev. of 7 runs, 100 loops each)
    129 ms ± 5.62 ms per loop (mean ± std. dev. of 7 runs, 10 loops each)



```python
%timeit sorted(nondom_arch(1_000))
%timeit sorted(nondom_arch(10_000))  # expect 1.2ms
%timeit sorted(nondom_arch(100_000)) # expect 21ms
```

    126 µs ± 977 ns per loop (mean ± std. dev. of 7 runs, 10000 loops each)
    1.08 ms ± 17.3 µs per loop (mean ± std. dev. of 7 runs, 1000 loops each)
    14.8 ms ± 298 µs per loop (mean ± std. dev. of 7 runs, 100 loops each)



```python
%timeit sorted(randars[1_000])
%timeit sorted(randars[10_000])   # expect 5ms
%timeit sorted(randars[100_000])  # expect 110ms
```

    288 µs ± 10.4 µs per loop (mean ± std. dev. of 7 runs, 1000 loops each)
    4.43 ms ± 86.6 µs per loop (mean ± std. dev. of 7 runs, 100 loops each)
    76.2 ms ± 5.69 ms per loop (mean ± std. dev. of 7 runs, 10 loops each)



```python
%timeit list(randars[1_000])
%timeit list(randars[10_000])
%timeit list(randars[100_000])  # expect 1ms
```

    2.13 µs ± 37.6 ns per loop (mean ± std. dev. of 7 runs, 100000 loops each)
    33 µs ± 685 ns per loop (mean ± std. dev. of 7 runs, 10000 loops each)
    407 µs ± 12.3 µs per loop (mean ± std. dev. of 7 runs, 1000 loops each)


### Summary with 1e5 data (outdated)
```
   1 ms `list` 
  22 ms `sorted` on sorted list
 130 ms `sorted` on unsorted list
 110 ms archive on sorted nondominated list
 190 ms archive on list which needs pruning (was 1300ms)
```

## Timing of `add`


```python
%%timeit a = NA(nondom_arch(1_000))  # expect 7.3ms
for i in range(1000):
    a.add([ai - 1e-4 for ai in a[np.random.randint(len(a))]])
len(a)
```

    24.6 ms ± 982 µs per loop (mean ± std. dev. of 7 runs, 10 loops each)



```python
%%timeit a = NA(nondom_arch(10_000))  # expect 7.7ms
for i in range(1000):
    a.add([ai - 1e-4 for ai in a[np.random.randint(len(a))]])
len(a)
```

    25.1 ms ± 744 µs per loop (mean ± std. dev. of 7 runs, 10 loops each)



```python
%%timeit a = NA(nondom_arch(100_000))  # expect 15ms
for i in range(1000):
    a.add([ai - 1e-4 for ai in a[np.random.randint(len(a))]])
len(a)  # deletion kicks in and makes it 20 times slower if implemented with pop
```

    35 ms ± 1.29 ms per loop (mean ± std. dev. of 7 runs, 10 loops each)



```python
%%timeit a = NA(nondom_arch(100_000))  # expect 10ms
for i in range(1000):
    a.add([ai - 1e-8 for ai in a[np.random.randint(len(a))]])
len(a) # no deletion has taken place
```

    25.2 ms ± 472 µs per loop (mean ± std. dev. of 7 runs, 10 loops each)



```python
%%timeit a = NA(nondom_arch(1_000_000))  # expect 270ms
for i in range(1000):
    a.add([ai - 1e-4 for ai in a[np.random.randint(len(a))]])
len(a)  # deletion kicks in
```

    97.4 ms ± 3.52 ms per loop (mean ± std. dev. of 7 runs, 10 loops each)



```python
%%timeit a = NA(nondom_arch(1_000_000))  # expect 12ms
for i in range(1000):
    a.add([ai - 1e-8 for ai in a[np.random.randint(len(a))]])
len(a)
```

    27.9 ms ± 1.36 ms per loop (mean ± std. dev. of 7 runs, 10 loops each)


## Timing of Hypervolume computation


```python
%timeit a = NA(nondom_arch(1_000), [5, 5])  # expect 28ms, takes 4 or 40x longer than without hypervolume computation
```

    19.7 ms ± 281 µs per loop (mean ± std. dev. of 7 runs, 10 loops each)



```python
%timeit a = NA(nondom_arch(10_000), [5, 5])  # expect 300ms
```

    196 ms ± 2.04 ms per loop (mean ± std. dev. of 7 runs, 1 loop each)



```python
%timeit a = NA(nondom_arch(100_000), [5, 5])  # expect 3s, takes 3x longer than without hypervolume computation
```

    2.11 s ± 130 ms per loop (mean ± std. dev. of 7 runs, 1 loop each)



```python
%%timeit a = NA(nondom_arch(1_000), [5, 5])  # expect 220ns
a.hypervolume
```

    137 ns ± 1.13 ns per loop (mean ± std. dev. of 7 runs, 10000000 loops each)



```python
%%timeit a = NA(nondom_arch(10_000), [5, 5])  # expect 210ns
a.hypervolume
```

    140 ns ± 1.07 ns per loop (mean ± std. dev. of 7 runs, 10000000 loops each)



```python
%%timeit a = NA(nondom_arch(100_000), [5, 5])  # expect 225ns 
a.hypervolume
```

    142 ns ± 5.18 ns per loop (mean ± std. dev. of 7 runs, 10000000 loops each)



```python
NA.hypervolume_computation_float_type = float
```


```python
%timeit a = NA(nondom_arch(1_000), [5, 5])  # expect 11ms, takes 4 or 40x longer than without hypervolume computation
```

    7.73 ms ± 176 µs per loop (mean ± std. dev. of 7 runs, 100 loops each)



```python
NA.hypervolume_final_float_type = float
NA.hypervolume_computation_float_type = float
```


```python
%timeit a = NA(nondom_arch(1_000), [5, 5])  # expect 3.8ms, takes 4 or 40x longer than without hypervolume computation
```

    2.9 ms ± 70.9 µs per loop (mean ± std. dev. of 7 runs, 100 loops each)

