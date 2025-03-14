""" This module provides functions to generate non-dominated points for testing purposes """

import math
import random


def get_non_dominated_points(n_points, n_dim=3, mode='spherical'):
    """ Returns a list of non-dominated points:
     - n_points: number of points
     - n_dim: number of dimensions
     - mode: 'spherical' or 'linear' """
    if n_dim == 2:
        if mode == 'spherical':
            return spherical_front_2d(1, n_points, normalized=False)
        elif mode == 'linear':
            return linear_front_2d(1, n_points, normalized=False)
    if n_dim == 3:
        if mode == 'spherical':
            return spherical_front_3d(1, n_points, normalized=False)
        elif mode == 'linear':
            return linear_front_3d(1, n_points, normalized=False)
    elif n_dim == 4:
        if mode == 'spherical':
            return spherical_front_4d(1, n_points, normalized=False)
        elif mode == 'linear':
            return linear_front_4d(1, n_points, normalized=False)
    else:
        raise ValueError("Invalid number of dimensions")


def get_random_points(n_points, n_dim):
    """ Returns a list of random points between 0 and 1, with n_points and n_dim dimensions """
    return [[random.random() for _ in range(n_dim)] for _ in range(n_points)]


def get_stacked_points(n_points, points_definitions):
    """ Returns a list of points with n_points and n_dim dimensions,
    where point from i-th dimension is defined by points_definitions[i]:

        - 'random' for random value between 0 and 1
        - int for a fixed value """
    points = []
    for i in range(n_points):
        points.append([])
        for p_def in points_definitions:
            if p_def == 'random':
                points[-1].append(random.random())
            elif isinstance(p_def, int):
                points[-1].append(p_def)
            else:
                raise ValueError("Invalid point definition")

    return points


def permute_points(points, permutation):
    """ takes a list of points (n x dim) and a permutation (dim)
    and returns the points with the permutation applied """
    return [[point[permutation[i]] for i in range(len(permutation))] for point in points]


def spherical_front_2d(distance, num_points, normalized):
    """ Returns a list of non-dominated points on the 2D spherical front """
    vectors = []

    if normalized:
        v1 = [0, distance]
        v2 = [distance, 0]
        vectors = [v1, v2]

    while len(vectors) < num_points:
        phi = random.random() * math.pi / 2
        vectors.append([distance * math.cos(phi), distance * math.sin(phi)])

    return vectors


def linear_front_2d(distance, num_points, normalized=True):
    """ Returns a list of non-dominated points on the 2D linear front """
    vectors = []

    if normalized:
        v1 = [1, 1 - distance]
        v2 = [1 - distance, 1]
        vectors = [v1, v2]

    while len(vectors) < num_points:
        x = random.random()
        vectors.append([x, 1 - x])

    return vectors


def spherical_front_3d(distance, num_points, normalized=True):
    """ Returns a list of non-dominated points on the 3D spherical front """
    vectors = []

    if normalized:
        v1 = [0, 0, distance]
        v2 = [0, distance, 0]
        v3 = [distance, 0, 0]
        vectors = [v1, v2, v3]

    while len(vectors) < num_points:
        x, y, z = 1, 1, 1

        while (math.sqrt(x * x + y * y + z * z) > 1) or (x < 0.5 and y < 0.5 and z < 0.5):
            x = next_gaussian_double()
            y = next_gaussian_double()
            z = next_gaussian_double()

        r1 = math.sqrt(x * x + y * y + z * z)
        alpha = math.acos(z / r1)
        beta = math.atan2(y, x)

        vect = [distance * math.sin(alpha) * math.cos(beta),
                distance * math.sin(alpha) * math.sin(beta),
                distance * math.cos(alpha)]
        vectors.append(vect)

    return vectors


def linear_front_3d(distance, num_points, normalized):
    """ Returns a list of non-dominated points on the 3D linear front """
    vectors = []

    if normalized:
        v1 = [1, 1, 1 - distance]
        v2 = [1, 1 - distance, 1]
        v3 = [1 - distance, 1, 1]
        vectors = [v1, v2, v3]

    while len(vectors) < num_points:
        array = [0.0]
        for _ in range(2):
            array.append(distance * random.random())
        array.append(distance)
        array.sort()

        x = 1 - (array[1] - array[0])
        y = 1 - (array[2] - array[1])
        z = 1 - (array[3] - array[2])
        vectors.append([x, y, z])

    return vectors


def linear_front_4d(distance, num_points, normalized):
    """ Returns a list of non-dominated points on the 4D linear front """
    vectors = []

    if normalized:
        v1 = [0, 0, 0, distance]
        v2 = [0, 0, distance, 0]
        v3 = [0, distance, 0, 0]
        v4 = [distance, 0, 0, 0]
        vectors = [v1, v2, v3, v4]

    while len(vectors) < num_points:
        array = [0.0] + [distance * random.random() for _ in range(3)] + [distance]
        array.sort()

        x = array[1] - array[0]
        y = array[2] - array[1]
        z = array[3] - array[2]
        w = array[4] - array[3]

        v = [x, y, z, w]
        vectors.append(v)

    return vectors


def spherical_front_4d(distance, num_points, normalized):
    """ Returns a list of non-dominated points on the 4D spherical front """
    vectors = []

    if normalized:
        v1 = [0, 0, 0, distance]
        v2 = [0, 0, distance, 0]
        v3 = [0, distance, 0, 0]
        v4 = [distance, 0, 0, 0]
        vectors = [v1, v2, v3, v4]

    while len(vectors) < num_points:
        x, y, z, w = 1, 1, 1, 1

        while (math.sqrt(x * x + y * y + z * z + w * w) > 1) or (x < 0.5 and y < 0.5 and z < 0.5 and w < 0.5):
            x = next_gaussian_double()
            y = next_gaussian_double()
            z = next_gaussian_double()
            w = next_gaussian_double()

        alpha = math.atan(math.sqrt(y * y + z * z + w * w) / x)
        beta = math.atan(math.sqrt(z * z + w * w) / y)
        gamma = 2 * math.atan(z / (math.sqrt(z * z + w * w) + w))

        v = [
            distance * math.cos(alpha),
            distance * math.sin(alpha) * math.cos(beta),
            distance * math.sin(alpha) * math.sin(beta) * math.cos(gamma),
            distance * math.sin(alpha) * math.sin(beta) * math.sin(gamma)
        ]
        vectors.append(v)
    return vectors


def next_gaussian_double():
    factor = 2.0
    while True:
        result = random.gauss(0, 1)
        if result < -factor:
            continue
        if result > factor:
            continue
        if result >= 0:
            result = result / (2 * factor)
        else:
            result = (2 * factor + result) / (2 * factor)
        return result
