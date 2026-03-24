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
    "For each of the six standard uncertainty sources, provide data-requirement details "
    "and indicate whether its uncertainty is propagated through the modelling chain. "
    "Finally, indicate whether uncertainty is calculated at the project scale."
)

# ── Six named sources with display labels and count-field help text ───────────
_SOURCES = [
    (
        "initial_conditions",
        "1. Initial conditions",
        "Number of state variables in the model (e.g. number of pools in a biogeochemical model).",
        "Most important initial condition inputs (e.g. soil organic carbon stock, bulk density).",
    ),
    (
        "drivers",
        "2. Drivers",
        "Number of different driver variables or covariates (e.g. climate inputs: temperature, precipitation, solar radiation).",
        "Most important driver inputs (e.g. daily temperature, precipitation, NDVI).",
    ),
    (
        "parameters",
        "3. Parameters",
        "Number of model parameters that must be set or estimated.",
        "Most important parameter inputs (e.g. decomposition rate constant, carbon-use efficiency).",
    ),
    (
        "management",
        "4. Management",
        "Number of distinct management activity types can be taken in / simulated by the OPC (count sub-inputs belonging to a major activity type as one, e.g. tillage date and tillage amount don't count separately but as one under 'tillage').",
        "Most important management activity types (e.g. tillage, fertiliser application, irrigation).",
    ),
    (
        "process_error",
        "5. Process error",
        "Number of process error terms explicitly represented in the OPC simulations or dimension of the error covariance matrix.",
        "Most important dynamic uncertainty in the process model (e.g. attributable to model misspecification [structural error] or stochasticity) not explained by any other uncertainty source.",
    ),
    (
        "random_effects",
        "6. Random effects",
        "Number of random effect terms in the OPC simulations (e.g. site-level or year-level random effects).",
        "Most important random effects (e.g. site-to-site, year-to-year).",
    ),
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
    return unc.get(
        key,
        {
            "count": None,
            "data_driven": False,
            "top_inputs": [],
            "propagated": False,
            "propagation_method": "",
        },
    )


# ── Single form ───────────────────────────────────────────────────────────────
with st.form("unc_form"):
    source_values: dict = {}

    for key, label, count_help, inputs_help in _SOURCES:
        s = _src_default(key)
        st.markdown(f"**{label}**")

        # ── Data requirements sub-section ──────────────────────────────────
        st.markdown("*Data requirements*")

        col_count, col_driven = st.columns([1, 1])
        with col_count:
            raw_count = s.get("count")
            count_val = st.number_input(
                "Number of inputs",
                min_value=0,
                step=1,
                value=int(raw_count) if raw_count is not None else 0,
                help=count_help,
                key=f"count_{key}",
            )
        with col_driven:
            driven_yn = st.radio(
                "Data driven?",
                _YES_NO,
                index=0 if s.get("data_driven", False) else 1,
                horizontal=True,
                help=(
                    "Select **Yes** if this source's inputs are derived from measured or "
                    "observational data (including data assimilation outcomes). Select **No** for spin-up values, hand-tuned "
                    "constants, scenario-derived values or theoretical defaults."
                ),
                key=f"driven_{key}",
            )

        existing_inputs = s.get("top_inputs", [])
        # Pad to 5 lines for display
        lines_display = "\n".join((existing_inputs + ["", "", "", "", ""])[:5])
        top_inputs_raw = st.text_area(
            "Up to 5 most important inputs (one per line)",
            value=lines_display,
            height=130,
            help=inputs_help,
            key=f"inputs_{key}",
        )

        # ── Propagation sub-section ────────────────────────────────────────
        st.markdown("*Uncertainty propagation*")
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

        source_values[key] = {
            "count": count_val,
            "driven": driven_yn,
            "top_inputs_raw": top_inputs_raw,
            "yn": yn,
            "method": method,
        }
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
    for key, *_ in _SOURCES:
        v = source_values[key]
        # Parse top_inputs: split on newlines, strip, drop blanks, cap at 5
        top_inputs = [
            line.strip() for line in v["top_inputs_raw"].splitlines() if line.strip()
        ][:5]
        new_unc[key] = {
            "count": int(v["count"]),
            "data_driven": _yn_to_bool(v["driven"]),
            "top_inputs": top_inputs,
            "propagated": _yn_to_bool(v["yn"]),
            "propagation_method": v["method"].strip(),
        }
    new_unc["project_scale"] = _yn_to_bool(project_scale_yn)

    rec["uncertainty_propagation"] = new_unc
    _s.set_record(rec)
    storage.save_opc(rec)
    st.success("Saved.")
