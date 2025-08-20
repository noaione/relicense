"""
MIT License

Copyright (c) 2025-present noaione

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from pathlib import Path
from typing import Annotated

from .templates import ALL_LICENSES, License

import click
import typer
from click.shell_completion import CompletionItem
from rich import print
from rich.prompt import Prompt

app = typer.Typer(name="relicense", help="Generate license files from templates.")


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


@app.command()
def main(
    license: Annotated[License, typer.Option(click_type=LicenseParameter())],
    output: Path = typer.Option(
        None,
        "--output",
        "-o",
        help="The output file to write the license text to, defaults to LICENSE in the current directory.",
    ),
):
    """
    Generate a license file from a template.

    This command generates a license file based on the specified SPDX identifier.
    If no output file is specified, it defaults to writing to LICENSE in the current directory.
    """

    print(f"Generating license for [bold magenta]{license}[/bold magenta]...")
    template: list[str] = license.extract_template()
    
    for variable in template:
        value = Prompt.ask(f"Enter value for [bold red]{variable}[/bold red] (type [italic bold]\\[empty][/italic bold] to nullify)").strip()
        if not value:
            print(f" Skipping [bold italic red]{variable}[/bold italic red] as no value was provided.")
            continue
        if value == "[empty]":
            print(f" Nullifying [bold italic red]{variable}[/bold italic red].")
            value = ""
        license.apply_variable(variable, value)

    if not output:
        output = Path.cwd() / "LICENSE"

    print(f"Writing license to {output}...")
    output.write_text(license.get_result(), encoding="utf-8")


def entrypoint():
    """Wrapper for the main function to allow for command line execution."""
    app()
