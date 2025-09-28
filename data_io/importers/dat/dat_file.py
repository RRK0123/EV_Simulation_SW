"""DAT importer scaffold."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, Tuple

from ..base import Importer


@dataclass(slots=True)
class DatImporter(Importer):
    format: str = "dat"

    def import_file(self, path: str, mapping: Dict[str, str]) -> Tuple[Iterable[Dict[str, float]], Dict[str, str]]:
        metadata = {"source_path": path, "channel_mapping": mapping}
        return [], metadata


__all__ = ["DatImporter"]

