"""MDF4 importer scaffold."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, Tuple

from ..base import Importer


@dataclass(slots=True)
class MDF4Importer(Importer):
    format: str = "mdf4"

    def import_file(self, path: str, mapping: Dict[str, str]) -> Tuple[Iterable[Dict[str, float]], Dict[str, str]]:
        # Placeholder implementation returning no samples and metadata stub.
        metadata = {"source_path": path, "channel_mapping": mapping}
        return [], metadata


__all__ = ["MDF4Importer"]

