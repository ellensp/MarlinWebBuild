#!/usr/bin/env python3
"""
Helpers for mapping MarlinFirmware/Configurations examples to PlatformIO envs.

  marlin_index.py index <marlin_root> <configs_root>        -> JSON index on stdout
  marlin_index.py envs  <marlin_root> <configs_root> <path>  -> envs, one per line

<path> is relative to <configs_root>/config/examples, e.g. "Creality/Ender-3/CrealityV422".
Env discovery follows Marlin's buildroot/bin/mfenvs (pins.h "env:" comments).
"""

import json, re, sys
from pathlib import Path

MB_RE = re.compile(r'^\s*#define\s+MOTHERBOARD\s+BOARD_(\w+)', re.M)
ENV_RE = re.compile(r'(?:env|lin):(\S+)')

def board_of(config_dir: Path):
    m = MB_RE.search((config_dir / 'Configuration.h').read_text(errors='replace'))
    return m.group(1) if m else None

def envs_for(marlin_root: Path, board: str, pins_lines=None):
    if pins_lines is None:
        pins_lines = (marlin_root / 'Marlin/src/pins/pins.h').read_text(errors='replace').splitlines()
    mb = re.compile(r'MB\(.*\b' + re.escape(board) + r'\b.*\)')
    envs = []
    for i, line in enumerate(pins_lines):
        if not mb.search(line): continue
        for cand in pins_lines[i:i + 2]:
            if '#include' in cand and '//' in cand:
                for e in ENV_RE.findall(cand.split('//', 1)[1]):
                    if not e.endswith('_xfer') and e not in envs:
                        envs.append(e)
    return envs

def example_dirs(configs_root: Path):
    base = configs_root / 'config/examples'
    for cfg in sorted(base.rglob('Configuration.h')):
        yield cfg.parent.relative_to(base).as_posix(), cfg.parent

def build_index(marlin_root: Path, configs_root: Path):
    pins_lines = (marlin_root / 'Marlin/src/pins/pins.h').read_text(errors='replace').splitlines()
    out = []
    for rel, d in example_dirs(configs_root):
        board = board_of(d)
        envs = envs_for(marlin_root, board, pins_lines) if board else []
        out.append({'path': rel, 'board': board, 'envs': envs})
    return out

def main(argv):
    if len(argv) >= 3 and argv[0] == 'index':
        print(json.dumps(build_index(Path(argv[1]), Path(argv[2])), separators=(',', ':')))
    elif len(argv) == 4 and argv[0] == 'envs':
        base = (Path(argv[2]) / 'config/examples').resolve()
        d = (base / argv[3]).resolve()
        # Reject anything that escapes config/examples or isn't a real example folder
        if base not in d.parents or not (d / 'Configuration.h').is_file():
            sys.exit(f"Not an example config: {argv[3]}")
        board = board_of(d)
        if not board: sys.exit("No MOTHERBOARD found in Configuration.h")
        print('\n'.join(envs_for(Path(argv[1]), board)))
    else:
        sys.exit(__doc__)

if __name__ == '__main__':
    main(sys.argv[1:])
