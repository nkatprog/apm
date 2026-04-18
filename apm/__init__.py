"""apm - A Python package manager and workflow automation tool.

Fork of microsoft/apm with extended capabilities for agentic workflows,
authentication, and CLI logging.
"""

__version__ = "0.1.0"
__author__ = "apm contributors"
__license__ = "MIT"

from apm.core import App

__all__ = ["App", "__version__"]
