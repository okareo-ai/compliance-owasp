#!/usr/bin/env python3
"""Update all OWASP notebooks to use owasp.common."""

import json
import re
from pathlib import Path

OWASP = Path(__file__).resolve().parent
NOTEBOOKS = list(OWASP.glob("LLM*/notebooks/run-evaluation.ipynb"))

INIT_CELL_NEW = '''import sys
import json
from pathlib import Path

# Add project root for owasp.common import
_nb = globals().get("__vsc_ipynb_file__", ".")
NOTEBOOK_DIR = Path(_nb).resolve().parent
CATEGORY_DIR = NOTEBOOK_DIR.parent
if str(CATEGORY_DIR.parent.parent) not in sys.path:
    sys.path.insert(0, str(CATEGORY_DIR.parent.parent))

from okareo.checks import ModelBasedCheck, CheckOutputType
from okareo.model_under_test import Driver

from owasp.common import (
    init_okareo,
    parse_artifact,
    CodeCheckFromSource,
    build_target,
    SINGLE_TURN_DRIVER_TEMPLATE,
)

okareo, OKAREO_API_KEY = init_okareo()
print(f"✓ Okareo SDK initialized (key: ...{OKAREO_API_KEY[-5:]})")
print(f"Category directory: {CATEGORY_DIR}")'''

# Target config + build replacement
TARGET_BUILD_OLD = re.compile(
    r'TARGET_ENV_PATH = CATEGORY_DIR\.parent / "target\.env".*?'
    r'print\(f"✓ Target built: \{TARGET_NAME\}"\)',
    re.DOTALL,
)

TARGET_BUILD_REPLACE = '''# Target loaded from owasp/target.env. To use a different config (e.g. prod):
#   target = build_target(CATEGORY_DIR, env_path="target.prod.env")
target = build_target(CATEGORY_DIR)
TARGET_NAME = target.name
print(f"✓ Target built: {TARGET_NAME}")'''


def update_cell_source(src: str, is_init: bool = False) -> str:
    """Update a cell's source to use common."""
    out = src

    # Replace init cell
    if is_init and "from okareo import Okareo" in src and "NOTEBOOK_DIR = Path" in src:
        return INIT_CELL_NEW

    # Replace target config + build
    if "TARGET_ENV_PATH = CATEGORY_DIR.parent" in out:
        out = TARGET_BUILD_OLD.sub(TARGET_BUILD_REPLACE, out)

    # Remove build target cell (headers, TurnConfig, etc.)
    if "next_turn_config = TurnConfig(" in out and "target = Target(target=endpoint_target_model" in out:
        out = re.sub(
            r'headers = \{"Accept": "application/json".*?'
            r'print\(f"✓ Target built: \{TARGET_NAME\}"\)',
            "# Target built in config cell above via build_target(CATEGORY_DIR)",
            out,
            flags=re.DOTALL,
        )

    # Remove SINGLE_TURN_DRIVER_TEMPLATE / PASS_THROUGH_TEMPLATE definition
    out = re.sub(
        r'\nSINGLE_TURN_DRIVER_TEMPLATE = """You are testing another Agent.*?'
        r'\{scenario_input\}"""\s*\n',
        "\n",
        out,
        flags=re.DOTALL,
    )
    out = re.sub(
        r'\nPASS_THROUGH_TEMPLATE = """You are testing another Agent.*?'
        r'\{scenario_input\}"""\s*\n',
        "\n",
        out,
        flags=re.DOTALL,
    )

    return out


def main():
    for nb_path in NOTEBOOKS:
        print(f"Updating {nb_path.relative_to(OWASP.parent)}")
        with open(nb_path) as f:
            nb = json.load(f)

        for i, cell in enumerate(nb["cells"]):
            if cell["cell_type"] != "code":
                continue
            src = "".join(cell["source"]) if isinstance(cell["source"], list) else cell["source"]
            is_init = "from okareo import Okareo" in src and "NOTEBOOK_DIR = Path" in src
            new_src = update_cell_source(src, is_init=is_init)
            if new_src != src:
                lines = new_src.split("\n")
                cell["source"] = [line + "\n" for line in lines[:-1]]
                if lines[-1]:
                    cell["source"].append(lines[-1] + "\n")
                elif cell["source"]:
                    cell["source"][-1] = cell["source"][-1].rstrip("\n")

        with open(nb_path, "w") as f:
            json.dump(nb, f, indent=1)

    print("Done.")


if __name__ == "__main__":
    main()
