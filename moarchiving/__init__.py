# -*- coding: utf-8 -*-
"""This module contains, for the time being, a single MOO archive class.

A bi-objective nondominated archive as sorted list with incremental update
in logarithmic time, providing computations of overall hypervolume,
contributing hypervolumes and uncrowded hypervolume improvements.

:Author: Nikolaus Hansen, 2018

:License: BSD 3-Clause, see LICENSE file.

"""

from .moarchiving import BiobjectiveNondominatedSortedList
from .moarchiving import __author__, __license__, __version__
