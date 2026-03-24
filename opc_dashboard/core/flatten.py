"""Flatten master JSON records into rows for the five CSV tables."""

import csv
import pathlib
from core.enums import UNCERTAINTY_SOURCES

# ── helpers ──────────────────────────────────────────────────────────────────


def _join(lst: list) -> str:
    """Semicolon-join a list for CSV output."""
    return ";".join(str(v) for v in lst if v)


# ── per-section flatteners ────────────────────────────────────────────────────


def flatten_factsheet(record: dict) -> dict:
    fs = record["factsheet"]
    meta = record["record_metadata"]
    return {
        "opc_id": meta["opc_id"],
        "opc_name": fs.get("opc_name", ""),
        "opc_fullname": fs.get("opc_fullname", ""),
        "lead_institutions": _join(fs.get("lead_institutions", [])),
        "main_modelling_approach": fs.get("main_modelling_approach", ""),
        "target_lusts": _join(fs.get("target_lusts", [])),
        "geographic_focus": _join(fs.get("geographic_focus", [])),
        "ghgs_covered": _join(fs.get("ghgs_covered", [])),
        "cf_practices_covered": _join(fs.get("cf_practices_covered", [])),
        "reporting_scale": _join(fs.get("reporting_scale", [])),
        "update_frequency": fs.get("update_frequency", ""),
        "user_orientation": _join(fs.get("user_orientation", [])),
        "operational_maturity": fs.get("operational_maturity", ""),
        "openness_level": fs.get("openness_level", ""),
        "validation_status": fs.get("validation_status", ""),
        "validation_status_notes": fs.get("validation_status_notes", ""),
        "execution_targets": _join(
            fs.get("runtime_environment", {}).get("execution_targets", [])
        ),
        "containerised": fs.get("runtime_environment", {}).get("containerised", ""),
        "container_tech": _join(
            fs.get("runtime_environment", {}).get("container_tech", [])
        ),
        "requires_parallelisation": fs.get("runtime_environment", {}).get(
            "requires_parallelisation", ""
        ),
        "minimum_compute_notes": fs.get("runtime_environment", {}).get(
            "minimum_compute_notes", ""
        ),
        "auto_data_ingestion": fs.get("automation_profile", {}).get(
            "data_ingestion", ""
        ),
        "auto_preprocessing": fs.get("automation_profile", {}).get("preprocessing", ""),
        "auto_model_execution": fs.get("automation_profile", {}).get(
            "model_execution", ""
        ),
        "auto_qa_qc": fs.get("automation_profile", {}).get("qa_qc", ""),
        "auto_report_generation": fs.get("automation_profile", {}).get(
            "report_generation", ""
        ),
        "input_interfaces": _join(
            fs.get("interoperability", {}).get("input_interfaces", [])
        ),
        "output_formats": _join(
            fs.get("interoperability", {}).get("output_formats", [])
        ),
        "integrates_with_fmis": fs.get("interoperability", {}).get("integrates_with_fmis", ""),
        "integrates_with_lpis": fs.get("interoperability", {}).get("integrates_with_lpis", ""),
        "integrates_with_lab_data": fs.get("interoperability", {}).get("integrates_with_lab_data", ""),
        "integrates_with_eo_pipeline": fs.get("interoperability", {}).get("integrates_with_eo_pipeline", ""),
        "machine_readable_io_schema": fs.get("interoperability", {}).get("machine_readable_io_schema", ""),
        "schema_version": meta.get("schema_version", ""),
        "last_updated": meta.get("last_updated", ""),
    }


def flatten_models(record: dict) -> list[dict]:
    meta = record["record_metadata"]
    rows = []
    for i, m in enumerate(record.get("models", [])):
        rows.append(
            {
                "opc_id": meta["opc_id"],
                "opc_name": record["factsheet"].get("opc_name", ""),
                "row_index": i,
                "model_name": m.get("model_name", ""),
                "model_role": m.get("model_role", ""),
                "model_version": m.get("model_version", ""),
                "model_repository": m.get("model_repository", ""),
                "scientific_publication_dois": _join(
                    m.get("scientific_publication_dois", [])
                ),
                "model_notes": m.get("notes", ""),
            }
        )
    return rows


def flatten_uncertainty(record: dict) -> list[dict]:
    meta = record["record_metadata"]
    unc = record.get("uncertainty_propagation", {})
    if not isinstance(unc, dict):
        return []
    row: dict = {
        "opc_id": meta["opc_id"],
        "opc_name": record["factsheet"].get("opc_name", ""),
    }
    for src in UNCERTAINTY_SOURCES:
        s = unc.get(src, {})
        row[f"{src}_count"] = s.get("count", "")
        row[f"{src}_data_driven"] = s.get("data_driven", "")
        row[f"{src}_top_inputs"] = _join(s.get("top_inputs", []))
        row[f"{src}_propagated"] = s.get("propagated", False)
        row[f"{src}_method"] = s.get("propagation_method", "")
    row["project_scale"] = unc.get("project_scale", False)
    return [row]


def flatten_validation_evidence(record: dict) -> list[dict]:
    meta = record["record_metadata"]
    rows = []
    for i, ev in enumerate(record.get("validation_evidence_overview", [])):
        rows.append(
            {
                "opc_id": meta["opc_id"],
                "opc_name": record["factsheet"].get("opc_name", ""),
                "row_index": i,
                "variable_validated": ev.get("variable_validated", ""),
                "dataset_type": ev.get("dataset_type", ""),
                "geography": ev.get("geography", ""),
                "period": ev.get("period", ""),
                "validation_metrics": _join(ev.get("validation_metrics", [])),
                "summary_result": ev.get("summary_result", ""),
                "remaining_gap": ev.get("remaining_gap", ""),
            }
        )
    return rows


def flatten_crcf_matrix(record: dict) -> list[dict]:
    meta = record["record_metadata"]
    crcf = record.get("crcf_model_readiness_matrix", {})
    if not isinstance(crcf, dict):
        return []

    opc_id = meta["opc_id"]
    opc_name = record["factsheet"].get("opc_name", "")
    assessment_unit = crcf.get("assessment_unit", "")
    applies_to_model = crcf.get("applies_to_model_name", "")
    ep = crcf.get("eligibility_pathway", {})
    ni_model = ep.get("national_inventory_model", False)
    cc_model = ep.get("commission_compliant_model", False)
    mcc = crcf.get("model_compliance_criteria", {})

    _CRITERIA = [
        ("transparency_traceability", "Transparency and traceability"),
        ("scientific_credibility", "Scientific credibility"),
        ("suitability", "Suitability"),
        ("minimum_accuracy", "Minimum accuracy"),
    ]

    rows = []
    for code, label in _CRITERIA:
        cr = mcc.get(code, {})
        row = {
            "opc_id": opc_id,
            "opc_name": opc_name,
            "assessment_unit": assessment_unit,
            "applies_to_model_name": applies_to_model,
            "eligibility_national_inventory_model": ni_model,
            "eligibility_commission_compliant_model": cc_model,
            "criterion_code": code,
            "criterion_label": label,
            "status": cr.get("status", ""),
            "short_justification": cr.get("short_justification", ""),
            "priority_for_improvement": cr.get("priority_for_improvement", ""),
            "evidence_notes": cr.get("evidence_notes", ""),
            "min_accuracy_bias_lte_pmu": cr.get("bias", "")
            if code == "minimum_accuracy"
            else "",
            "min_accuracy_pi_90pct": cr.get("pi", "")
            if code == "minimum_accuracy"
            else "",
            "min_accuracy_r2_gt_0": cr.get("r2", "")
            if code == "minimum_accuracy"
            else "",
        }
        rows.append(row)
    return rows


# ── multi-record CSV export ───────────────────────────────────────────────────


def _write_csv(rows: list[dict], path: pathlib.Path) -> None:
    if not rows:
        return
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def export_all_csvs(records: list[dict], output_dir: pathlib.Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)

    _write_csv(
        [flatten_factsheet(r) for r in records],
        output_dir / "opc_factsheet.csv",
    )
    _write_csv(
        [row for r in records for row in flatten_models(r)],
        output_dir / "opc_models.csv",
    )
    _write_csv(
        [row for r in records for row in flatten_uncertainty(r)],
        output_dir / "opc_uncertainty_propagation.csv",
    )
    _write_csv(
        [row for r in records for row in flatten_validation_evidence(r)],
        output_dir / "opc_validation_evidence_overview.csv",
    )
    _write_csv(
        [row for r in records for row in flatten_crcf_matrix(r)],
        output_dir / "opc_crcf_model_readiness_matrix.csv",
    )
