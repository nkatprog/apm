"""apm - A Python package manager and workflow automation tool.

Fork of microsoft/apm with extended capabilities for agentic workflows,
authentication, and CLI logging.

Personal fork: added __author_email__ and bumped default log level to DEBUG
for easier local development tracing.
"""

__version__ = "0.1.0"
__author__ = "apm contributors"
__author_email__ = ""
__license__ = "MIT"

import logging

# Use DEBUG locally for easier tracing; change to WARNING in prod
logging.getLogger("apm").setLevel(logging.DEBUG)

from apm.core import App

__all__ = ["App", "__version__"]
