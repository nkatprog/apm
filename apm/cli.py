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

    # Use a more informative format when in debug/verbose mode
    fmt = "%(asctime)s %(levelname)s [%(name)s]: %(message)s" if verbose else "%(levelname)s: %(message)s"

    logging.basicConfig(
        level=level,
        format=fmt,
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

    # Print help and exit cleanly when no subcommand is given
    if args.command is None:
        parser.print_help(sys.stderr)
        return 1

    #
