from __future__ import annotations

from pathlib import Path
from typing import Any

from .erp_adapter import AdapterResult, build_finance_lines
from .reconciliation import reconcile_normalized_lines


def reconcile_adapter_result(adapter_result: AdapterResult) -> dict[str, Any]:
    """Pass adapter output through reconciliation without posting or persistence."""
    return {
        "adapter": adapter_result.report,
        "reconciliation": reconcile_normalized_lines(adapter_result.lines),
    }


def run_live_read_only_reconciliation(
    env_path: str | Path | None = None,
) -> dict[str, Any]:
    """Read PostgreSQL through the adapter and reconcile normalized lines only."""
    kwargs = {} if env_path is None else {"env_path": env_path}
    return reconcile_adapter_result(build_finance_lines(**kwargs))
