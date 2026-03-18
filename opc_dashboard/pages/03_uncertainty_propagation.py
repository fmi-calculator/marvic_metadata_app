"""Page 3 — Uncertainty Propagation (opc_uncertainty_propagation.csv)."""
import sys
import pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

import streamlit as st

from core import state as _s
from core import storage

_s.ensure_session_state()
st.title("Uncertainty Propagation")

if not _s.is_loaded():
    st.warning("No OPC record loaded. Return to the Home page to load or create one.")
    st.stop()

rec = _s.get_record()
st.caption(f"Editing: **{rec['record_metadata']['opc_id']}**")
st.markdown(
    "For each of the six standard uncertainty sources, indicate whether its uncertainty "
    "is propagated through the modelling chain and describe the method used. "
    "Finally, indicate whether uncertainty is calculated at the project scale."
)

# ── Six named sources with display labels ─────────────────────────────────────
_SOURCES = [
    ("initial_conditions", "1. Initial conditions"),
    ("drivers",            "2. Drivers"),
    ("parameters",         "3. Parameters"),
    ("management",         "4. Management"),
    ("process_error",      "5. Process error"),
    ("random_effects",     "6. Random effects"),
]

_YES_NO = ["Yes", "No"]

def _bool_to_yn(v: bool) -> str:
    return "Yes" if v else "No"

def _yn_to_bool(s: str) -> bool:
    return s == "Yes"

# Load current values (fall back to conservative defaults)
unc: dict = rec.get("uncertainty_propagation", {})
if not isinstance(unc, dict):
    unc = {}

def _src_default(key: str) -> dict:
    return unc.get(key, {"propagated": False, "propagation_method": ""})

# ── Single form ───────────────────────────────────────────────────────────────
with st.form("unc_form"):
    source_values: dict = {}

    for key, label in _SOURCES:
        s = _src_default(key)
        st.markdown(f"**{label}**")
        col_r, col_m = st.columns([1, 3])
        with col_r:
            yn = st.radio(
                "Propagated?",
                _YES_NO,
                index=0 if s.get("propagated", False) else 1,
                horizontal=True,
                key=f"yn_{key}",
            )
        with col_m:
            method = st.text_input(
                "Propagation method",
                value=s.get("propagation_method", ""),
                placeholder="e.g. Monte Carlo",
                key=f"mt_{key}",
            )
        source_values[key] = {"yn": yn, "method": method}
        st.divider()

    st.markdown("**Project scale**")
    project_scale_yn = st.radio(
        "Is uncertainty calculated at the project scale?",
        _YES_NO,
        index=0 if unc.get("project_scale", False) else 1,
        horizontal=True,
        key="yn_project_scale",
    )

    submitted = st.form_submit_button("Save", use_container_width=True)

# ── On save ───────────────────────────────────────────────────────────────────
if submitted:
    new_unc: dict = {}
    for key, _ in _SOURCES:
        v = source_values[key]
        new_unc[key] = {
            "propagated":          _yn_to_bool(v["yn"]),
            "propagation_method":  v["method"].strip(),
        }
    new_unc["project_scale"] = _yn_to_bool(project_scale_yn)

    rec["uncertainty_propagation"] = new_unc
    _s.set_record(rec)
    storage.save_opc(rec)
    st.success("Saved.")
