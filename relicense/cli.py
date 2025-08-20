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

import typer

app = typer.Typer(name="relicense")


@app.command(name="gen")
def generate(
    license: str = typer.Option(..., help="The SPDX identifier of the license to generate."),
    output: typer.FileTextWrite = typer.Option(
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
    from relicense.templates import read_template

    license_text = read_template(f"{license}.txt")
    
    if output is None:
        output = open("LICENSE", "w")
    
    output.write(license_text)
    output.close()


def main():
    app()
