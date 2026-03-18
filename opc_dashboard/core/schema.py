"""Load master_OPC_schema.json from disk.

Search order:
  1. <app_root>/data/master_OPC_schema.json
  2. <workspace_root>/master_OPC_schema.json  (one level above app_root)
"""
import json
import pathlib

_app_root = pathlib.Path(__file__).parent.parent  # opc_dashboard/

_candidates = [
    _app_root / "data" / "master_OPC_schema.json",
    _app_root.parent / "master_OPC_schema.json",
]

SCHEMA_PATH: pathlib.Path | None = None
for _p in _candidates:
    if _p.exists():
        SCHEMA_PATH = _p
        break

if SCHEMA_PATH is None:
    raise FileNotFoundError(
        "master_OPC_schema.json not found. "
        f"Searched: {[str(p) for p in _candidates]}"
    )


def load_schema() -> dict:
    with open(SCHEMA_PATH, encoding="utf-8") as f:
        return json.load(f)
