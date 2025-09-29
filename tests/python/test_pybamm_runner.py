from __future__ import annotations

import pathlib
import sys
import tempfile
import unittest

from app.ui_qt.pybamm_runner import export_simulation_results


class ExportSimulationResultsTest(unittest.TestCase):
    def setUp(self) -> None:
        self.results = {
            "Time [s]": [0.0, 1.0, 2.0],
            "Terminal voltage [V]": [4.2, 4.1, 4.0],
        }

    def test_writes_dat_without_mdf(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            export_dir = pathlib.Path(tmpdir)
            export = export_simulation_results(
                export_dir,
                "smoke",
                self.results,
                include_mdf=False,
            )
            self.assertTrue(export.dat_path.exists())
            self.assertEqual(export.dat_path.suffix, ".dat")
            self.assertIsNone(export.mdf_path)
            self.assertFalse(export.warnings)
            content = export.dat_path.read_text(encoding="utf-8")
            self.assertIn("Time [s]\tTerminal voltage [V]", content.splitlines()[0])

    def test_warns_when_asammdf_missing(self) -> None:
        module_backup = sys.modules.pop("asammdf", None)
        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                export = export_simulation_results(
                    pathlib.Path(tmpdir),
                    "missing_mdf",
                    self.results,
                    include_mdf=True,
                )
            self.assertTrue(export.warnings)
            self.assertIsNone(export.mdf_path)
            self.assertIn("asammdf", export.warnings[0])
        finally:
            if module_backup is not None:
                sys.modules["asammdf"] = module_backup
            else:
                sys.modules.pop("asammdf", None)


if __name__ == "__main__":
    unittest.main()
