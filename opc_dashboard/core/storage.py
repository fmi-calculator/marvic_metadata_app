"""Atomic JSON load/save for OPC records."""
import datetime
import json
import os
import pathlib

_app_root = pathlib.Path(__file__).parent.parent
RECORDS_DIR = _app_root / "data" / "opc_records"
EXPORTS_DIR = _app_root / "data" / "exports"

# Ensure directories exist
RECORDS_DIR.mkdir(parents=True, exist_ok=True)
EXPORTS_DIR.mkdir(parents=True, exist_ok=True)


def list_opcs() -> list[str]:
    """Return sorted list of opc_id values found in RECORDS_DIR."""
    return sorted(
        p.stem for p in RECORDS_DIR.glob("*.json") if not p.stem.endswith(".tmp")
    )


def load_opc(opc_id: str) -> dict:
    path = RECORDS_DIR / f"{opc_id}.json"
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save_opc(record: dict) -> None:
    """Write record atomically and auto-stamp last_updated."""
    record["record_metadata"]["last_updated"] = datetime.date.today().isoformat()
    opc_id = record["record_metadata"]["opc_id"]
    target = RECORDS_DIR / f"{opc_id}.json"
    tmp = target.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(record, indent=2, ensure_ascii=False), encoding="utf-8")
    os.replace(tmp, target)


def record_exists(opc_id: str) -> bool:
    return (RECORDS_DIR / f"{opc_id}.json").exists()
