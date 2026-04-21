#!/usr/bin/env python3
"""
Run an OWASP LLM compliance suite from the CLI.

Usage:
    python run_suite.py --dir LLM01-prompt-injection
    python run_suite.py --dir LLM06-excessive-agency --max-turns 8
    python run_suite.py --dir LLM01-prompt-injection --upload-only
    python run_suite.py --dir LLM01-prompt-injection --eval-only
    python run_suite.py --dir ASI08-cascading-failures --sim pipeline-cascade-failure

Requires:
    - OKAREO_API_KEY set in environment or .env
    - owasp/target.json configured with target agent details
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

# Ensure project root is importable
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from okareo.checks import CheckOutputType, ModelBasedCheck
from okareo.model_under_test import Driver
from okareo_api_client.api.default import create_filter_v0_filters_post
from okareo_api_client.api.default import get_filters_v0_filters_get
from okareo_api_client.api.default import update_filter_v0_filters_filter_group_id_put
from okareo_api_client.models.comparison_operator import ComparisonOperator
from okareo_api_client.models.datapoint_field import DatapointField
from okareo_api_client.models.datapoint_filter_create import DatapointFilterCreate
from okareo_api_client.models.datapoint_filter_update import DatapointFilterUpdate
from okareo_api_client.models.filter_condition import FilterCondition

from owasp.common import (
    SINGLE_TURN_DRIVER_TEMPLATE,
    CodeCheckFromSource,
    build_target,
    init_okareo,
    parse_artifact,
    UNSET,
)


# ---------------------------------------------------------------------------
# Artifact metadata parsing
# ---------------------------------------------------------------------------


def _parse_scenario_meta(meta_path: Path) -> dict:
    """Extract frontmatter from a scenario _meta.md file.

    Supports a ``checks`` field as a comma-separated list of check names,
    e.g. ``checks: "check-a, check-b"``.  Parsed into a Python list.
    """
    content = meta_path.read_text(encoding="utf-8")
    meta: dict[str, object] = {}
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            for line in parts[1].strip().splitlines():
                if ":" in line:
                    key, val = line.split(":", 1)
                    key = key.strip()
                    val = val.strip().strip('"')
                    if key == "checks":
                        meta[key] = [v.strip() for v in val.split(",") if v.strip()]
                    else:
                        meta[key] = val
    return meta


def _check_eval_mode(check_path: Path) -> str:
    """Return evaluation_mode from a check artifact file."""
    data = parse_artifact(check_path)
    # Re-parse frontmatter for evaluation_mode (parse_artifact doesn't expose it)
    content = check_path.read_text(encoding="utf-8")
    if check_path.suffix == ".py":
        import re

        match = re.search(
            r"^# ---\s*\n(.*?)\n# ---", content, re.DOTALL | re.MULTILINE
        )
        block = match.group(1) if match else ""
    else:
        parts = content.split("---", 2)
        block = parts[1] if len(parts) >= 3 else ""
    for line in block.strip().splitlines():
        line = line.lstrip("# ").strip()
        if line.startswith("evaluation_mode:"):
            return line.split(":", 1)[1].strip().strip('"')
    return "single-turn"


# ---------------------------------------------------------------------------
# Part 1: Upload artifacts
# ---------------------------------------------------------------------------


def upload_artifacts(okareo, category_dir: Path, category_prefix: str):
    """Upload scenarios, checks, and drivers. Returns registered dicts."""
    scenarios_dir = category_dir / "scenarios"
    checks_dir = category_dir / "checks"
    drivers_dir = category_dir / "drivers"

    # --- Scenarios ---
    registered_scenarios = {}
    scenario_modes = {}  # scenario_name -> evaluation_mode
    scenario_checks = {}  # scenario_name -> list[str] | None (explicit check names)

    for jsonl_path in sorted(scenarios_dir.glob("*.jsonl")):
        scenario_name = f"{category_prefix}-{jsonl_path.stem}"
        print(f"  Uploading scenario: {scenario_name}")
        scenario = okareo.upload_scenario_set(
            scenario_name=scenario_name,
            file_path=str(jsonl_path),
        )
        registered_scenarios[scenario_name] = scenario
        print(f"    ✓ {scenario_name} (ID: {scenario.scenario_id})")

        # Read evaluation mode and checks from metadata
        meta_path = scenarios_dir / f"{jsonl_path.stem}_meta.md"
        if meta_path.exists():
            meta = _parse_scenario_meta(meta_path)
            scenario_modes[scenario_name] = meta.get(
                "evaluation_mode", "single-turn"
            )
            scenario_checks[scenario_name] = meta.get("checks")  # list or None
        else:
            scenario_modes[scenario_name] = "single-turn"

    print(f"  Total scenarios: {len(registered_scenarios)}")

    # --- Checks ---
    registered_checks = {}  # name -> check_id
    check_modes = {}  # name -> evaluation_mode

    for check_path in sorted(
        list(checks_dir.glob("*.md")) + list(checks_dir.glob("*.py"))
    ):
        check_data = parse_artifact(check_path)
        name = check_data["name"]
        print(f"  Registering check: {name}")

        if check_data.get("code_contents") is not UNSET and check_data.get(
            "code_contents"
        ):
            check_obj = CodeCheckFromSource(check_data["code_contents"])
        else:
            check_obj = ModelBasedCheck(
                prompt_template=check_data["prompt_template"],
                check_type=CheckOutputType.PASS_FAIL,
            )

        result = okareo.create_or_update_check(
            name=name,
            description=check_data.get("description", ""),
            check=check_obj,
        )
        registered_checks[name] = result.id
        check_modes[name] = _check_eval_mode(check_path)
        print(f"    ✓ {name} (ID: {result.id})")

    print(f"  Total checks: {len(registered_checks)}")

    # --- Drivers ---
    registered_drivers = {}  # name -> driver result object

    if drivers_dir.exists():
        for md_path in sorted(drivers_dir.glob("*.md")):
            driver_data = parse_artifact(md_path, default_temperature=0.6)
            name = driver_data["name"]
            print(f"  Registering driver: {name}")

            driver_obj = Driver(
                name=name,
                prompt_template=driver_data["prompt_template"],
                temperature=driver_data["temperature"],
            )
            result = okareo.create_or_update_driver(driver=driver_obj)
            registered_drivers[name] = result
            print(f"    ✓ {name} (ID: {result.id})")

    print(f"  Total drivers: {len(registered_drivers)}")

    return (
        registered_scenarios,
        scenario_modes,
        scenario_checks,
        registered_checks,
        check_modes,
        registered_drivers,
    )


# ---------------------------------------------------------------------------
# Part 2: Build evaluation plan & run simulations
# ---------------------------------------------------------------------------


def _load_eval_config(category_dir: Path) -> dict | None:
    """Load optional eval_config.json for simulation plan and options."""
    config_path = category_dir / "eval_config.json"
    if config_path.exists():
        return json.loads(config_path.read_text(encoding="utf-8"))
    return None


def _config_bool(value: object) -> bool:
    """Parse permissive bool-like config values."""
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "on"}
    return bool(value)


def _resolve_evaluation_plan(
    category_dir: Path,
    scenario_modes: dict[str, str],
    scenario_checks: dict[str, list[str] | None],
    check_modes: dict[str, str],
    registered_drivers: dict,
    sim_filter: str | None = None,
) -> tuple[list[dict], str]:
    """Resolve the simulation plan from eval_config.json or auto-detection."""
    eval_config = _load_eval_config(category_dir)
    if eval_config:
        plan = eval_config.get("simulations", [])
        source = "eval_config.json"
    else:
        plan = _build_auto_plan(
            scenario_modes,
            scenario_checks,
            check_modes,
            registered_drivers,
        )
        source = "auto-detected plan"

    if sim_filter:
        plan = [s for s in plan if sim_filter.lower() in s["scenario"].lower()]

    return plan, source


def _resolve_monitor_config_from_plan(
    plan: list[dict],
    registered_checks: dict[str, str],
) -> tuple[bool, list[str]]:
    """Return monitor requirement + monitor checks from selected simulations.

    Supported per simulation entry in ``eval_config.json``:
      - ``requires_monitor`` (bool-like)
      - ``monitor_checks`` (optional list[str]; falls back to ``checks``)
    """
    monitor_sims = [
        sim for sim in plan if _config_bool(sim.get("requires_monitor", False))
    ]
    if not monitor_sims:
        return False, []

    monitor_checks: list[str] = []
    seen: set[str] = set()

    for sim in monitor_sims:
        raw_checks = sim.get("monitor_checks")
        if raw_checks is None:
            raw_checks = sim.get("checks", [])
        if isinstance(raw_checks, str):
            raw_checks = [raw_checks]

        for check_name in raw_checks or []:
            if check_name not in registered_checks:
                print(
                    f"  ⚠ Monitor check '{check_name}' not found among uploaded checks; ignoring."
                )
                continue
            if check_name not in seen:
                seen.add(check_name)
                monitor_checks.append(check_name)

    if not monitor_checks:
        print(
            "  ⚠ Monitor required but no valid monitor checks configured. "
            "Monitor will be created without check restrictions."
        )

    return True, monitor_checks


def _build_auto_plan(
    scenario_modes: dict[str, str],
    scenario_checks: dict[str, list[str] | None],
    check_modes: dict[str, str],
    registered_drivers: dict,
) -> list[dict]:
    """
    Auto-derive an evaluation plan from artifact metadata.

    Returns a list of simulation dicts:
        {scenario, checks, driver, max_turns, first_turn}
    """
    single_turn_checks = [n for n, m in check_modes.items() if m == "single-turn"]
    multi_turn_checks = [n for n, m in check_modes.items() if m == "multi-turn"]

    single_scenarios = [n for n, m in scenario_modes.items() if m == "single-turn"]
    multi_scenarios = [n for n, m in scenario_modes.items() if m == "multi-turn"]

    driver_names = sorted(registered_drivers.keys())

    plan = []

    # Single-turn simulations
    for scenario_name in sorted(single_scenarios):
        explicit = scenario_checks.get(scenario_name)
        if explicit:
            checks = explicit
        elif single_turn_checks:
            checks = single_turn_checks
        else:
            checks = list(check_modes.keys())
        plan.append(
            {
                "scenario": scenario_name,
                "checks": checks,
                "driver": None,  # pass-through
                "max_turns": 1,
                "first_turn": "driver",
            }
        )

    def _resolve_checks(scenario_name: str, fallback: list[str]) -> list[str]:
        explicit = scenario_checks.get(scenario_name)
        return explicit if explicit else fallback

    # Multi-turn simulations
    if multi_scenarios and driver_names:
        if len(multi_scenarios) == len(driver_names):
            # 1:1 pairing by sorted order
            for scenario_name, driver_name in zip(
                sorted(multi_scenarios), driver_names
            ):
                checks = _resolve_checks(
                    scenario_name,
                    multi_turn_checks if multi_turn_checks else list(check_modes.keys()),
                )
                plan.append(
                    {
                        "scenario": scenario_name,
                        "checks": checks,
                        "driver": driver_name,
                        "max_turns": 10,
                        "first_turn": "target",
                    }
                )
        elif len(driver_names) == 1:
            # Single driver for all multi-turn scenarios
            for scenario_name in sorted(multi_scenarios):
                checks = _resolve_checks(
                    scenario_name,
                    multi_turn_checks if multi_turn_checks else list(check_modes.keys()),
                )
                plan.append(
                    {
                        "scenario": scenario_name,
                        "checks": checks,
                        "driver": driver_names[0],
                        "max_turns": 10,
                        "first_turn": "target",
                    }
                )
        else:
            print(
                f"  ⚠ Cannot auto-pair {len(multi_scenarios)} multi-turn scenarios "
                f"with {len(driver_names)} drivers. Create eval_config.json for explicit mapping."
            )
            for scenario_name in sorted(multi_scenarios):
                checks = _resolve_checks(
                    scenario_name,
                    multi_turn_checks if multi_turn_checks else list(check_modes.keys()),
                )
                plan.append(
                    {
                        "scenario": scenario_name,
                        "checks": checks,
                        "driver": driver_names[0],
                        "max_turns": 10,
                        "first_turn": "target",
                    }
                )
    elif multi_scenarios:
        print(
            f"  ⚠ {len(multi_scenarios)} multi-turn scenarios but no drivers found — skipping"
        )

    return plan


def run_evaluation(
    okareo,
    api_key: str,
    target,
    category_prefix: str,
    registered_scenarios: dict,
    scenario_modes: dict,
    scenario_checks: dict,
    registered_checks: dict,
    check_modes: dict,
    registered_drivers: dict,
    category_dir: Path,
    max_turns_override: int | None = None,
    sim_filter: str | None = None,
    plan: list[dict] | None = None,
    plan_source: str | None = None,
):
    """Run all simulations in the evaluation plan."""
    if plan is None:
        plan, source = _resolve_evaluation_plan(
            category_dir=category_dir,
            scenario_modes=scenario_modes,
            scenario_checks=scenario_checks,
            check_modes=check_modes,
            registered_drivers=registered_drivers,
            sim_filter=sim_filter,
        )
        print(f"\n  Using {source} ({len(plan)} simulations)")
        if sim_filter:
            print(f"  Filtered to {len(plan)} simulation(s) matching '{sim_filter}'")
    else:
        source = plan_source or "provided plan"
        print(f"\n  Using {source} ({len(plan)} simulations)")

    target_name = target.name
    results = {}

    for sim in plan:
        scenario_name = sim["scenario"]
        driver_name = sim.get("driver")
        checks = sim.get("checks", list(registered_checks.keys()))
        max_turns = max_turns_override or sim.get("max_turns", 1)
        first_turn = sim.get("first_turn", "driver")

        if scenario_name not in registered_scenarios:
            print(f"\n  ⚠ Scenario {scenario_name} not found — skipping")
            continue

        scenario = registered_scenarios[scenario_name]
        is_multi = max_turns > 1

        print(f"\n{'=' * 60}")
        print(f"  Running: {scenario_name}")
        print(f"  Mode: {'multi-turn' if is_multi else 'single-turn'} | max_turns={max_turns} | first_turn={first_turn}")
        if driver_name:
            print(f"  Driver: {driver_name}")
        print(f"  Checks: {checks}")
        print(f"{'=' * 60}")

        try:
            if is_multi and driver_name and driver_name in registered_drivers:
                driver_reg = registered_drivers[driver_name]
                driver = Driver(
                    temperature=getattr(driver_reg, "temperature", 0.6),
                    name=driver_name,
                    prompt_template=driver_reg.prompt_template,
                )
            else:
                driver = Driver(
                    temperature=0,
                    name=f"{target_name}-passthrough",
                    prompt_template=SINGLE_TURN_DRIVER_TEMPLATE,
                )

            sim_name = f"{category_prefix} {'Simulation' if is_multi else 'Eval'} — {scenario_name}"
            t0 = time.monotonic()
            test_run = okareo.run_simulation(
                target=target,
                driver=driver,
                name=sim_name,
                api_key=api_key,
                first_turn=first_turn,
                scenario=scenario,
                max_turns=max_turns,
                checks=checks,
            )
            elapsed = time.monotonic() - t0
            results[scenario_name] = {
                "test_run": test_run,
                "elapsed": elapsed,
                "checks": list(checks),
            }
            print(f"  ✓ Complete: {test_run.id} ({elapsed:.1f}s)")
            if hasattr(test_run, "app_link") and test_run.app_link:
                print(f"  View: {test_run.app_link}")
        except Exception as e:
            print(f"  ✗ Error: {e}")
            results[scenario_name] = None

    return results


def ensure_category_monitor(
    okareo,
    api_key: str,
    category_prefix: str,
    checks: list[str],
) -> str | None:
    """Ensure a single, reusable category monitor exists (idempotent)."""
    monitor_name = f"{category_prefix}-monitor"
    description = (
        "Auto-created by run_suite.py. Captures online datapoints linked to "
        "simulations via context_token."
    )

    print(f"\nPart 2 — Ensuring Monitor")
    print("-" * 40)

    target_checks = sorted(set(checks or []))

    filters = get_filters_v0_filters_get.sync(
        client=okareo.client,
        api_key=api_key,
    )
    if isinstance(filters, list):
        for existing in filters:
            if getattr(existing, "name", None) == monitor_name:
                existing_id = getattr(existing, "filter_group_id", None)
                existing_checks_raw = getattr(existing, "checks", None)
                existing_checks = (
                    sorted(existing_checks_raw)
                    if isinstance(existing_checks_raw, list)
                    else []
                )

                if existing_checks != target_checks:
                    print(
                        f"  ↻ Updating monitor checks for {monitor_name}: "
                        f"{existing_checks} -> {target_checks}"
                    )
                    try:
                        update_response = (
                            update_filter_v0_filters_filter_group_id_put.sync(
                                filter_group_id=existing_id,
                                client=okareo.client,
                                body=DatapointFilterUpdate(
                                    name=monitor_name,
                                    description=description,
                                    filters=getattr(existing, "filters", None),
                                    checks=target_checks,
                                ),
                                api_key=api_key,
                            )
                        )
                        okareo.validate_response(update_response)
                    except Exception as e:
                        print(
                            f"  ✗ Failed to update monitor {monitor_name} checks: {e}"
                        )
                        return str(existing_id) if existing_id else None

                print(
                    f"  ✓ Reusing existing monitor: {monitor_name} "
                    f"(filter_group_id={existing_id})"
                )
                return str(existing_id) if existing_id else None

    payload = DatapointFilterCreate(
        name=monitor_name,
        description=description,
        checks=target_checks,
        filters=[
            FilterCondition(
                field=DatapointField.CONTEXT_TOKEN,
                operator=ComparisonOperator.IS_SET,
                value="1",
            ),
            FilterCondition(
                field=DatapointField.SOURCE,
                operator=ComparisonOperator.NOT_EQUAL,
                value="Okareo",
            ),
        ],
    )

    try:
        response = create_filter_v0_filters_post.sync(
            client=okareo.client,
            body=payload,
            api_key=api_key,
        )
        okareo.validate_response(response)

        filter_group_id = getattr(response, "filter_group_id", None)
        print(
            f"  ✓ Created monitor: {monitor_name} "
            f"(filter_group_id={filter_group_id})"
        )
        return str(filter_group_id) if filter_group_id else None
    except Exception as e:
        print(f"  ✗ Failed to ensure monitor {monitor_name}: {e}")
        return None


# ---------------------------------------------------------------------------
# Results summary
# ---------------------------------------------------------------------------


def print_summary(category_prefix: str, results: dict):
    """Print final results table."""
    print(f"\n{'=' * 70}")
    print(f"{category_prefix} — EVALUATION RESULTS")
    print(f"{'=' * 70}")
    print(f"\n{'Scenario':<50} {'Status':<10} {'Run Time':<10} {'Run ID / Link'}")
    print("-" * 110)

    for name, result in results.items():
        if result is None:
            print(f"{name:<50} {'ERROR':<10} {'N/A':<10} N/A")
        else:
            test_run = result["test_run"]
            elapsed = result["elapsed"]
            link = getattr(test_run, "app_link", None) or test_run.id
            runtime = f"{elapsed:.1f}s"
            print(f"{name:<50} {'COMPLETE':<10} {runtime:<10} {link}")

    errors = sum(1 for r in results.values() if r is None)
    total = len(results)
    print(f"\nTotal: {total} | Completed: {total - errors} | Errors: {errors}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main():
    parser = argparse.ArgumentParser(
        description="Run an OWASP LLM compliance suite against a target agent.",
        epilog="Example: python run_suite.py --dir LLM01-prompt-injection",
    )
    parser.add_argument(
        "--dir",
        required=True,
        help="Category directory name (e.g. LLM01-prompt-injection). Resolved under owasp/.",
    )
    parser.add_argument(
        "--max-turns",
        type=int,
        default=None,
        help="Override max_turns for all simulations.",
    )
    parser.add_argument(
        "--upload-only",
        action="store_true",
        help="Upload artifacts only (skip evaluation).",
    )
    parser.add_argument(
        "--eval-only",
        action="store_true",
        help="Run evaluation only (skip artifact upload). Requires artifacts already registered.",
    )
    parser.add_argument(
        "--target",
        default=None,
        help="Path to target config file (default: owasp/target.json). Supports .json and legacy .env.",
    )
    parser.add_argument(
        "--target-env",
        default=None,
        help="Deprecated: use --target instead. Path to target config file.",
    )
    parser.add_argument(
        "--sim",
        default=None,
        help="Run only simulations whose scenario name contains this substring.",
    )
    args = parser.parse_args()

    owasp_dir = PROJECT_ROOT / "owasp"
    category_dir = owasp_dir / args.dir

    if not category_dir.exists():
        print(f"Error: Category directory not found: {category_dir}")
        sys.exit(1)

    # Derive prefix from directory name (e.g. "LLM01")
    category_prefix = args.dir.split("-")[0]

    print(f"{'=' * 60}")
    print(f"OWASP Suite Runner — {args.dir}")
    print(f"{'=' * 60}")

    okareo, api_key = init_okareo()
    print(f"✓ Okareo SDK initialized\n")

    # Part 1: Upload
    if not args.eval_only:
        print("Part 1 — Uploading Artifacts")
        print("-" * 40)
        (
            registered_scenarios,
            scenario_modes,
            scenario_checks,
            registered_checks,
            check_modes,
            registered_drivers,
        ) = upload_artifacts(okareo, category_dir, category_prefix)
    else:
        # Eval-only: still need to discover artifacts for the plan
        print("Part 1 — Skipped (--eval-only)")
        print("  Discovering artifacts for evaluation plan...")
        (
            registered_scenarios,
            scenario_modes,
            scenario_checks,
            registered_checks,
            check_modes,
            registered_drivers,
        ) = upload_artifacts(okareo, category_dir, category_prefix)

    plan, plan_source = _resolve_evaluation_plan(
        category_dir=category_dir,
        scenario_modes=scenario_modes,
        scenario_checks=scenario_checks,
        check_modes=check_modes,
        registered_drivers=registered_drivers,
        sim_filter=args.sim,
    )
    create_monitor, monitor_checks = _resolve_monitor_config_from_plan(
        plan=plan,
        registered_checks=registered_checks,
    )

    if create_monitor:
        print("Selected simulation config requires monitor setup; enabling it automatically.")
        print(f"  Monitor checks: {monitor_checks if monitor_checks else '[]'}")

    if args.upload_only:
        if create_monitor:
            ensure_category_monitor(
                okareo=okareo,
                api_key=api_key,
                category_prefix=category_prefix,
                checks=monitor_checks,
            )
        print("\n✓ Upload complete (--upload-only). Exiting.")
        return

    if create_monitor:
        ensure_category_monitor(
            okareo=okareo,
            api_key=api_key,
            category_prefix=category_prefix,
            checks=monitor_checks,
        )

    # Part 2: Evaluate
    eval_part = 3 if create_monitor else 2
    print(f"\nPart {eval_part} — Running Evaluation")
    print("-" * 40)

    target = build_target(category_dir, config_path=args.target, env_path=args.target_env)
    print(f"  Target: {target.name}")

    results = run_evaluation(
        okareo=okareo,
        api_key=api_key,
        target=target,
        category_prefix=category_prefix,
        registered_scenarios=registered_scenarios,
        scenario_modes=scenario_modes,
        scenario_checks=scenario_checks,
        registered_checks=registered_checks,
        check_modes=check_modes,
        registered_drivers=registered_drivers,
        category_dir=category_dir,
        max_turns_override=args.max_turns,
        sim_filter=args.sim,
        plan=plan,
        plan_source=plan_source,
    )

    print_summary(category_prefix, results)


if __name__ == "__main__":
    main()
