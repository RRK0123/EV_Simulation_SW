from __future__ import annotations

import ctypes
import ctypes.util
import pathlib
from typing import Optional


class OrchestratorClient:
    """Thin ctypes-based bridge to the evsim_core shared library."""

    def __init__(self, library_path: Optional[pathlib.Path] = None) -> None:
        self._handle = None
        self._lib = self._load_library(library_path)
        self._lib.evsim_create_orchestrator.restype = ctypes.c_void_p
        self._lib.evsim_destroy_orchestrator.argtypes = [ctypes.c_void_p]
        self._lib.evsim_run_default_scenario.argtypes = [ctypes.c_void_p, ctypes.c_double, ctypes.c_uint32]
        self._lib.evsim_run_default_scenario.restype = ctypes.c_int
        handle = self._lib.evsim_create_orchestrator()
        if not handle:
            raise RuntimeError("Failed to create orchestrator instance")
        self._handle = ctypes.c_void_p(handle)

    def _load_library(self, library_path: Optional[pathlib.Path]) -> ctypes.CDLL:
        candidates = []
        if library_path is not None:
            candidates.append(pathlib.Path(library_path))
        module_path = pathlib.Path(__file__).resolve().parent.parent
        candidates.append(module_path / ".." / ".." / "build" / "libevsim_core.so")
        candidates.append(module_path / ".." / ".." / "build" / "Debug" / "evsim_core.dll")
        system_name = ctypes.util.find_library("evsim_core")
        if system_name:
            candidates.append(pathlib.Path(system_name))

        for candidate in candidates:
            if candidate and candidate.exists():
                return ctypes.cdll.LoadLibrary(str(candidate))
        raise FileNotFoundError("Could not locate evsim_core shared library")

    def run_default_scenario(self, time_step: float = 1.0, steps: int = 60) -> None:
        if not self._handle:
            raise RuntimeError("Orchestrator not initialised")
        result = self._lib.evsim_run_default_scenario(self._handle, time_step, steps)
        if result != 0:
            raise RuntimeError(f"Simulation run failed with code {result}")

    def close(self) -> None:
        if self._handle:
            self._lib.evsim_destroy_orchestrator(self._handle)
            self._handle = None

    def __enter__(self) -> "OrchestratorClient":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()


__all__ = ["OrchestratorClient"]
