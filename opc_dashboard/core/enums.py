"""Controlled vocabularies derived from the JSON schema.

All lists are read once at import time so they stay in sync with the schema.
"""

from core.schema import load_schema

_schema = load_schema()
_f = _schema["properties"]["factsheet"]["properties"]
_m = _schema["properties"]["models"]["items"]["properties"]
_c = _schema["$defs"]["crcfCriterionDetail"]["properties"]

MODELLING_APPROACH_OPTIONS: list[str] = _f["main_modelling_approach"]["enum"]
GHG_OPTIONS: list[str] = _f["ghgs_covered"]["items"]["enum"]
CF_PRACTICES_OPTIONS: list[str] = _f["cf_practices_covered"]["items"]["enum"]
SCALE_OPTIONS: list[str] = _schema["$defs"]["scaleEnum"]["enum"]
UPDATE_FREQUENCY_OPTIONS: list[str] = _f["update_frequency"]["enum"]
USER_ORIENTATION_OPTIONS: list[str] = _f["user_orientation"]["items"]["enum"]
OPERATIONAL_MATURITY_OPTIONS: list[str] = _f["operational_maturity"]["enum"]
OPENNESS_LEVEL_OPTIONS: list[str] = _f["openness_level"]["enum"]
VALIDATION_STATUS_OPTIONS: list[str] = _f["validation_status"]["enum"]

MODEL_ROLE_OPTIONS: list[str] = _m["model_role"]["enum"]

_re = _f["runtime_environment"]["properties"]
EXECUTION_TARGET_OPTIONS: list[str] = _re["execution_targets"]["items"]["enum"]
CONTAINER_TECH_OPTIONS: list[str] = _re["container_tech"]["items"]["enum"]

_ap = _f["automation_profile"]["properties"]
AUTOMATION_LEVEL_OPTIONS: list[str] = _ap["data_ingestion"]["enum"]

_io = _f["interoperability"]["properties"]
INPUT_INTERFACE_OPTIONS: list[str] = _io["input_interfaces"]["items"]["enum"]
OUTPUT_FORMAT_OPTIONS: list[str] = _io["output_formats"]["items"]["enum"]

CRCF_STATUS_OPTIONS: list[str] = _c["status"]["enum"]
CRCF_PRIORITY_OPTIONS: list[str] = _c["priority_for_improvement"]["enum"]

UNCERTAINTY_SOURCES: list[str] = [
    "initial_conditions",
    "drivers",
    "parameters",
    "management",
    "process_error",
    "random_effects",
]
