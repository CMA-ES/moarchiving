
# Introduction

The [Python](https://www.python.org/) `class` `moarchiving.BiobjectiveNondominatedSortedList` implements a bi-objective non-dominated archive with `list` as parent class. It is heavily based on the [`bisect`](https://docs.python.org/2/library/bisect.html) module. It provides easy and fast access to the overall hypervolume, the contributing hypervolume of each element, and to the [uncrowded hypervolume improvement](https://arxiv.org/abs/1904.08823) of any given point in objective space.

Documentation (possibly slighly outdated) is available [here](https://cma-es.github.io/morachiving/moarchiving-apidocs/index.html) or [here](https://cma-es.github.io/morachiving/moarchiving-epydocs/index.html).

Installation via

```
pip install git+https://github.com/CMA-ES/moarchiving.git@master
```

or (soon) simply via

```
pip install moarchiving
```

## Testing and timing of `moarchiving.BiobjectiveNondominatedSortedList`


```python
import doctest
import moarchiving
# reload(moarchiving)
NA = moarchiving.BiobjectiveNondominatedSortedList
doctest.testmod(moarchiving)
# NA.make_expensive_asserts = True
```




    TestResults(failed=0, attempted=49)




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

    10000 loops, best of 3: 123 µs per loop



```python
%timeit [float(i) for i in rg]  # expect 170mics
```

    10000 loops, best of 3: 175 µs per loop



```python
%timeit [fractions.Fraction(i) for i in rg]  # expect 2.7ms
```

    100 loops, best of 3: 2.9 ms per loop


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
b = NA(a)
print(b.merge([[-1.2, 1]]))
print(a.add_list([[-1.2, 1]]))
assert b == a
print(a.merge(b))
```

    1
    1
    0



```python
r = np.random.randn(100_000, 2).tolist()
r2 = sorted(np.random.randn(200, 2).tolist())
assert NA(r).add_list(r2) == NA(r).merge(r2)
```


```python
%%timeit a = NA(r)  # expect 390mics
a.add_list(r2)
```

    1000 loops, best of 3: 388 µs per loop



```python
%%timeit a = NA(r)  # expect 290mics
a.merge(r2)
```

    1000 loops, best of 3: 290 µs per loop


## Timing of initialization


```python
%timeit nondom_arch(1_000)
%timeit nondom_arch(10_000)
%timeit nondom_arch(100_000)  # just checking baseline, expect 16ms
```

    The slowest run took 5.09 times longer than the fastest. This could mean that an intermediate result is being cached.
    10000 loops, best of 3: 122 µs per loop
    1000 loops, best of 3: 1.02 ms per loop
    10 loops, best of 3: 18.5 ms per loop



```python
%timeit NA(nondom_arch(1_000))
%timeit NA(nondom_arch(10_000))  # expect 10ms
%timeit NA(nondom_arch(100_000))  # expect 112ms, nondom_arch itself takes about 25%
```

    1000 loops, best of 3: 1.47 ms per loop
    10 loops, best of 3: 15.6 ms per loop
    1 loop, best of 3: 223 ms per loop



```python
randars = {}  # prepare input lists
for n in [1_000, 10_000, 100_000]:
    randars[n] = np.random.rand(n, 2).tolist()
len(NA(nondom_arch(100_000))), len(NA(randars[100_000]))
```




    (100000, 16)




```python
%timeit NA(randars[1_000])
%timeit NA(randars[10_000])  # expect 9ms
%timeit NA(randars[100_000])  # expect 180 ms
```

    1000 loops, best of 3: 767 µs per loop
    100 loops, best of 3: 10.6 ms per loop
    10 loops, best of 3: 206 ms per loop



```python
%timeit sorted(nondom_arch(1_000))
%timeit sorted(nondom_arch(10_000))  # expect 1.2ms
%timeit sorted(nondom_arch(100_000)) # expect 21ms
```

    10000 loops, best of 3: 139 µs per loop
    1000 loops, best of 3: 1.33 ms per loop
    10 loops, best of 3: 21.4 ms per loop



```python
%timeit sorted(randars[1_000])
%timeit sorted(randars[10_000])   # expect 5ms
%timeit sorted(randars[100_000])  # expect 110ms
```

    1000 loops, best of 3: 319 µs per loop
    100 loops, best of 3: 5.8 ms per loop
    10 loops, best of 3: 132 ms per loop



```python
%timeit list(randars[1_000])
%timeit list(randars[10_000])
%timeit list(randars[100_000])  # expect 1ms
```

    The slowest run took 4.29 times longer than the fastest. This could mean that an intermediate result is being cached.
    100000 loops, best of 3: 2.58 µs per loop
    10000 loops, best of 3: 33.8 µs per loop
    The slowest run took 4.59 times longer than the fastest. This could mean that an intermediate result is being cached.
    100 loops, best of 3: 841 µs per loop


### Summary with 1e5 data
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

    100 loops, best of 3: 9.98 ms per loop



```python
%%timeit a = NA(nondom_arch(10_000))  # expect 7.7ms
for i in range(1000):
    a.add([ai - 1e-4 for ai in a[np.random.randint(len(a))]])
len(a)
```

    100 loops, best of 3: 10.4 ms per loop



```python
%%timeit a = NA(nondom_arch(100_000))  # expect 15ms
for i in range(1000):
    a.add([ai - 1e-4 for ai in a[np.random.randint(len(a))]])
len(a)  # deletion kicks in and makes it 20 times slower if implemented with pop
```

    100 loops, best of 3: 12.2 ms per loop



```python
%%timeit a = NA(nondom_arch(100_000))  # expect 10ms
for i in range(1000):
    a.add([ai - 1e-8 for ai in a[np.random.randint(len(a))]])
len(a) # no deletion has taken place
```

    100 loops, best of 3: 15.1 ms per loop



```python
%%timeit a = NA(nondom_arch(1_000_000))  # expect 270ms
for i in range(1000):
    a.add([ai - 1e-4 for ai in a[np.random.randint(len(a))]])
len(a)  # deletion kicks in
```

    1 loop, best of 3: 326 ms per loop



```python
%%timeit a = NA(nondom_arch(1_000_000))  # expect 12ms
for i in range(1000):
    a.add([ai - 1e-8 for ai in a[np.random.randint(len(a))]])
len(a)
```

    10 loops, best of 3: 45.6 ms per loop


## Timing of Hypervolume computation


```python
%timeit a = NA(nondom_arch(1_000), [5, 5])  # expect 28ms, takes 4 or 40x longer than without hypervolume computation
```

    10 loops, best of 3: 32.9 ms per loop



```python
%timeit a = NA(nondom_arch(10_000), [5, 5])  # expect 300ms
```

    1 loop, best of 3: 321 ms per loop



```python
%timeit a = NA(nondom_arch(100_000), [5, 5])  # expect 3s, takes 3x longer than without hypervolume computation
```

    1 loop, best of 3: 3.13 s per loop



```python
%%timeit a = NA(nondom_arch(1_000), [5, 5])  # expect 220ns
a.hypervolume
```

    The slowest run took 19.04 times longer than the fastest. This could mean that an intermediate result is being cached.
    1000000 loops, best of 3: 222 ns per loop



```python
%%timeit a = NA(nondom_arch(10_000), [5, 5])  # expect 210ns
a.hypervolume
```

    The slowest run took 87.97 times longer than the fastest. This could mean that an intermediate result is being cached.
    1000000 loops, best of 3: 217 ns per loop



```python
%%timeit a = NA(nondom_arch(100_000), [5, 5])  # expect 225ns 
a.hypervolume
```

    The slowest run took 12.86 times longer than the fastest. This could mean that an intermediate result is being cached.
    1000000 loops, best of 3: 225 ns per loop



```python
NA.hypervolume_computation_float_type = float
```


```python
%timeit a = NA(nondom_arch(1_000), [5, 5])  # expect 11ms, takes 4 or 40x longer than without hypervolume computation
```

    100 loops, best of 3: 11.2 ms per loop



```python
NA.hypervolume_final_float_type = float
NA.hypervolume_computation_float_type = float
```


```python
%timeit a = NA(nondom_arch(1_000), [5, 5])  # expect 3.8ms, takes 4 or 40x longer than without hypervolume computation
```

    100 loops, best of 3: 4.8 ms per loop

