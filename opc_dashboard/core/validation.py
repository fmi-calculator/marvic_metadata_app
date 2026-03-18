"""Schema validation and business-rule checks."""
import jsonschema
from core.schema import load_schema

_SCHEMA = load_schema()


def validate_schema(record: dict) -> list[str]:
    """Return a list of JSON Schema validation error messages (empty = valid)."""
    validator = jsonschema.Draft202012Validator(_SCHEMA)
    errors = sorted(validator.iter_errors(record), key=lambda e: list(e.path))
    return [f"{' > '.join(str(p) for p in e.path) or 'root'}: {e.message}" for e in errors]


def validate_business_rules(record: dict) -> list[str]:
    """Return a list of non-blocking business-rule warning messages."""
    warnings: list[str] = []
    fs = record.get("factsheet", {})
    models = record.get("models", [])
    val_ev = record.get("validation_evidence_overview", [])
    crcf = record.get("crcf_model_readiness_matrix", {})

    approach = fs.get("main_modelling_approach", "")
    if approach == "hybrid" and len(models) < 2:
        warnings.append(
            "main_modelling_approach is 'hybrid' but fewer than 2 model rows exist."
        )

    if fs.get("validation_status") == "independently_validated" and not val_ev:
        warnings.append(
            "validation_status is 'independently_validated' but no validation evidence rows exist."
        )

    # crcf_model_readiness_matrix is a flat dict (not an array)
    model_names = {m.get("model_name", "") for m in models}
    crcf_unit = crcf.get("assessment_unit", "")
    crcf_model_ref = crcf.get("applies_to_model_name", "")

    if crcf_unit == "model_component" and not crcf_model_ref:
        warnings.append(
            "CRCF assessment_unit is 'model_component' but applies_to_model_name is empty."
        )

    if crcf_model_ref and crcf_model_ref not in model_names:
        warnings.append(
            f"CRCF applies_to_model_name '{crcf_model_ref}' does not match any model in the models list."
        )

    return warnings
