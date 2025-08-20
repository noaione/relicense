"""
relicense
~~~~~~~~~
Automatically generate license files from templates.

:copyright: (c) 2025-present noaione
:license: WTFPL, see LICENSE for more details.
"""

from relicense._metadata import get_version
from relicense.templates import SPDX_COMMIT, ALL_LICENSES, License

__version__ = get_version()

__all__ = (
    "License",
    "ALL_LICENSES",
    "SPDX_COMMIT",
    "__version__"
)
