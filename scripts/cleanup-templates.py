#!/usr/bin/env python3
"""
Generate a file `non_osi_or_non_fsf.txt` listing templates that are not OSI-approved or not FSF-free.
Format per user request:
[Index]. [SPDX-Identifier] - [Actual license name] - [Reasoning]

Exclusions: Creative Commons (CC*), CDLA/CDL*, Business Source (BUSL*), and SSPL are excluded as allowed by user.
"""
import os
import json
import sys
import urllib.request

ROOT = os.path.dirname(os.path.abspath(__file__))
TEMPLATES = os.path.join(ROOT, '..', 'relicense', 'templates')
OUTFILE = os.path.join(os.path.dirname(ROOT), 'to-be-reviewed.txt')

SPDX_JSON_URL = 'https://raw.githubusercontent.com/spdx/license-list-data/master/json/licenses.json'

# Allowed prefixes or markers to skip (per user's allowances)
ALLOWED_PREFIXES = ('BUSL-', 'SSPL-', 'CDL', 'CDLA', 'GLWTPL', 'WTFNMFPL')
# Markers used to identify public-domain or PD-like licenses to allow
ALLOWED_PD_MARKERS = ('-PD', 'PDDL', 'CC0')
# Also allow Creative Commons (filenames starting with 'CC' or 'CC-')


def fetch_spdx():
    with urllib.request.urlopen(SPDX_JSON_URL, timeout=30) as resp:
        data = resp.read().decode('utf-8')
    return json.loads(data)


def normalize(s):
    return s.strip()


def main():
    if not os.path.isdir(TEMPLATES):
        print('Templates dir not found:', TEMPLATES, file=sys.stderr)
        sys.exit(1)

    spdx = fetch_spdx()
    licenses = {entry['licenseId']: entry for entry in spdx.get('licenses', [])}

    # Also prepare a lowercase mapping for fuzzy matching by id and by name
    lc_id_map = {k.lower(): v for k, v in licenses.items()}
    # name map not used currently, keep commented for potential future fuzzy matching
    # lc_name_map = {v.get('name','').lower(): v for v in licenses.values()}

    entries = []
    to_be_deleted = []
    files = sorted(os.listdir(TEMPLATES))
    for fname in files:
        if not fname.lower().endswith('.txt'):
            continue
        key = fname[:-4]
        if key == '__init__':
            continue

        # skip allowed categories: Creative Commons, BUSL/SSPL/CDL/CDLA prefixes,
        # and public-domain markers (e.g. NCBI-PD, NIST-PD, PDDL, CC0)
        if key.upper().startswith('CC') or any(key.startswith(p) for p in ALLOWED_PREFIXES) or any(m in key.upper() for m in ALLOWED_PD_MARKERS):
            continue

        matched = None
        reason = None
        # direct SPDX id match
        if key in licenses:
            matched = licenses[key]
        else:
            # try case-insensitive exact id
            if key.lower() in lc_id_map:
                matched = lc_id_map[key.lower()]
            else:
                # try matching by name contains key
                for lic in licenses.values():
                    name = lic.get('name','').lower()
                    if key.lower() == name.replace(' ','').replace('-',''):
                        matched = lic
                        break
                    if "-exception" in key.lower():
                        matched = lic
                        break
                if not matched:
                    for lic in licenses.values():
                        name = lic.get('name','').lower()
                        if key.lower() in name or name in key.lower():
                            matched = lic
                            break
                        if "-exception" in key.lower():
                            matched = lic
                            break

        if matched:
            is_osi = matched.get('isOsiApproved', False)
            is_fsf = matched.get('isFsfLibre', False)
            reasons = []
            if not is_osi and not is_fsf:
                reasons.append('not OSI-approved or FSF-free')
            if '-exception' in key.lower():
                reasons.append('exception license')
            if reasons:
                # entries.append(key)
                to_be_deleted.append(key)
                # entries.append((key, matched.get('name',''), '; '.join(reasons)))
        else:
            # no SPDX mapping found — flag for manual review
            entries.append((key, 'UNKNOWN (no SPDX mapping found)', 'manual review — likely nonstandard, EULA, or custom/derivative text'))

    # write out file
    with open(OUTFILE, 'w', encoding='utf-8') as out:
        if not entries:
            out.write('No non-OSI or non-FSF templates found (after exclusions).\n')
        else:
            for i, (spdx_id, name, reason) in enumerate(entries, start=1):
                out.write(f"{i}. {spdx_id} - {name} - {reason}\n")
    for key in to_be_deleted:
        try:
            os.remove(os.path.join(TEMPLATES, f"{key}.txt"))
        except OSError as e:
            print(f"Error removing {key}.txt: {e}", file=sys.stderr)

    print('Wrote', OUTFILE)

if __name__ == '__main__':
    main()
