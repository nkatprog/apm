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
            json.dump(data, fh, indent=2)
            fh.write("\n")
        logger.debug("Manifest saved to %s", self.manifest_path)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def install(self, package_name: str, version: str = "latest", dev: bool = False) -> bool:
        """Install a package and record it in the manifest.

        Args:
            package_name: Name of the package to install.
            version: Version constraint (default: ``latest``).
            dev: Whether to record as a dev dependency.

        Returns:
            ``True`` on success, ``False`` otherwise.
        """
        logger.info("Installing %s@%s (dev=%s)", package_name, version, dev)
        self.packages_dir.mkdir(parents=True, exist_ok=True)

        try:
            result = subprocess.run(
                ["pip", "install", f"{package_name}=={version}" if version != "latest" else package_name],
                capture_output=True,
                text=True,
                check=True,
            )
            logger.debug(result.stdout)
        except subprocess.CalledProcessError as exc:
            logger.error("Failed to install %s: %s", package_name, exc.stderr)
            return False

        manifest = self._load_manifest()
        dep_key = "devDependencies" if dev else "dependencies"
        manifest.setdefault(dep_key, {})[package_name] = version
        self._save_manifest(manifest)
        logger.info("Package %s installed successfully.", package_name)
        return True

    def remove(self, package_name: str) -> bool:
        """Remove a package and update the manifest.

        Args:
            package_name: Name of the package to remove.

        Returns:
            ``True`` on success, ``False`` otherwise.
        """
        logger.info("Removing %s", package_name)
        try:
            result = subprocess.run(
                ["pip", "uninstall", "-y", package_name],
                capture_output=True,
                text=True,
                check=True,
            )
            logger.debug(result.stdout)
        except subprocess.CalledProcessError as exc:
            logger.error("Failed to remove %s: %s", package_name, exc.stderr)
            return False

        manifest = self._load_manifest()
        for dep_key in ("dependencies", "devDependencies"):
            manifest.get(dep_key, {}).pop(package_name, None)
        self._save_manifest(manifest)
        logger.info("Package %s removed successfully.", package_name)
        return True

    def list_packages(self) -> List[str]:
        """Return a sorted list of installed package names from the manifest."""
        manifest = self._load_manifest()
        packages: List[str] = []
        for dep_key in ("dependencies", "devDependencies"):
            packages.extend(manifest.get(dep_key, {}).keys())
        return sorted(set(packages))
