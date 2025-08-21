"""
relicense
~~~~~~~~~
Automatically generate license files from templates.

:copyright: (c) 2025-present noaione
:license: WTFPL, see LICENSE for more details.
"""

from relicense._metadata import get_version
from relicense.templates import ALL_LICENSES, SPDX_COMMIT, License

__version__ = get_version()

__all__ = (
    "ALL_LICENSES",
    "SPDX_COMMIT",
    "License",
    "__version__"
)
