# -*- coding: utf-8 -*-
""" This package implements a multi-objective (2, 3 and 4 objectives are supported)
non-dominated archive.

It provides easy and fast access to the hypervolume and hypervolume plus indicators,
the contributing hypervolume of each element, and to the uncrowded hypervolume improvement
of any given point in objective space.
Additionally, it provides a constrained version of the archive, which allows to store points
with constraints and to compute the ICMOP indicator.


:Authors: Nikolaus Hansen, Nace Sever, Mila Nedić, Tea Tušar, 2024

:License: BSD 3-Clause, see LICENSE file.

"""

from .moarchiving2d import BiobjectiveNondominatedSortedList
from .moarchiving3d import MOArchive3d
from .moarchiving4d import MOArchive4d
from .moarchiving_parent import MOArchiveParent
from .constrained_moarchive import CMOArchive
from moarchiving.tests import (test_moarchiving2d, test_moarchiving3d, test_moarchiving4d,
                               test_constrained_moarchiving, test_sorted_list)
from .moarchiving2d import __author__, __license__, __version__
