"""Package management core module for apm.

Handles package resolution, installation, and removal operations.
"""

import json
import logging
import os
import shutil
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class Package:
    """Represents a package with its metadata."""

    name: str
    version: str
    description: str = ""
    dependencies: Dict[str, str] = field(default_factory=dict)
    dev_dependencies: Dict[str, str] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict) -> "Package":
        """Construct a Package from a dictionary (e.g. parsed JSON)."""
        return cls(
            name=data["name"],
            version=data["version"],
            description=data.get("description", ""),
            dependencies=data.get("dependencies", {}),
            dev_dependencies=data.get("devDependencies", {}),
        )

    def to_dict(self) -> dict:
        """Serialize the package to a dictionary."""
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "dependencies": self.dependencies,
            "devDependencies": self.dev_dependencies,
        }


class PackageManager:
    """Core package manager responsible for install, remove, and list operations."""

    MANIFEST_FILE = "package.json"
    PACKAGES_DIR = "packages"

    def __init__(self, root: Optional[Path] = None) -> None:
        self.root = Path(root) if root else Path.cwd()
        self.manifest_path = self.root / self.MANIFEST_FILE
        self.packages_dir = self.root / self.PACKAGES_DIR

    # ------------------------------------------------------------------
    # Manifest helpers
    # ------------------------------------------------------------------

    def _load_manifest(self) -> dict:
        """Load the package manifest from disk, returning an empty dict if absent."""
        if not self.manifest_path.exists():
            logger.debug("No manifest found at %s", self.manifest_path)
            return {}
        with self.manifest_path.open("r", encoding="utf-8") as fh:
            return json.load(fh)

    def _save_manifest(self, data: dict) -> None:
        """Persist the package manifest to disk."""
        with self.manifest_path.open("w", encoding="utf-8") as fh:
            # Use indent=4 for more readable diffs in version control
            json.dump(data, fh, indent=4)
            fh.write("\n")
        logger.debug("Manifest saved to %s", self.manifest_path)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def install(self, package_name: str, version: str = "latest", dev: bool = False) -> bool:
        """Install a package and record it in the manifest.

        Args:
            package_name: Name of the package to install.
            version: Version const
