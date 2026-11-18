#!/usr/bin/env python3
"""
Marlin versions the builder offers, and the Configurations ref that goes with each.

  marlin_versions.py list          -> JSON list of versions on stdout
  marlin_versions.py resolve <id>  -> marlin_ref=, configs_ref=, label=, kind= lines on stdout

The versions are the bugfix branch plus every Marlin "latest-*" tag. Each tag is
named by the release it points to (latest-2.1.x -> 2.1.2.9), and tags that point
to the same commit are listed once. The examples for a release come from the
Configurations tag of the same version, else its release-<version> branch, else
the nearest shorter version (2.1.0.5 -> 2.1.0 -> 2.1).

<id> is a version from the list ("2.1.2.9", "bugfix-2.1.x") or a latest tag
("latest-2.1.x"). Anything else is rejected.
"""

import json, re, subprocess, sys

MARLIN = 'https://github.com/MarlinFirmware/Marlin'
CONFIGS = 'https://github.com/MarlinFirmware/Configurations'
BUGFIX = 'bugfix-2.1.x'
VERSION_RE = re.compile(r'^\d+(\.\d+)+$')

def ls_remote(url):
    """{'tags': {name: sha}, 'heads': {name: sha}}, with annotated tags peeled to their commit."""
    out = subprocess.run(['git', 'ls-remote', '--tags', '--heads', url],
                         check=True, capture_output=True, text=True).stdout
    refs = {'tags': {}, 'heads': {}}
    for line in out.splitlines():
        sha, ref = line.split('\t')
        kind, _, name = ref[len('refs/'):].partition('/')
        if kind not in refs: continue
        if name.endswith('^{}'):
            refs[kind][name[:-3]] = sha  # the peeled commit wins over the tag object
        else:
            refs[kind].setdefault(name, sha)
    return refs

def vkey(v):
    return tuple(int(p) for p in v.split('.'))

def configs_ref(version, cfg):
    parts = version.split('.')
    while len(parts) >= 2:
        v = '.'.join(parts)
        if v in cfg['tags']: return v
        if f'release-{v}' in cfg['heads']: return f'release-{v}'
        parts.pop()
    return None

def versions(marlin=None, cfg=None):
    marlin = marlin or ls_remote(MARLIN)
    cfg = cfg or ls_remote(CONFIGS)
    out = []
    if BUGFIX in marlin['heads'] and BUGFIX in cfg['heads']:
        out.append({'id': BUGFIX, 'label': BUGFIX, 'kind': 'bugfix',
                    'marlin_ref': BUGFIX, 'configs_ref': BUGFIX, 'aliases': []})
    by_sha = {}
    for tag, sha in marlin['tags'].items():
        if tag.startswith('latest-'):
            by_sha.setdefault(sha, []).append(tag)
    releases = []
    for sha, latest in by_sha.items():
        named = sorted((t for t, s in marlin['tags'].items() if s == sha and VERSION_RE.match(t)), key=vkey)
        if not named: continue  # a latest tag with no release tag on its commit
        version = named[-1]
        cref = configs_ref(version, cfg)
        if not cref: continue
        latest.sort(key=lambda t: (len(t), t))
        releases.append({'id': version, 'label': f"{version} ({', '.join(latest)})", 'kind': 'release',
                         'marlin_ref': version, 'configs_ref': cref, 'aliases': latest})
    releases.sort(key=lambda v: vkey(v['id']), reverse=True)
    return out + releases

def main(argv):
    if argv == ['list']:
        print(json.dumps(versions(), indent=1))
    elif len(argv) == 2 and argv[0] == 'resolve':
        want = argv[1].strip()
        for v in versions():
            if want == v['id'] or want in v['aliases']:
                print(f"marlin_ref={v['marlin_ref']}\nconfigs_ref={v['configs_ref']}\nlabel={v['id']}\nkind={v['kind']}")
                return
        sys.exit(f"`{want[:64]}` isn't a Marlin version this builder offers.")
    else:
        sys.exit(__doc__)

if __name__ == '__main__':
    main(sys.argv[1:])
