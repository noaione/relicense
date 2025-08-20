"""
relicense.templates
~~~~~~~~~~~~~~~~~~~
The code that handles reading license templates from the package.

:copyright: (c) 2025-present noaione
:license: MIT, see LICENSE for more details.
"""

from pathlib import Path
from importlib import resources

__all__ = (
    "ALL_LICENSES",
    "read_template",
)

CURRENT_DIR = Path(__file__).parent.resolve()

REMAPPED_LICENSES: dict[str, Path] = {}
for license_file in CURRENT_DIR.glob("*.template"):
    license_name = license_file.stem
    REMAPPED_LICENSES[license_name] = license_file

ALL_LICENSES = list(REMAPPED_LICENSES.keys())


def read_template(name: str) -> str:
    """Read a template file from the list of remapped licenses.

    :param name: The name of the license template to read, e.g. '0bsd.txt'.
    :return: The contents of the license template file.
    """

    if name not in REMAPPED_LICENSES:
        raise ValueError(f"License template '{name}' not found.")

    with resources.open_text("relicense.templates", REMAPPED_LICENSES[name].name) as f:
        return f.read()
