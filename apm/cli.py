"""Command-line interface for apm (Another Package Manager)."""

import sys
import argparse
import logging
from typing import Optional

from apm import __version__

logger = logging.getLogger(__name__)


def build_parser() -> argparse.ArgumentParser:
    """Build and return the argument parser for the apm CLI."""
    parser = argparse.ArgumentParser(
        prog="apm",
        description="apm — a package manager utility",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--version", "-V",
        action="version",
        version=f"apm {__version__}",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        default=False,
        help="Enable verbose/debug output.",
    )
    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        default=False,
        help="Suppress non-error output.",
    )

    subparsers = parser.add_subparsers(dest="command", metavar="<command>")

    # install
    install_parser = subparsers.add_parser("install", help="Install a package.")
    install_parser.add_argument("packages", nargs="+", metavar="PACKAGE", help="Package(s) to install.")
    install_parser.add_argument("--save", action="store_true", help="Save to dependencies.")
    install_parser.add_argument("--save-dev", action="store_true", help="Save to dev dependencies.")

    # uninstall
    uninstall_parser = subparsers.add_parser("uninstall", aliases=["remove"], help="Uninstall a package.")
    uninstall_parser.add_argument("packages", nargs="+", metavar="PACKAGE", help="Package(s) to uninstall.")

    # list
    subparsers.add_parser("list", help="List installed packages.")

    # update
    update_parser = subparsers.add_parser("update", help="Update package(s).")
    update_parser.add_argument("packages", nargs="*", metavar="PACKAGE", help="Package(s) to update (all if omitted).")

    # search
    search_parser = subparsers.add_parser("search", help="Search for packages.")
    search_parser.add_argument("query", help="Search query string.")

    return parser


def configure_logging(verbose: bool = False, quiet: bool = False) -> None:
    """Configure root logger based on verbosity flags."""
    if quiet:
        level = logging.ERROR
    elif verbose:
        level = logging.DEBUG
    else:
        level = logging.INFO

    logging.basicConfig(
        level=level,
        format="%(levelname)s: %(message)s",
        stream=sys.stderr,
    )


def main(argv: Optional[list] = None) -> int:
    """Entry point for the apm CLI.

    Args:
        argv: Argument list (defaults to sys.argv).

    Returns:
        Exit code (0 for success, non-zero for failure).
    """
    parser = build_parser()
    args = parser.parse_args(argv)

    configure_logging(verbose=args.verbose, quiet=args.quiet)

    if args.command is None:
        parser.print_help()
        return 0

    logger.debug("Running command: %s", args.command)

    # Dispatch to subcommand handlers (stubs — to be implemented per module)
    command = args.command

    if command == "install":
        logger.info("Installing: %s", ", ".join(args.packages))
    elif command in ("uninstall", "remove"):
        logger.info("Uninstalling: %s", ", ".join(args.packages))
    elif command == "list":
        logger.info("Listing installed packages...")
    elif command == "update":
        targets = args.packages or ["all packages"]
        logger.info("Updating: %s", ", ".join(targets))
    elif command == "search":
        logger.info("Searching for: %s", args.query)
    else:
        logger.error("Unknown command: %s", command)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
