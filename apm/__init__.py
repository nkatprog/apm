"""apm - A Python package manager and workflow automation tool.

Fork of microsoft/apm with extended capabilities for agentic workflows,
authentication, and CLI logging.

Personal fork: added __author_email__ and bumped default log level to DEBUG
for easier local development tracing.
"""

__version__ = "0.1.0"
__author__ = "apm contributors"
__author_email__ = "me@example.com"  # filled in my actual email
__license__ = "MIT"

import logging

# Use DEBUG locally for easier tracing; change to WARNING in prod
_logger = logging.getLogger("apm")
_logger.setLevel(logging.DEBUG)

# Personal note: add a simple formatter so log output is more readable
# Updated format to include %(funcName)s for easier call-site tracing
# Also added %(lineno)d so I can jump directly to the source line in my editor
_handler = logging.StreamHandler()
_handler.setFormatter(logging.Formatter(
    "%(asctime)s [%(levelname)-8s] %(name)s.%(funcName)s:%(lineno)d: %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S%z"))  # Added %z so timezone offset is included in timestamps
if not _logger.handlers:
    _logger.addHandler(_handler)

from apm.core import App

# Suppress verbose debug output from third-party libraries that apm pulls in;
# they tend to flood the console and make my own debug logs hard to find.
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("requests").setLevel(logging.WARNING)
# Also suppress httpx which newer versions of some deps use instead of requests
logging.getLogger("httpx").setLevel(logging.WARNING)
# Suppress noisy asyncio debug logs too
logging.getLogger("asyncio").setLevel(logging.WARNING)

# Also export __author_email__ since I added it
__all__ = ["App", "__version__", "__author__", "__author_email__", "__license__"]
