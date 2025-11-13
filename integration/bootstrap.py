# ini buat ngeload dependencies dari submodul
from __future__ import annotations

import sys
from contextlib import contextmanager
from dataclasses import dataclass
from importlib import import_module
from importlib.machinery import ModuleSpec
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from types import ModuleType
from typing import Any, Callable

ROOT = Path(__file__).resolve().parent.parent
SUBMODULE_PATHS = [
    ROOT / "Query-Processor",
    ROOT / "Query-Optimizer",
    ROOT / "Storage-Manager",
    ROOT / "Concurrency-Control-Manager",
    ROOT / "Failure-Recovery-Manager",
]


def ensure_sys_path() -> None:
    for candidate in reversed(SUBMODULE_PATHS):
        if candidate.exists():
            path_str = str(candidate)
            if path_str not in sys.path:
                sys.path.insert(0, path_str)


def _load_module(fullname: str, filepath: Path) -> ModuleType:
    spec = spec_from_file_location(fullname, filepath)
    if spec is None or spec.loader is None:
        raise ImportError(f"Failed to load module {fullname} from {filepath}")
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    sys.modules[fullname] = module
    return module


@contextmanager
def _bind_top_level_pkg(name: str, path: Path):
    previous = sys.modules.get(name)
    package = ModuleType(name)
    package.__spec__ = ModuleSpec(name, loader=None, is_package=True)
    package.__path__ = [str(path)]
    sys.modules[name] = package
    try:
        yield
    finally:
        if previous is None:
            sys.modules.pop(name, None)
        else:
            sys.modules[name] = previous


@dataclass(frozen=True)
class Dependencies:
    query_processor_cls: Any
    rows_cls: Any
    execution_result_cls: Any
    query_type_enum: Any
    query_type_resolver: Callable[[str], Any]
    concurrency_control_cls: Any
    failure_recovery_factory: Callable[[], Any]


def load_dependencies() -> Dependencies:
    ensure_sys_path()

    QueryProcessor = import_module("query_processor.QueryProcessor").QueryProcessor
    query_utils = import_module("query_processor.helper.query_utils")
    QueryType = query_utils.QueryType
    get_query_type = query_utils.get_query_type
    ExecutionResult = import_module("query_processor.model.ExecutionResult").ExecutionResult
    Rows = import_module("query_processor.model.Rows").Rows

    ccm_root = ROOT / "Concurrency-Control-Manager"
    with _bind_top_level_pkg("model", ccm_root / "model"):
        ccm_module = _load_module("ConcurrencyControlManager", ccm_root / "ConcurrencyControlManager.py")
    ConcurrencyControlManager = getattr(ccm_module, "ConcurrencyControlManager")

    frm_root = ROOT / "Failure-Recovery-Manager"
    with _bind_top_level_pkg("model", frm_root / "model"), _bind_top_level_pkg("helper", frm_root / "helper"):
        failure_module = _load_module("FailureRecovery", frm_root / "FailureRecovery.py")
    get_failure_recovery_manager = getattr(failure_module, "getFailureRecoveryManager")

    return Dependencies(
        query_processor_cls=QueryProcessor,
        rows_cls=Rows,
        execution_result_cls=ExecutionResult,
        query_type_enum=QueryType,
        query_type_resolver=get_query_type,
        concurrency_control_cls=ConcurrencyControlManager,
        failure_recovery_factory=get_failure_recovery_manager,
    )
