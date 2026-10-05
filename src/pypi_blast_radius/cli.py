"""Command-line interface for pypi-blast-radius."""

from __future__ import annotations

import argparse
import json
import sys

from ._core import estimate_blast_radius


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="pypi-blast-radius",
        description="Estimate the downstream impact of a PyPI package version.",
    )
    parser.add_argument("package", help="PyPI package name")
    parser.add_argument("version", help="exact version, e.g. 2.31.0")
    parser.add_argument(
        "--downloads",
        type=int,
        default=0,
        help="optional monthly download count to fold into the impact proxy",
    )
    parser.add_argument("--json", action="store_true", help="emit raw JSON")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    result = estimate_blast_radius(args.package, args.version, args.downloads)
    if not result:
        print(f"No deps.dev data for {args.package}=={args.version}", file=sys.stderr)
        return 1
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        for key, value in result.items():
            print(f"{key:32} {value}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
