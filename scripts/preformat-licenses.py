import textwrap

from pathlib import Path

ROOT_DIR = Path(__file__).parent.resolve() / '..'

TEMPLATES_DIR = ROOT_DIR / 'src' / 'relicense' / 'templates'


def format_license(complete_text: str) -> str:
    """Format the license text by stripping leading/trailing whitespace.

    :param complete_text: The complete license text to format.
    :return: The formatted license text.
    """

    corrected_lines = []
    for line in complete_text.splitlines():
        # Wrap the text to a maximum of 80 characters per line with correct line breaks.
        initial_indent = len(line) - len(line.lstrip())
        indent = "" if initial_indent == 0 else " " * initial_indent
        rewrapped = textwrap.wrap(
            line,
            width=80,
            initial_indent="",
            subsequent_indent=indent,
            break_long_words=False,
            break_on_hyphens=False,
            drop_whitespace=True,
            placeholder='',
        )
        if not rewrapped:
            corrected_lines.append('')
        else:
            corrected_lines.extend(rewrapped)
    return '\n'.join(corrected_lines).replace('\r\n', '\n')

ALL_FILES = list(TEMPLATES_DIR.glob("*.template"))
ALL_FILES.sort(key=lambda x: x.stem)

for license_file in ALL_FILES:
    license_name = license_file.stem
    with license_file.open('r', encoding='utf-8') as f:
        content = f.read()
        formatted_content = format_license(content)
        with license_file.open('w', encoding='utf-8') as out_f:
            out_f.write(formatted_content)
            print(f"Formatted {license_name}.template")
