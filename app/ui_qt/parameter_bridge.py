from __future__ import annotations

import json
import numbers
import pathlib
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


def _serialise_value(value: Any) -> Any:
    if hasattr(value, "_scalar"):
        value = value.value
    if hasattr(value, "value") and isinstance(value.value, numbers.Number):
        value = value.value
    if isinstance(value, bool):
        return bool(value)
    if isinstance(value, numbers.Integral):
        return int(value)
    if isinstance(value, numbers.Real):
        return float(value)
    return value

from PySide6 import QtCore

try:
    import yaml  # type: ignore
except ImportError:  # pragma: no cover - runtime optional dependency
    yaml = None  # type: ignore


@dataclass
class ParameterDefinition:
    identifier: str
    name: str
    label: str
    type: str
    default: Any
    value: Any
    unit: str
    category: str
    advanced: bool
    description: str = ""
    minimum: Optional[float] = None
    maximum: Optional[float] = None
    step: Optional[float] = None
    choices: List[Dict[str, Any]] = field(default_factory=list)
    source: Optional[str] = None
    override: Optional[Any] = None


class ParameterListModel(QtCore.QAbstractListModel):
    IdRole = QtCore.Qt.UserRole + 1
    LabelRole = IdRole + 1
    TypeRole = LabelRole + 1
    ValueRole = TypeRole + 1
    DefaultRole = ValueRole + 1
    UnitRole = DefaultRole + 1
    CategoryRole = UnitRole + 1
    AdvancedRole = CategoryRole + 1
    DescriptionRole = AdvancedRole + 1
    MinRole = DescriptionRole + 1
    MaxRole = MinRole + 1
    StepRole = MaxRole + 1
    ChoicesRole = StepRole + 1
    DirtyRole = ChoicesRole + 1

    def __init__(self, parent: Optional[QtCore.QObject] = None) -> None:
        super().__init__(parent)
        self._items: List[ParameterDefinition] = []
        self._change_callback: Optional[Any] = None

    def set_change_callback(self, callback: Any) -> None:
        self._change_callback = callback

    def roleNames(self) -> Dict[int, QtCore.QByteArray]:  # type: ignore[override]
        return {
            self.IdRole: b"id",
            self.LabelRole: b"label",
            self.TypeRole: b"type",
            self.ValueRole: b"value",
            self.DefaultRole: b"default",
            self.UnitRole: b"unit",
            self.CategoryRole: b"category",
            self.AdvancedRole: b"advanced",
            self.DescriptionRole: b"description",
            self.MinRole: b"minimum",
            self.MaxRole: b"maximum",
            self.StepRole: b"step",
            self.ChoicesRole: b"choices",
            self.DirtyRole: b"dirty",
        }

    def rowCount(self, parent: QtCore.QModelIndex = QtCore.QModelIndex()) -> int:  # type: ignore[override]
        if parent.isValid():
            return 0
        return len(self._items)

    def data(self, index: QtCore.QModelIndex, role: int = QtCore.Qt.DisplayRole) -> Any:  # type: ignore[override]
        if not index.isValid():
            return None
        item = self._items[index.row()]
        if role == self.IdRole:
            return item.identifier
        if role == self.LabelRole:
            return item.label
        if role == self.TypeRole:
            return item.type
        if role == self.ValueRole:
            return item.value
        if role == self.DefaultRole:
            return item.default
        if role == self.UnitRole:
            return item.unit
        if role == self.CategoryRole:
            return item.category
        if role == self.AdvancedRole:
            return item.advanced
        if role == self.DescriptionRole:
            return item.description
        if role == self.MinRole:
            return item.minimum
        if role == self.MaxRole:
            return item.maximum
        if role == self.StepRole:
            return item.step
        if role == self.ChoicesRole:
            return item.choices
        if role == self.DirtyRole:
            return item.override is not None
        return None

    def flags(self, index: QtCore.QModelIndex) -> QtCore.Qt.ItemFlags:  # type: ignore[override]
        if not index.isValid():
            return QtCore.Qt.NoItemFlags
        return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsEditable

    def setData(self, index: QtCore.QModelIndex, value: Any, role: int = QtCore.Qt.EditRole) -> bool:  # type: ignore[override]
        if not index.isValid() or role != self.ValueRole:
            return False
        item = self._items[index.row()]
        clean_value = self._normalise_value(value, item.type)
        if clean_value == item.value:
            return False
        item.value = clean_value
        if clean_value == item.default:
            item.override = None
        else:
            item.override = clean_value
        self.dataChanged.emit(index, index, [self.ValueRole, self.DirtyRole])
        if self._change_callback is not None:
            self._change_callback(item.identifier, item)
        return True

    def _normalise_value(self, value: Any, param_type: str) -> Any:
        if param_type in {"number", "integer"} and isinstance(value, str):
            try:
                value = float(value)
            except ValueError:
                return value
        if param_type == "integer" and isinstance(value, numbers.Real):
            return int(value)
        if param_type == "number" and isinstance(value, numbers.Real):
            return float(value)
        if param_type == "bool" and isinstance(value, str):
            return value.lower() in {"true", "1", "yes", "on"}
        return value

    def set_items(self, items: List[ParameterDefinition]) -> None:
        self.beginResetModel()
        self._items = items
        self.endResetModel()

    def update_defaults(self, defaults: Dict[str, Any]) -> None:
        changed_indexes: List[QtCore.QModelIndex] = []
        for row, item in enumerate(self._items):
            if item.identifier in defaults:
                item.default = defaults[item.identifier]
                if item.override is None:
                    if item.value != item.default:
                        item.value = item.default
                        changed_indexes.append(self.index(row, 0))
                elif item.override == item.default:
                    item.override = None
                    if item.value != item.default:
                        item.value = item.default
                    changed_indexes.append(self.index(row, 0))
        if changed_indexes:
            for index in changed_indexes:
                self.dataChanged.emit(index, index, [self.DefaultRole, self.ValueRole, self.DirtyRole])

    def set_overrides(self, overrides: Dict[str, Any]) -> None:
        changed: List[QtCore.QModelIndex] = []
        for row, item in enumerate(self._items):
            if item.identifier in overrides:
                new_value = overrides[item.identifier]
                if item.value != new_value:
                    item.value = new_value
                    item.override = new_value if new_value != item.default else None
                    changed.append(self.index(row, 0))
            else:
                if item.override is not None:
                    item.override = None
                    if item.value != item.default:
                        item.value = item.default
                        changed.append(self.index(row, 0))
        if changed:
            for index in changed:
                self.dataChanged.emit(index, index, [self.ValueRole, self.DirtyRole])

    def items(self) -> List[ParameterDefinition]:
        return list(self._items)


class ParameterFilterModel(QtCore.QSortFilterProxyModel):
    def __init__(self, *, diff_only: bool = False, parent: Optional[QtCore.QObject] = None) -> None:
        super().__init__(parent)
        self._search: str = ""
        self._category: str = ""
        self._show_advanced: bool = True
        self._diff_only = diff_only
        self.setDynamicSortFilter(True)

    def set_search(self, text: str) -> None:
        if text == self._search:
            return
        self._search = text
        self.invalidateFilter()

    def set_category(self, category: str) -> None:
        if category == self._category:
            return
        self._category = category
        self.invalidateFilter()

    def set_show_advanced(self, show: bool) -> None:
        if show == self._show_advanced:
            return
        self._show_advanced = show
        self.invalidateFilter()

    def set_diff_only(self, diff_only: bool) -> None:
        if diff_only == self._diff_only:
            return
        self._diff_only = diff_only
        self.invalidateFilter()

    def filterAcceptsRow(self, source_row: int, source_parent: QtCore.QModelIndex) -> bool:  # type: ignore[override]
        index = self.sourceModel().index(source_row, 0, source_parent)
        if not index.isValid():
            return False
        label = self.sourceModel().data(index, ParameterListModel.LabelRole)
        name = self.sourceModel().data(index, ParameterListModel.IdRole)
        category = self.sourceModel().data(index, ParameterListModel.CategoryRole)
        advanced = self.sourceModel().data(index, ParameterListModel.AdvancedRole)
        dirty = self.sourceModel().data(index, ParameterListModel.DirtyRole)
        if self._diff_only and not dirty:
            return False
        if not self._show_advanced and advanced:
            return False
        if self._category and category != self._category:
            return False
        if self._search:
            haystack = f"{label} {name}".lower()
            if self._search.lower() not in haystack:
                return False
        return True


class ScenarioStore:
    def __init__(self, path: pathlib.Path) -> None:
        self.path = path
        self._data: Dict[str, Any] = {}
        self.load()

    def load(self) -> None:
        if yaml is None:
            raise RuntimeError("PyYAML is required to load scenario files")
        if not self.path.exists():
            raise FileNotFoundError(f"Scenario file not found: {self.path}")
        with self.path.open("r", encoding="utf-8") as handle:
            self._data = yaml.safe_load(handle) or {}

    def save(self) -> None:
        if yaml is None:
            raise RuntimeError("PyYAML is required to save scenario files")
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("w", encoding="utf-8") as handle:
            yaml.safe_dump(self._data, handle, sort_keys=False)

    @property
    def pybamm_config(self) -> Dict[str, Any]:
        return self._data.setdefault("pybamm", {})

    @property
    def overrides(self) -> Dict[str, Any]:
        return self.pybamm_config.setdefault("overrides", {})

    def set_override(self, identifier: str, value: Optional[Any]) -> None:
        overrides = self.overrides
        if value is None or value == "":
            overrides.pop(identifier, None)
        else:
            overrides[identifier] = value
        self.save()

    def set_overrides(self, overrides: Dict[str, Any]) -> None:
        self.pybamm_config["overrides"] = overrides
        self.save()

    @property
    def schema_path(self) -> pathlib.Path:
        rel = self.pybamm_config.get("parameter_schema")
        if not rel:
            raise ValueError("Scenario missing pybamm.parameter_schema entry")
        base = self.path.resolve().parents[2]
        return (base / rel).resolve()

    @property
    def chemistry(self) -> str:
        return self.pybamm_config.get("chemistry", "lithium_ion")

    @property
    def model(self) -> str:
        return self.pybamm_config.get("model", "DFN")

    @property
    def presets(self) -> List[Dict[str, Any]]:
        return list(self.pybamm_config.get("presets", []))

    @property
    def current_preset(self) -> str:
        return self.pybamm_config.get("default_preset", "")

    def set_current_preset(self, preset_id: str) -> None:
        self.pybamm_config["default_preset"] = preset_id
        self.save()


class PyBammProcessor(QtCore.QObject):
    previewReady = QtCore.Signal(dict)
    progressUpdated = QtCore.Signal(str, float)
    errorOccurred = QtCore.Signal(str)

    def __init__(self, parent: Optional[QtCore.QObject] = None) -> None:
        super().__init__(parent)
        self._debounce_timer = QtCore.QTimer(self)
        self._debounce_timer.setSingleShot(True)
        self._debounce_timer.timeout.connect(self._process)
        self._pending_overrides: Dict[str, Any] = {}
        self._id_to_name: Dict[str, str] = {}
        self._chemistry = "lithium_ion"
        self._model = "DFN"
        self._preset = "Chen2020"

    def configure(self, *, id_to_name: Dict[str, str], chemistry: str, model: str, preset: str) -> None:
        self._id_to_name = dict(id_to_name)
        self._chemistry = chemistry
        self._model = model
        self._preset = preset or self._preset

    def set_preset(self, preset: str) -> None:
        if preset:
            self._preset = preset

    def schedule(self, overrides: Dict[str, Any], debounce_ms: int = 250) -> None:
        self._pending_overrides = dict(overrides)
        self._debounce_timer.start(debounce_ms)

    def _process(self) -> None:
        try:
            import pybamm  # type: ignore
        except ImportError:  # pragma: no cover - optional dependency
            self.errorOccurred.emit("PyBaMM is not available in the runtime environment")
            return
        try:
            chemistry_module = getattr(pybamm, self._chemistry)
            model_factory = getattr(chemistry_module, self._model)
            parameter_set = getattr(pybamm.parameter_sets, self._preset)
        except AttributeError as exc:  # pragma: no cover - invalid configuration
            self.errorOccurred.emit(str(exc))
            return
        model = model_factory()
        parameter_values = pybamm.ParameterValues(chemistry=parameter_set)
        pybamm.logger.verbose = False  # silence detailed logs
        self.progressUpdated.emit("processing", 0.05)
        parameter_values.process_model(model)
        override_payload: Dict[str, Any] = {}
        for identifier, value in self._pending_overrides.items():
            name = self._id_to_name.get(identifier)
            if not name:
                continue
            override_payload[name] = value
        if override_payload:
            parameter_values.update(override_payload)
        self.progressUpdated.emit("processing", 0.6)
        preview: Dict[str, Any] = {
            "preset": self._preset,
            "override_count": len(override_payload),
        }
        sample_keys = [name for name in ["Nominal cell capacity [A.h]", "Negative electrode thickness [m]"] if name in parameter_values]
        for key in sample_keys:
            try:
                preview[key] = _serialise_value(parameter_values[key])
            except Exception:  # pragma: no cover - parameter evaluation error
                continue
        self.progressUpdated.emit("processing", 0.95)
        self.previewReady.emit(preview)
        self.progressUpdated.emit("done", 1.0)

    def collect_defaults(self, preset: str) -> Dict[str, Any]:
        try:
            import pybamm  # type: ignore
        except ImportError:  # pragma: no cover - optional dependency
            return {}
        try:
            chemistry_module = getattr(pybamm, self._chemistry)
            model_factory = getattr(chemistry_module, self._model)
            parameter_set = getattr(pybamm.parameter_sets, preset)
        except AttributeError:
            return {}
        model = model_factory()
        parameter_values = pybamm.ParameterValues(chemistry=parameter_set)
        parameter_values.process_model(model)
        defaults: Dict[str, Any] = {}
        for identifier, name in self._id_to_name.items():
            try:
                value = _serialise_value(parameter_values[name])
            except KeyError:
                continue
            defaults[identifier] = value
        return defaults


class ParameterBridge(QtCore.QObject):
    schemaLoaded = QtCore.Signal()
    presetsChanged = QtCore.Signal()
    categoriesChanged = QtCore.Signal()
    overridesChanged = QtCore.Signal()
    previewReady = QtCore.Signal(dict)
    progressUpdated = QtCore.Signal(str, float)
    errorOccurred = QtCore.Signal(str)

    def __init__(self, scenario_path: pathlib.Path, parent: Optional[QtCore.QObject] = None) -> None:
        super().__init__(parent)
        self._scenario = ScenarioStore(scenario_path)
        self._model = ParameterListModel(self)
        self._model.set_change_callback(self._on_value_changed)
        self._filtered_model = ParameterFilterModel(parent=self)
        self._filtered_model.setSourceModel(self._model)
        self._diff_model = ParameterFilterModel(diff_only=True, parent=self)
        self._diff_model.setSourceModel(self._model)
        self._categories: List[str] = []
        self._presets = self._scenario.presets
        self._current_preset = self._scenario.current_preset or (self._presets[0]["id"] if self._presets else "")
        self._id_to_name: Dict[str, str] = {}
        self._processor = PyBammProcessor(self)
        self._processor.previewReady.connect(self.previewReady)
        self._processor.progressUpdated.connect(self.progressUpdated)
        self._processor.errorOccurred.connect(self.errorOccurred)
        self._load_schema()

    @QtCore.Slot(str)
    def setSearchQuery(self, text: str) -> None:
        self._filtered_model.set_search(text)
        self._diff_model.set_search(text)

    @QtCore.Slot(str)
    def setCategoryFilter(self, category: str) -> None:
        category_value = "" if category in {"", "All"} else category
        self._filtered_model.set_category(category_value)
        self._diff_model.set_category(category_value)

    @QtCore.Slot(bool)
    def setShowAdvanced(self, show: bool) -> None:
        self._filtered_model.set_show_advanced(show)
        self._diff_model.set_show_advanced(show)

    @QtCore.Slot()
    def resetOverrides(self) -> None:
        self._scenario.set_overrides({})
        self._model.set_overrides({})
        self._processor.schedule({})
        self.overridesChanged.emit()

    @QtCore.Slot(str)
    def applyPreset(self, preset_id: str) -> None:
        if not preset_id or preset_id == self._current_preset:
            return
        self._current_preset = preset_id
        self._scenario.set_current_preset(preset_id)
        self._processor.set_preset(preset_id)
        defaults = self._processor.collect_defaults(preset_id)
        if defaults:
            self._model.update_defaults(defaults)
        self._processor.schedule(self._scenario.overrides)
        self.presetsChanged.emit()

    @QtCore.Slot(str)
    def exportOverrides(self, name: str) -> None:
        if yaml is None:
            self.errorOccurred.emit("PyYAML is required to export overrides")
            return
        target_dir = self._scenario.path.parent.parent / "overrides"
        target_dir.mkdir(parents=True, exist_ok=True)
        target_path = target_dir / f"{name}.yaml"
        with target_path.open("w", encoding="utf-8") as handle:
            yaml.safe_dump(self._scenario.overrides, handle, sort_keys=True)

    @QtCore.Slot(str)
    def importOverrides(self, name: str) -> None:
        if yaml is None:
            self.errorOccurred.emit("PyYAML is required to import overrides")
            return
        source_path = self._scenario.path.parent.parent / "overrides" / f"{name}.yaml"
        if not source_path.exists():
            self.errorOccurred.emit(f"Override preset '{name}' not found")
            return
        with source_path.open("r", encoding="utf-8") as handle:
            overrides = yaml.safe_load(handle) or {}
        self._scenario.set_overrides(overrides)
        self._model.set_overrides(overrides)
        self._processor.schedule(overrides)
        self.overridesChanged.emit()

    def _load_schema(self) -> None:
        schema_path = self._scenario.schema_path
        if not schema_path.exists():
            raise FileNotFoundError(f"Parameter schema not found: {schema_path}")
        with schema_path.open("r", encoding="utf-8") as handle:
            schema_data = json.load(handle)
        overrides = self._scenario.overrides
        items: List[ParameterDefinition] = []
        categories = set()
        for entry in schema_data:
            identifier = entry["id"]
            value = overrides.get(identifier, entry.get("default"))
            override_value = overrides.get(identifier)
            item = ParameterDefinition(
                identifier=identifier,
                name=entry.get("name", identifier),
                label=entry.get("label", entry.get("name", identifier)),
                type=entry.get("type", "number"),
                default=entry.get("default"),
                value=value,
                unit=entry.get("unit", ""),
                category=entry.get("category", ""),
                advanced=bool(entry.get("advanced", False)),
                description=entry.get("description", ""),
                minimum=entry.get("min"),
                maximum=entry.get("max"),
                step=entry.get("step"),
                choices=entry.get("choices", []),
                source=entry.get("source"),
                override=override_value if override_value is not None and override_value != entry.get("default") else None,
            )
            if not item.category:
                item.category = "Uncategorised"
            if item.override is not None:
                item.value = item.override
            categories.add(item.category)
            self._id_to_name[item.identifier] = item.name
            items.append(item)
        self._model.set_items(items)
        self._filtered_model.invalidateFilter()
        self._diff_model.invalidateFilter()
        self._categories = sorted(categories)
        self.schemaLoaded.emit()
        self.categoriesChanged.emit()
        self.presetsChanged.emit()
        self._processor.configure(
            id_to_name=self._id_to_name,
            chemistry=self._scenario.chemistry,
            model=self._scenario.model,
            preset=self._current_preset,
        )
        self._processor.schedule(overrides)

    def _on_value_changed(self, identifier: str, item: ParameterDefinition) -> None:
        override_value = item.override
        self._scenario.set_override(identifier, override_value)
        overrides = self._scenario.overrides
        self._processor.schedule(overrides)
        self.overridesChanged.emit()

    @QtCore.Property(QtCore.QObject, constant=True)
    def model(self) -> QtCore.QObject:
        return self._filtered_model

    @QtCore.Property(QtCore.QObject, constant=True)
    def diffModel(self) -> QtCore.QObject:
        return self._diff_model

    @QtCore.Property(list, notify=categoriesChanged)
    def categories(self) -> List[str]:
        return ["All"] + self._categories

    @QtCore.Property(list, notify=presetsChanged)
    def presets(self) -> List[Dict[str, Any]]:
        return self._presets

    @QtCore.Property(str, notify=presetsChanged)
    def currentPreset(self) -> str:
        return self._current_preset

    @QtCore.Property(int, notify=overridesChanged)
    def dirtyCount(self) -> int:
        return sum(1 for item in self._model.items() if item.override is not None)


__all__ = [
    "ParameterBridge",
    "ParameterDefinition",
    "ParameterFilterModel",
    "ParameterListModel",
    "PyBammProcessor",
    "ScenarioStore",
]
