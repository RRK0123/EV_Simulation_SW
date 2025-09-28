from __future__ import annotations

import pathlib
import sys
from typing import Optional

try:
    from PySide6 import QtCore, QtGui, QtQml
except ImportError as exc:  # pragma: no cover - optional dependency
    raise SystemExit("PySide6 is required to launch the Qt UI") from exc

from orchestrator_client import OrchestratorClient
from parameter_bridge import ParameterBridge


class SimulationController(QtCore.QObject):
    runCompleted = QtCore.Signal(str)
    runFailed = QtCore.Signal(str)

    def __init__(self, parent: Optional[QtCore.QObject] = None) -> None:
        super().__init__(parent)
        self._client: Optional[OrchestratorClient] = None

    @QtCore.Slot()
    def run_scenario(self) -> None:
        try:
            if self._client is None:
                self._client = OrchestratorClient()
            self._client.run_default_scenario(1.0, 120)
            self.runCompleted.emit("Simulation finished")
        except Exception as exc:  # pragma: no cover - UI path
            self.runFailed.emit(str(exc))


def main() -> int:
    app = QtGui.QGuiApplication(sys.argv)
    engine = QtQml.QQmlApplicationEngine()

    controller = SimulationController()
    engine.rootContext().setContextProperty("simulationController", controller)

    scenario_path = pathlib.Path(__file__).resolve().parents[2] / "configs" / "scenarios" / "default.yaml"
    parameter_bridge = ParameterBridge(scenario_path)
    engine.rootContext().setContextProperty("parameterBridge", parameter_bridge)

    qml_path = pathlib.Path(__file__).parent / "qml" / "Main.qml"
    engine.load(QtCore.QUrl.fromLocalFile(str(qml_path)))

    if not engine.rootObjects():
        return -1
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
