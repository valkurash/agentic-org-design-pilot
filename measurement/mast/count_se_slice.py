#!/usr/bin/env python3
"""Summarize MAST-Data: full corpus + ProgramDev (SE) slice (§2 epidemiology)."""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path

DEFAULT_DATA = Path(__file__).resolve().parent / "data/raw/MAST-Data/MAD_full_dataset.json"
DEFAULT_OUT = Path(__file__).resolve().parent / "data/summary/se_slice_stats.json"

SE_BENCHMARKS = frozenset({"ProgramDev"})
SE_MAS = frozenset({"MetaGPT", "ChatDev", "OpenManus"})


def load_records(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def summarize(records: list[dict]) -> dict:
    by_benchmark = Counter(r["benchmark_name"] for r in records)
    by_mas = Counter(r["mas_name"] for r in records)
    by_llm = Counter(r["llm_name"] for r in records)

    program_dev = [r for r in records if r["benchmark_name"] in SE_BENCHMARKS]
    se_mas = [r for r in program_dev if r["mas_name"] in SE_MAS]

    se_by_mas = Counter(r["mas_name"] for r in se_mas)
    se_by_llm = Counter(r["llm_name"] for r in se_mas)
    se_mas_llm: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    for r in se_mas:
        se_mas_llm[r["mas_name"]][r["llm_name"]] += 1

    mast_any = sum(1 for r in records if any(r["mast_annotation"].values()))
    se_mast_any = sum(1 for r in se_mas if any(r["mast_annotation"].values()))

    mode_totals = Counter()
    se_mode_totals = Counter()
    for r in records:
        for mode, flag in r["mast_annotation"].items():
            if flag:
                mode_totals[mode] += 1
    for r in se_mas:
        for mode, flag in r["mast_annotation"].items():
            if flag:
                se_mode_totals[mode] += 1

    return {
        "source_file": "MAD_full_dataset.json",
        "total_records": len(records),
        "frameworks": len(by_mas),
        "benchmarks": dict(by_benchmark.most_common()),
        "mas_name": dict(by_mas.most_common()),
        "llm_name": dict(by_llm.most_common()),
        "mast_any_failure_flag": mast_any,
        "program_dev": {
            "total": len(program_dev),
            "se_mas_subset": {
                "frameworks": sorted(SE_MAS),
                "total": len(se_mas),
                "by_mas": dict(se_by_mas.most_common()),
                "by_llm": dict(se_by_llm.most_common()),
                "by_mas_llm": {k: dict(v) for k, v in sorted(se_mas_llm.items())},
                "mast_any_failure_flag": se_mast_any,
                "mast_mode_counts": dict(se_mode_totals.most_common()),
            },
        },
        "mast_mode_counts_all": dict(mode_totals.most_common()),
        "notes": {
            "se_slice_definition": "benchmark_name=ProgramDev AND mas_name in MetaGPT|ChatDev|OpenManus",
            "use_for_epidemiology": "se_mas_subset (primary); full corpus for context checks",
            "public_release_count": "1242 traces (paper marketing '1600+' is outdated)",
        },
    }


def print_report(stats: dict) -> None:
    pd = stats["program_dev"]
    se = pd["se_mas_subset"]
    print("MAST-Data summary")
    print("=" * 50)
    print(f"Total records:     {stats['total_records']}")
    print(f"Frameworks:        {stats['frameworks']}")
    print(f"Any MAST failure:  {stats['mast_any_failure_flag']}")
    print()
    print("By benchmark:")
    for name, count in stats["benchmarks"].items():
        print(f"  {name:20} {count:5}")
    print()
    print("ProgramDev (all MAS):", pd["total"])
    print("SE subset (MetaGPT + ChatDev + OpenManus):", se["total"])
    print("  by framework:")
    for name, count in se["by_mas"].items():
        print(f"    {name:12} {count:5}")
    print("  by LLM:")
    for name, count in se["by_llm"].items():
        print(f"    {name:12} {count:5}")
    print(f"  any MAST failure: {se['mast_any_failure_flag']}")
    print()
    print("Top MAST modes (SE subset):")
    for mode, count in list(se["mast_mode_counts"].items())[:8]:
        print(f"  {mode:6} {count:5}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--data",
        type=Path,
        default=DEFAULT_DATA,
        help=f"Path to MAD_full_dataset.json (default: {DEFAULT_DATA})",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=DEFAULT_OUT,
        help=f"Write JSON summary here (default: {DEFAULT_OUT})",
    )
    parser.add_argument("--no-write", action="store_true", help="Print only, do not write JSON")
    args = parser.parse_args()

    if not args.data.is_file():
        raise SystemExit(f"Dataset not found: {args.data}\nDownload: hf download mcemri/MAST-Data --repo-type dataset --local-dir {args.data.parent}")

    records = load_records(args.data)
    stats = summarize(records)
    print_report(stats)

    if not args.no_write:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(stats, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print()
        print(f"Wrote {args.out}")


if __name__ == "__main__":
    main()
