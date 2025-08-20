"""
relicense.templates
~~~~~~~~~~~~~~~~~~~
The code that handles reading license templates from the package.

:copyright: (c) 2025-present noaione
:license: MIT, see LICENSE for more details.
"""

from pathlib import Path
from importlib import resources
import re

import click
from click.shell_completion import CompletionItem

__all__ = (
    "ALL_LICENSES",
    "License",
    "LicenseParameter",
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


class License:
    def __init__(self, spdx: str) -> None:
        self.spdx = spdx
        self._template: str | None = None

    def __repr__(self) -> str:
        return f"License(spdx={self.spdx})"

    def __str__(self) -> str:
        return self.spdx

    def read(self) -> str:
        """Read the license template file."""
        if self._template is None:
            self._template = read_template(self.spdx)
        return self._template
    
    def apply_variable(self, variable: str, value: str) -> None:
        """Apply a variable to the license template."""
        if self._template is None:
            self._template = self.read()
        self._template = self._template.replace(f"%%{variable}%%", value)

    def get_result(self) -> str:
        """Get the license template with applied variables."""
        if self._template is None:
            self._template = self.read()
        templates =  self._template
        new_templates = []
        for line in templates.splitlines():
            line = line.rstrip() # we don't want trailing spaces
            new_templates.append(line)
        templates = "\n".join(new_templates)
        return templates.rstrip()

    def extract_template(self) -> list[str]:
        """Extract the template data from the license template.
        
        Template are formatted like this: %%variable%%, where variable is the
        name of the variable to be replaced.
        """

        template = self.read()
        matched = re.findall(r"%%(.*?)%%", template)
        if not matched:
            return []
        variables: set[str] = set()
        for match in matched:
            match = match.strip()
            if match and match not in variables:
                variables.add(match)
        variables_list = sorted(list(variables))
        return variables_list


class LicenseParameter(click.ParamType):
    name = "license"

    def convert(self, value, param: click.Parameter | None, ctx: click.Context | None) -> License:
        """Convert the input value to a License object."""
        if isinstance(value, str):
            if value not in ALL_LICENSES:
                self.fail(f"Invalid license: {value}. Available licenses: {', '.join(ALL_LICENSES)}", param, ctx)
            return License(value)
        elif isinstance(value, License):
            return value
        else:
            self.fail(f"Expected a string or License object, got {type(value).__name__}", param, ctx)

    def get_metavar(self, param: click.Parameter | None, ctx: click.Context) -> str:
        """Return the metavar for the license parameter."""
        return " | ".join(ALL_LICENSES)

    def shell_complete(self, ctx: click.Context, param: click.Parameter, incomplete: str) -> list[CompletionItem]:
        """Provide shell completion for the license parameter."""
        return [CompletionItem(license_name) for license_name in ALL_LICENSES if license_name.startswith(incomplete)]
