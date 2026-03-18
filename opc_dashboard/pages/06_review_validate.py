"""Page 6 — Review & Validate (pseudocode / implementation blueprint).

This file is intentionally written as annotated pseudocode.
It is not executable but describes exactly what the page should do
so that a developer can implement it without ambiguity.

──────────────────────────────────────────────────────────────────
HIGH-LEVEL FLOW
──────────────────────────────────────────────────────────────────

    1. Guard: stop if no OPC is loaded in session state.
    2. Run schema validation  → list of blocking errors.
    3. Run business-rule checks → list of non-blocking warnings.
    4. Display a top-level status badge (pass / warning / fail).
    5. Display per-section completeness scores.
    6. Display schema errors (if any) in st.error blocks.
    7. Display business-rule warnings (if any) in st.warning blocks.
    8. Display the full record as formatted JSON in an expander.
"""

# ── PSEUDOCODE BEGINS ─────────────────────────────────────────────────────────

# IMPORT state, validation helpers
# import sys, pathlib
# sys.path.insert(0, ...)
# import streamlit as st
# from core import state as _s
# from core.validation import validate_schema, validate_business_rules

# ENSURE session state is initialised
# _s.ensure_session_state()

# SET page title
# st.title("Review & Validate")

# GUARD: if no OPC loaded, show warning and stop
# IF NOT _s.is_loaded():
#     st.warning("No OPC record loaded. Return to the Home page to load or create one.")
#     st.stop()

# LOAD current record from session state
# rec = _s.get_record()
# st.caption(f"Reviewing: **{rec['record_metadata']['opc_id']}**")

# ── 1. RUN VALIDATION ─────────────────────────────────────────────────────────

# schema_errors   = validate_schema(rec)          # list[str], blocking
# rule_warnings   = validate_business_rules(rec)  # list[str], non-blocking

# ── 2. TOP-LEVEL STATUS BADGE ─────────────────────────────────────────────────

# IF schema_errors is non-empty:
#     st.error(f"❌  Schema validation failed — {len(schema_errors)} error(s). "
#              "The record cannot be exported until all errors are resolved.")
# ELIF rule_warnings is non-empty:
#     st.warning(f"⚠️  Schema valid — {len(rule_warnings)} business-rule warning(s).")
# ELSE:
#     st.success("✅  Record is valid and ready for export.")

# ── 3. PER-SECTION COMPLETENESS SCORES ───────────────────────────────────────
#
# For each section, compute the fraction of required fields that are non-empty.
# Display as st.progress bars labelled with the section name and percentage.
#
# DEFINE function completeness(section_dict, required_keys) -> float:
#     filled = sum(1 for k in required_keys if section_dict.get(k))
#     RETURN filled / len(required_keys) if required_keys else 1.0
#
# REQUIRED KEYS per section (mirror master_OPC_schema.json "required" arrays):
#
#   factsheet_required = [
#       "opc_name", "lead_institutions", "main_modelling_approach",
#       "target_lusts", "geographic_focus", "ghgs_covered",
#       "reporting_scale", "update_frequency", "user_orientation",
#       "operational_maturity", "openness_level", "validation_status",
#   ]
#
#   models_required_per_item = ["model_name", "model_role", "scientific_publication_dois"]
#
#   uncertainty_sources = [
#       "initial_conditions", "drivers", "parameters",
#       "management", "process_error", "random_effects",
#   ]
#
#   crcf_criteria = [
#       "transparency_traceability", "scientific_credibility",
#       "suitability", "minimum_accuracy",
#   ]
#   crcf_criterion_fields = ["status", "short_justification", "priority_for_improvement"]
#
# st.subheader("Section completeness")
#
# factsheet_score = completeness(rec["factsheet"], factsheet_required)
# st.progress(factsheet_score, text=f"Factsheet — {factsheet_score:.0%}")
#
# IF rec["models"] is empty:
#     models_score = 0.0
# ELSE:
#     per_model_scores = [
#         completeness(m, models_required_per_item) for m in rec["models"]
#     ]
#     models_score = average(per_model_scores)
# st.progress(models_score, text=f"Models ({len(rec['models'])} component(s)) — {models_score:.0%}")
#
# unc = rec["uncertainty_propagation"]
# unc_score = average([
#     1.0 if unc[src]["propagated"] else 0.5   # propagated=False is a valid answer,
#     for src in uncertainty_sources            # so score 0.5 if method blank, 1.0 otherwise
# ])
# st.progress(unc_score, text=f"Uncertainty propagation — {unc_score:.0%}")
#
# val_ev = rec["validation_evidence_overview"]
# IF val_ev is empty:
#     val_score = 0.0
#     st.progress(val_score, text="Validation evidence — 0 % (no entries)")
# ELSE:
#     val_required = ["variable_validated", "dataset_type", "geography",
#                     "period", "validation_metrics", "summary_result", "remaining_gap"]
#     val_score = average([completeness(ev, val_required) for ev in val_ev])
#     st.progress(val_score, text=f"Validation evidence ({len(val_ev)} entries) — {val_score:.0%}")
#
# crcf_mcc = rec["crcf_model_readiness_matrix"].get("model_compliance_criteria", {})
# IF crcf_mcc is empty:
#     crcf_score = 0.0
# ELSE:
#     crcf_score = average([
#         completeness(crcf_mcc.get(code, {}), crcf_criterion_fields)
#         for code in crcf_criteria
#     ])
# st.progress(crcf_score, text=f"CRCF compliance criteria — {crcf_score:.0%}")

# ── 4. SCHEMA ERRORS ──────────────────────────────────────────────────────────

# IF schema_errors:
#     st.subheader("Schema errors (must fix before export)")
#     FOR error_msg IN schema_errors:
#         st.error(error_msg)

# ── 5. BUSINESS-RULE WARNINGS ─────────────────────────────────────────────────

# IF rule_warnings:
#     st.subheader("Business-rule warnings (non-blocking)")
#     FOR warning_msg IN rule_warnings:
#         st.warning(warning_msg)

# ── 6. FULL RECORD JSON VIEWER ────────────────────────────────────────────────

# WITH st.expander("Full record JSON", expanded=False):
#     st.json(rec)

# ── PSEUDOCODE ENDS ───────────────────────────────────────────────────────────
