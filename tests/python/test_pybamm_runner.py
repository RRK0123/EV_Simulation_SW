from __future__ import annotations

import pathlib
import sys
import tempfile
import types
import unittest
from typing import Dict, List, Optional, Tuple

from app.ui_qt.pybamm_runner import export_simulation_results, run_pybamm_simulation


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


class RunPyBammSimulationTest(unittest.TestCase):
    def setUp(self) -> None:
        self.module_backup = sys.modules.pop("pybamm", None)

    def tearDown(self) -> None:
        if self.module_backup is not None:
            sys.modules["pybamm"] = self.module_backup
        else:
            sys.modules.pop("pybamm", None)

    def _install_fake_pybamm(self) -> types.SimpleNamespace:
        fake_module = types.SimpleNamespace()

        class FakeParameterValues:
            last_instance: Optional["FakeParameterValues"] = None

            def __init__(self, chemistry: object) -> None:
                self.chemistry = chemistry
                self.updated_with: Optional[Dict[str, object]] = None
                FakeParameterValues.last_instance = self

            def update(self, overrides: Dict[str, object]) -> None:
                self.updated_with = overrides

        class FakeArray:
            def __init__(self, values: List[float]) -> None:
                self._values = list(values)

            def tolist(self) -> List[float]:
                return list(self._values)

            @property
            def entries(self) -> "FakeArray":
                return self

        class FakeSolution:
            def __init__(self, t_eval: List[float]) -> None:
                self.t = FakeArray(t_eval)
                self._variables: Dict[str, FakeArray] = {
                    "Terminal voltage [V]": FakeArray([4.2 for _ in t_eval]),
                    "Custom": FakeArray(list(range(len(t_eval)))),
                }

            def __getitem__(self, name: str) -> FakeArray:
                return self._variables[name]

        class FakeSimulation:
            last_t_eval: Optional[List[float]] = None
            last_parameter_values: Optional[FakeParameterValues] = None
            last_model_instance: Optional[object] = None

            def __init__(self, model_instance: object, parameter_values: FakeParameterValues) -> None:
                type(self).last_model_instance = model_instance
                type(self).last_parameter_values = parameter_values

            def solve(self, t_eval: List[float]) -> FakeSolution:
                type(self).last_t_eval = [float(value) for value in t_eval]
                return FakeSolution(type(self).last_t_eval)

        def fake_model_factory() -> dict[str, str]:
            return {"model": "dfn"}

        def fake_linspace(start: float, stop: float, count: int) -> List[float]:
            fake_module.linspace_args = (start, stop, count)
            if count <= 1:
                return [float(start)]
            step = (stop - start) / (count - 1)
            return [float(start + step * index) for index in range(count)]

        fake_module.ParameterValues = FakeParameterValues
        fake_module.Simulation = FakeSimulation
        fake_module.linspace = fake_linspace
        fake_module.linspace_args: Optional[Tuple[float, float, int]] = None
        fake_module.parameter_sets = types.SimpleNamespace(TestSet="chemistry_source")
        fake_module.lithium_ion = types.SimpleNamespace(DFN=fake_model_factory)

        sys.modules["pybamm"] = fake_module
        return fake_module

    def test_runs_simulation_with_overrides_and_extra_variables(self) -> None:
        fake_module = self._install_fake_pybamm()

        results = run_pybamm_simulation(
            chemistry="lithium_ion",
            model="DFN",
            parameter_set="TestSet",
            overrides={"My parameter": 3.14},
            t_eval=[0, 10, 20],
            extra_variables=["Custom"],
        )

        self.assertIn("Time [s]", results)
        self.assertEqual(results["Time [s]"], [0.0, 10.0, 20.0])
        self.assertEqual(results["Custom"], [0, 1, 2])
        parameter_values = fake_module.ParameterValues.last_instance
        self.assertIsNotNone(parameter_values)
        self.assertEqual(parameter_values.chemistry, "chemistry_source")
        self.assertEqual(parameter_values.updated_with, {"My parameter": 3.14})
        self.assertEqual(fake_module.Simulation.last_t_eval, [0.0, 10.0, 20.0])
        self.assertEqual(fake_module.Simulation.last_model_instance, {"model": "dfn"})

    def test_uses_default_time_grid_when_t_eval_missing(self) -> None:
        fake_module = self._install_fake_pybamm()

        results = run_pybamm_simulation(
            chemistry="lithium_ion",
            model="DFN",
            parameter_set="TestSet",
            overrides={},
        )

        self.assertIn("Time [s]", results)
        self.assertEqual(fake_module.linspace_args, (0, 3600, 361))
        self.assertEqual(len(results["Time [s]"]), 361)
        self.assertEqual(len(results["Terminal voltage [V]"]), 361)

if __name__ == "__main__":
    unittest.main()
