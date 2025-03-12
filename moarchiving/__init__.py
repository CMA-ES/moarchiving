# -*- coding: utf-8 -*-
"""This package implements a non-dominated archive for 2, 3, or 4 objectives,

providing easy and fast access to multiple hypervolume indicators, namely
the hypervolume of the archive, the contributing hypervolume of each
element, the uncrowded hypervolume improvement of any given point in the
objective space, and the uncrowded hypervolume of the (unpruned) archive.

Additionally, the package provides a constrained version of the archive,
which allows to store points with constraints.


:Authors: Nikolaus Hansen, Nace Sever, Mila Nedić, Tea Tušar, 2024

:License: BSD 3-Clause, see LICENSE file.

"""

__author__ = "Nikolaus Hansen, Nace Sever, Mila Nedic, Tea Tusar"
__license__ = "BSD 3-clause"
__version__ = "1.0.0"


from .get_archive import get_mo_archive, get_cmo_archive
from .moarchiving import BiobjectiveNondominatedSortedList
from .moarchiving3obj import MOArchive3obj
from .moarchiving4obj import MOArchive4obj
from .moarchiving_parent import MOArchiveParent
from .constrained_moarchive import CMOArchive
from moarchiving.tests import (test_moarchiving2obj, test_moarchiving3obj, test_moarchiving4obj,
                               test_constrained_moarchiving, test_sorted_list)
