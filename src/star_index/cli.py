from __future__ import annotations

import argparse

from . import __version__
from . import build as build_cmd
from . import bundle as bundle_cmd
from . import refresh as refresh_cmd
from . import validate as validate_cmd


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="star-index",
        description="Build deterministic, agent-ready artifacts from GitHub stars.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument("command", choices=["build", "refresh", "bundle", "validate"])
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args, remaining = parser.parse_known_args(argv)

    if args.command == "build":
        return build_cmd.main(remaining)
    if args.command == "refresh":
        return refresh_cmd.main(remaining)
    if args.command == "bundle":
        return bundle_cmd.main(remaining)
    if args.command == "validate":
        return validate_cmd.main(remaining)
    parser.error(f"Unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
