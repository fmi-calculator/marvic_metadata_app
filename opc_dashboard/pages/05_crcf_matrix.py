"""Page 5 — CRCF Model Readiness Matrix (opc_crcf_model_readiness_matrix.csv)."""

import sys
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

import streamlit as st

from core import state as _s
from core import storage
from core.enums import (
    CRCF_STATUS_OPTIONS,
    CRCF_PRIORITY_OPTIONS,
    PRACTICE_EVIDENCE_OPTIONS,
    OUTCOME_EVIDENCE_OPTIONS,
    FIELD_VISITS_OPTIONS,
)

_s.ensure_session_state()
st.title("CRCF Readiness")

if not _s.is_loaded():
    st.warning("No OPC record loaded. Return to the Home page to load or create one.")
    st.stop()

rec = _s.get_record()
st.caption(f"Editing: **{rec['record_metadata']['opc_id']}**")

# ── Load saved state ──────────────────────────────────────────────────────────
saved = rec.get("crcf_model_readiness_matrix", {})
if not isinstance(saved, dict):
    saved = {}

ep = saved.get("eligibility_pathway", {})
mcc = saved.get("model_compliance_criteria", {})

_CRITERIA = [
    ("transparency_traceability", "Transparency and traceability"),
    ("scientific_credibility", "Scientific credibility"),
    ("suitability", "Suitability"),
    ("minimum_accuracy", "Minimum accuracy"),
]


def _saved_criterion(code: str) -> dict:
    return mcc.get(
        code,
        {
            "status": "unclear",
            "short_justification": "",
            "priority_for_improvement": "medium",
            "evidence_notes": "",
        },
    )


def _safe_index(opts: list, val, default: int = 0) -> int:
    try:
        return opts.index(val)
    except ValueError:
        return default


model_name_opts = [""] + [
    m.get("model_name", "") for m in rec.get("models", []) if m.get("model_name")
]

# ── Assessment level ──────────────────────────────────────────────────────────
saved_unit = saved.get("assessment_unit", "OPC")
assessment_unit = st.radio(
    "**Assessment level**",
    options=["OPC", "model_component"],
    format_func=lambda x: "OPC" if x == "OPC" else "Model component",
    captions=[
        "if whole OPC is assessed for CRCF readiness",
        "if the following criteria is assessed for a particular model component",
    ],
    index=0 if saved_unit == "OPC" else 1,
    horizontal=True,
)

applies_to_model_name = ""
if assessment_unit == "model_component":
    saved_model = saved.get("applies_to_model_name", "")
    applies_to_model_name = st.selectbox(
        "Which model component?",
        options=model_name_opts,
        index=_safe_index(model_name_opts, saved_model),
    )

st.divider()

# ── Eligibility pathway ───────────────────────────────────────────────────────
st.subheader("Eligibility pathway")
st.caption("Select all that apply — these options are not mutually exclusive.")

ni_model = st.checkbox(
    "National GHG inventory model",
    value=ep.get("national_inventory_model", False),
)
cc_model = st.checkbox(
    "Commission-compliant model",
    value=ep.get("commission_compliant_model", False),
)

st.divider()

# ── Model compliance criteria ─────────────────────────────────────────────────
st.subheader("Model compliance criteria")

disabled = not cc_model
if disabled:
    st.caption(
        "Fields below are active only when **Commission-compliant model** is selected above."
    )

criteria_values: dict = {}
for code, label in _CRITERIA:
    r = _saved_criterion(code)
    st.markdown(f"**{label}**")

    col1, col2 = st.columns(2)
    with col1:
        status = st.selectbox(
            "Status",
            options=CRCF_STATUS_OPTIONS,
            index=_safe_index(CRCF_STATUS_OPTIONS, r.get("status", "unclear")),
            key=f"crcf_status_{code}",
            disabled=disabled,
        )
    with col2:
        priority = st.selectbox(
            "Priority for improvement",
            options=CRCF_PRIORITY_OPTIONS,
            index=_safe_index(
                CRCF_PRIORITY_OPTIONS, r.get("priority_for_improvement", "medium")
            ),
            key=f"crcf_priority_{code}",
            disabled=disabled,
        )

    short_justification = st.text_input(
        "Short justification",
        value=r.get("short_justification", ""),
        placeholder="One-sentence rationale for the status assigned.",
        key=f"crcf_just_{code}",
        disabled=disabled,
    )
    evidence_notes = st.text_area(
        "Evidence notes (optional)",
        value=r.get("evidence_notes", ""),
        height=70,
        placeholder="References, links, or additional context.",
        key=f"crcf_evnotes_{code}",
        disabled=disabled,
    )

    bias_val = pi_val = r2_val = False
    if code == "minimum_accuracy":
        st.markdown("*Minimum accuracy thresholds met:*")
        mc1, mc2, mc3 = st.columns(3)
        with mc1:
            bias_val = st.checkbox(
                "bias ≤ PMU",
                value=r.get("bias", False),
                key="crcf_bias",
                disabled=disabled,
            )
        with mc2:
            pi_val = st.checkbox(
                "≥ 90 % PI coverage",
                value=r.get("pi", False),
                key="crcf_pi",
                disabled=disabled,
            )
        with mc3:
            r2_val = st.checkbox(
                "R² > 0",
                value=r.get("r2", False),
                key="crcf_r2",
                disabled=disabled,
            )

    criteria_values[code] = {
        "status": status,
        "short_justification": short_justification.strip(),
        "priority_for_improvement": priority,
        "evidence_notes": evidence_notes.strip(),
        "bias": bias_val,
        "pi": pi_val,
        "r2": r2_val,
    }

    st.divider()

# ── Verification profile ──────────────────────────────────────────────────────
st.subheader("Verification profile")
st.caption(
    "Describe what evidence types can support practice and outcome verification, "
    "and whether field visits are required as part of the verification process."
)
vp = saved.get("verification_profile", {})

practice_evidence = st.multiselect(
    "Practice verification evidence (select all that apply)",
    options=PRACTICE_EVIDENCE_OPTIONS,
    default=[
        v
        for v in vp.get("practice_verification_evidence", [])
        if v in PRACTICE_EVIDENCE_OPTIONS
    ],
    help="Evidence types that can verify that the claimed management practices actually took place.",
)
outcome_evidence = st.multiselect(
    "Outcome verification evidence (select all that apply)",
    options=OUTCOME_EVIDENCE_OPTIONS,
    default=[
        v
        for v in vp.get("outcome_verification_evidence", [])
        if v in OUTCOME_EVIDENCE_OPTIONS
    ],
    help="Evidence types that can verify the modelled carbon / GHG outcome.",
)

_FV_OPTS = [""] + FIELD_VISITS_OPTIONS
_fv_saved = vp.get("field_visits_required", "")
field_visits_required = st.selectbox(
    "Field visits required?",
    options=_FV_OPTS,
    index=_FV_OPTS.index(_fv_saved) if _fv_saved in _FV_OPTS else 0,
    help="How often are physical field visits required to complete verification?",
)

# ── Save ──────────────────────────────────────────────────────────────────────
if st.button("Save", use_container_width=True):
    new_crcf = {
        "assessment_unit": assessment_unit,
        "applies_to_model_name": applies_to_model_name,
        "eligibility_pathway": {
            "national_inventory_model": ni_model,
            "commission_compliant_model": cc_model,
        },
        "model_compliance_criteria": criteria_values,
        "verification_profile": {
            "practice_verification_evidence": practice_evidence,
            "outcome_verification_evidence": outcome_evidence,
            "field_visits_required": field_visits_required,
        },
    }
    rec["crcf_model_readiness_matrix"] = new_crcf
    _s.set_record(rec)
    storage.save_opc(rec)
    st.success("Saved.")
