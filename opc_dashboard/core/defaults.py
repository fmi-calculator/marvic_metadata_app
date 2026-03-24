"""Create blank OPC records and default sub-structures."""

import datetime
from core.schema import load_schema
from core.enums import UNCERTAINTY_SOURCES

_SCHEMA_VERSION = "1.0.0"

_BLANK_CRITERION = {
    "status": "unclear",
    "short_justification": "",
    "priority_for_improvement": "medium",
    "evidence_notes": "",
}


def default_crcf() -> dict:
    """Return a blank CRCF flat object matching the new schema structure."""
    return {
        "assessment_unit": "OPC",
        "applies_to_model_name": "",
        "eligibility_pathway": {
            "national_inventory_model": False,
            "commission_compliant_model": False,
        },
        "model_compliance_criteria": {
            "transparency_traceability": dict(_BLANK_CRITERION),
            "scientific_credibility": dict(_BLANK_CRITERION),
            "suitability": dict(_BLANK_CRITERION),
            "minimum_accuracy": {
                **_BLANK_CRITERION,
                "bias": False,
                "pi": False,
                "r2": False,
            },
        },
        "verification_profile": {
            "practice_verification_evidence": [],
            "outcome_verification_evidence": [],
            "field_visits_required": "",
        },
    }


def empty_uncertainty_sources() -> dict:
    return {
        src: {"considered": False, "propagated": False, "method": ""}
        for src in UNCERTAINTY_SOURCES
    }


def new_opc_record(opc_id: str, created_by: str, notes: str = "") -> dict:
    return {
        "record_metadata": {
            "schema_version": _SCHEMA_VERSION,
            "opc_id": opc_id,
            "created_by": created_by,
            "last_updated": datetime.date.today().isoformat(),
            "notes": notes,
        },
        "factsheet": {
            "opc_name": "",
            "opc_fullname": "",
            "lead_institutions": [],
            "main_modelling_approach": "",
            "target_lusts": [],
            "geographic_focus": [],
            "ghgs_covered": [],
            "crop_types_supported": [],
            "cf_practices_covered": [],
            "reporting_scale": [],
            "update_frequency": "",
            "user_orientation": [],
            "operational_maturity": "",
            "openness_level": "",
            "validation_status": "",
            "validation_status_notes": "",
            "runtime_environment": {
                "execution_targets": [],
                "containerised": False,
                "container_tech": [],
                "requires_parallelisation": False,
                "minimum_compute_notes": "",
            },
            "automation_profile": {
                "data_ingestion": "",
                "preprocessing": "",
                "model_execution": "",
                "qa_qc": "",
                "report_generation": "",
            },
            "interoperability": {
                "input_interfaces": [],
                "output_formats": [],
                "integrates_with_fmis": False,
                "integrates_with_lpis": False,
                "integrates_with_lab_data": False,
                "integrates_with_eo_pipeline": False,
                "machine_readable_io_schema": False,
            },
            "input_dependency_profile": {
                "requires_field_management_data": False,
                "requires_soil_sampling": False,
                "requires_lab_analysis": False,
                "requires_optical_eo": False,
                "requires_sar_eo": False,
                "requires_weather_data": False,
                "most_critical_bottleneck": "",
            },
        },
        "models": [],
        "uncertainty_propagation": {
            "initial_conditions": {
                "count": None,
                "data_driven": False,
                "top_inputs": [],
                "propagated": False,
                "propagation_method": "",
            },
            "drivers": {
                "count": None,
                "data_driven": False,
                "top_inputs": [],
                "propagated": False,
                "propagation_method": "",
            },
            "parameters": {
                "count": None,
                "data_driven": False,
                "top_inputs": [],
                "propagated": False,
                "propagation_method": "",
            },
            "management": {
                "count": None,
                "data_driven": False,
                "top_inputs": [],
                "propagated": False,
                "propagation_method": "",
            },
            "process_error": {
                "count": None,
                "data_driven": False,
                "top_inputs": [],
                "propagated": False,
                "propagation_method": "",
            },
            "random_effects": {
                "count": None,
                "data_driven": False,
                "top_inputs": [],
                "propagated": False,
                "propagation_method": "",
            },
            "project_scale": False,
        },
        "validation_evidence_overview": [],
        "crcf_model_readiness_matrix": default_crcf(),
    }
