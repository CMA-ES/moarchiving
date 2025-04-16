# -*- coding: utf-8 -*-
"""This package implements a multi-objective non-dominated archive for 2, 3 or 4 objectives,
providing easy and fast access to multiple hypervolume indicators:

- the hypervolume of the entire archive,
- the contributing hypervolume of each element,
- the uncrowded hypervolume improvement (https://doi.org/10.1145/3321707.3321852, https://arxiv.org/abs/1904.08823) of any given point in the objective space, and
- the uncrowded hypervolume of the (unpruned) archive, here called hypervolume plus (see `BiobjectiveNondominatedSortedList.hypervolume_plus`).

Additionally, the package provides a constrained version of the archive,
which allows to store points with constraints.

The source code is available at https://github.com/CMA-ES/moarchiving

Authors: Nikolaus Hansen, Nace Sever, Mila Nedić, Tea Tušar, 2024
License: BSD 3-Clause, see LICENSE file.
"""

__author__ = "Nikolaus Hansen, Nace Sever, Mila Nedic, Tea Tusar"
__license__ = "BSD 3-clause"
__version__ = "1.0.0"


from .get_archive import get_mo_archive
from .get_archive import get_cmo_archive
from .moarchiving import BiobjectiveNondominatedSortedList
from .moarchiving import BiobjectiveNondominatedSortedList as MOArchive2obj
from .moarchiving3obj import MOArchive3obj
from .moarchiving4obj import MOArchive4obj
from .constrained_moarchive import CMOArchive
#  from . import tests  # creates a circular import?
