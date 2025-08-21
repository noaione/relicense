"""
An auto update script for the `relicense` package.
"""

from datetime import datetime
import json
import os
import re
import sys
import textwrap
import urllib.request

from pathlib import Path
import uuid

ROOT_DIR = (Path(__file__).parent.resolve() / "..").resolve()
TEMPLATES_DIR = ROOT_DIR / "src" / "relicense" / "templates"

SPDX_JSON_URL = "https://raw.githubusercontent.com/spdx/license-list-data/master/json/licenses.json"

# Allowed prefixes or markers to skip (per user's allowances)
ALLOWED_PREFIXES = ("BUSL-", "SSPL-", "CDL", "CDLA", "GLWTPL", "WTFNMFPL")
# Markers used to identify public-domain or PD-like licenses to allow
ALLOWED_PD_MARKERS = ("-PD", "PDDL", "CC0")
EXCEPTION_STUFF_PREFIX = ("ANTLR-")


def fetch_spdx():
    with urllib.request.urlopen(SPDX_JSON_URL, timeout=30) as resp:
        data = resp.read().decode("utf-8")
    return json.loads(data)


def fetch_spdx_license_and_format(license_json: str) -> str:
    with urllib.request.urlopen(license_json, timeout=30) as resp:
        complete_text_json_raw: str = resp.read().decode("utf-8")
        complete_text_json = json.loads(complete_text_json_raw)
        complete_text = complete_text_json["licenseText"]
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
    return "\n".join(corrected_lines).replace("\r\n", "\n")


def is_cc_license_and_localized(license_id: str) -> bool:
    """Check if the license is a Creative Commons license and localized."""
    correct_variants = [
        "CC-BY",
        "CC-BY-SA",
        "CC-BY-NC",
        "CC-BY-NC-SA",
        "CC-BY-ND",
        "CC-BY-NC-ND",
        "CC-SA",
    ]
    
    if license_id.startswith("CC0"):
        return True

    if not license_id.startswith("CC-"):
        return False

    for variant in correct_variants:
        if license_id.startswith(variant):
            # strip data
            stripped_id = license_id[len(variant):].strip().lstrip("-")
            if stripped_id and "-" not in stripped_id:
                return True
    return False


def get_current_version() -> str:
    version_file = TEMPLATES_DIR / "_metadata.py"
    if not version_file.is_file():
        raise FileNotFoundError(f"Version file not found: {version_file}")
    with version_file.open("r", encoding="utf-8") as f:
        matcher = re.search(r"SPDX_COMMIT = [\"']([^'\"]+)?[\"']", f.read())
    if not matcher:
        raise ValueError("Current version not found in the version file.")
    return matcher.group(1)


def update_version_file(new_version: str) -> None:
    """Update the version file with the new version."""
    version_file = TEMPLATES_DIR / "_metadata.py"
    if not version_file.is_file():
        raise FileNotFoundError(f"Version file not found: {version_file}")

    with version_file.open("r", encoding="utf-8") as f:
        content = f.read()

    new_content = re.sub(r"SPDX_COMMIT = [\"']([^'\"]+)?[\"']", f"SPDX_COMMIT = \"{new_version}\"", content)

    with version_file.open("w", encoding="utf-8") as f:
        f.write(new_content)


def filter_allowed_licenses(entries: list[dict]) -> list[dict]:
    """Filter out licenses based on allowed prefixes and markers."""
    filtered = []
    for entry in entries:
        license_id: str = entry["licenseId"]
        is_osi: bool = entry.get("isOsiApproved", False)
        is_fsf: bool = entry.get("isFsfLibre", False)
        if "-exception" in license_id.lower():
            continue
        if is_osi or is_fsf:
            filtered.append(entry)
            continue
        if license_id.upper().startswith("ANTLR-"):
            continue
        if any(marker in license_id.upper() for marker in ALLOWED_PD_MARKERS):
            filtered.append(entry)
            continue
        if any(license_id.upper().startswith(prefix) for prefix in ALLOWED_PREFIXES):
            filtered.append(entry)
            continue
        if is_cc_license_and_localized(license_id.upper()):
            filtered.append(entry)
            continue
    return filtered


BASE_BODY = """## Auto-generated License Update Report

This report is automatically generated via GitHub Actions to keep
the license templates up to date with the SPDX license list.

Please review the changes to add proper template variables
for new licenses, and to remove or deprecate licenses that
are no longer needed.

### Newly Added Licenses
{added}

### Removed Licenses
{removed}

### Deprecated Licenses
{removed_deprecated}

{note}

Timestamp: {timestamp}
"""


def create_formatted_github_output(added: list[str], removed: list[str], removed_deprecated: list[str]) -> str:
    """Create a formatted string for GitHub Actions output."""

    timestamp = datetime.now().isoformat()
    added_str = "\n".join(f"- `{lic}`" for lic in added) if added else "**None**"
    removed_str = "\n".join(f"- `{lic}`" for lic in removed) if removed else "**None**"
    removed_deprecated_str = "\n".join(f"- `{lic}`" for lic in removed_deprecated) if removed_deprecated else "**None**"
    
    note = '---'
    if not added and not removed and not removed_deprecated:
        note = "*No changes detected but the license version was updated.*\n\n---"

    return BASE_BODY.format(
        added=added_str,
        removed=removed_str,
        removed_deprecated=removed_deprecated_str,
        timestamp=timestamp,
        note=note
    )


def main():
    if not TEMPLATES_DIR.is_dir():
        print(f"Templates directory not found: {TEMPLATES_DIR}", file=sys.stderr)
        sys.exit(1)

    current_version = get_current_version()
    print(f"Current license version: {current_version}")
    spdx = fetch_spdx()
    license_version = spdx["licenseListVersion"]
    print(f"SPDX license list version: {license_version}")

    if current_version == license_version:
        print("No update needed, the license version is up to date.")
        return

    allowed_licenses = filter_allowed_licenses(spdx.get("licenses", []))
    # don't include deprecated licenses in the allowed list
    allowed_licenses_ids = [lic["licenseId"] for lic in allowed_licenses if not lic.get("isDeprecatedLicenseId", False)]
    spdx_deprecated_licenses = [lic["licenseId"] for lic in allowed_licenses if lic.get("isDeprecatedLicenseId", False)]

    # get all existing template files
    existing_files = [f.stem for f in TEMPLATES_DIR.glob("*.template") if f.is_file()]

    # get missing licenses
    missing_licenses = [lic for lic in allowed_licenses if lic["licenseId"] not in existing_files and not lic.get("isDeprecatedLicenseId", False)]
    removed_licenses = sorted([lic for lic in existing_files if lic not in allowed_licenses_ids])

    # If we found any new licenses, we will create a new template file for each
    output_added_files = []
    if len(missing_licenses) > 0:
        print(f"Found {len(missing_licenses)} new licenses to add:")
        for lic in missing_licenses:
            print(f"-> Adding new license: {lic['licenseId']}")
            license_url = lic["detailsUrl"]
            license_data = fetch_spdx_license_and_format(license_url)
            # write to file
            license_file = TEMPLATES_DIR / f"{lic['licenseId']}.template"
            license_file.write_text(license_data, encoding="utf-8")
            print(f"--> Added license {lic['licenseId']} to {license_file}")
            output_added_files.append(lic["licenseId"])
    output_removed_files = []
    output_removed_deprecated_files = []
    if len(removed_licenses) > 0:
        print(f"Found {len(removed_licenses)} removed licenses:")
        for lic in removed_licenses:
            print(f"-> Removing license: {lic}")
            license_file = TEMPLATES_DIR / f"{lic}.template"
            if license_file.is_file():
                license_file.unlink()
                print(f"--> Removed license file {license_file}")
                if lic in spdx_deprecated_licenses:
                    output_removed_deprecated_files.append(lic)
                else:
                    output_removed_files.append(lic)
            else:
                print(f"--> License file {license_file} does not exist, skipping.")

    # Update the version file with the new version
    update_version_file(license_version)
    # Write for github actions
    if os.environ.get("GITHUB_OUTPUT"):
        with open(os.environ["GITHUB_OUTPUT"], "a") as fp:
            delimiter = uuid.uuid4().hex.replace("-", "")
            print(f"update_report<<{delimiter}", file=fp)
            print(create_formatted_github_output(output_added_files, output_removed_files, output_removed_deprecated_files), file=fp)
            print(delimiter, file=fp)
    else:
        print("GITHUB_OUTPUT environment variable not set, skipping GitHub Actions output.")
        print(create_formatted_github_output(output_added_files, output_removed_files, output_removed_deprecated_files))

if __name__ == "__main__":
    main()
