"""
DO WHAT THE FUCK YOU WANT TO PUBLIC LICENSE
Version 2, December 2004

Copyright (C) 2025 noaione

Everyone is permitted to copy and distribute verbatim or modified copies of this
license document, and changing it is allowed as long as the name is changed.

DO WHAT THE FUCK YOU WANT TO PUBLIC LICENSE
TERMS AND CONDITIONS FOR COPYING, DISTRIBUTION AND MODIFICATION

    0. You just DO WHAT THE FUCK YOU WANT TO.
"""

from .templates._metadata import SPDX_COMMIT

__all__ = (
    "get_version",
)

def get_version():
    """Get the package version + SPDX commit version

    :rtype: str
    """
    # Formatted like this: 0.1.0+spdx.shortCommit
    return f"0.1.0+spdx.{SPDX_COMMIT}"
