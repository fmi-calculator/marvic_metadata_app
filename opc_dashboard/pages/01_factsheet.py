"""Page 1 — Factsheet (opc_factsheet.csv)."""
import sys
import pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

import streamlit as st

from core import state as _s
from core import storage
from core.enums import (
    MODELLING_APPROACH_OPTIONS,
    GHG_OPTIONS,
    CF_PRACTICES_OPTIONS,
    SCALE_OPTIONS,
    UPDATE_FREQUENCY_OPTIONS,
    USER_ORIENTATION_OPTIONS,
    OPERATIONAL_MATURITY_OPTIONS,
    OPENNESS_LEVEL_OPTIONS,
    VALIDATION_STATUS_OPTIONS,
)

_s.ensure_session_state()
st.title("Factsheet")

if not _s.is_loaded():
    st.warning("No OPC record loaded. Return to the Home page to load or create one.")
    st.stop()

rec = _s.get_record()
fs  = rec["factsheet"]

st.caption(f"Editing: **{rec['record_metadata']['opc_id']}**")

# ── Form ──────────────────────────────────────────────────────────────────────

with st.form("factsheet_form"):

    opc_name = st.text_input("OPC name / acronym *", value=fs.get("opc_name", ""),
        help="Short identifier or acronym, e.g. ACEO")

    opc_fullname = st.text_input("OPC full name (optional)", value=fs.get("opc_fullname", ""),
        help="Full descriptive name, e.g. AgriCarbon Processing Chain with Earth Observation")

    lead_raw = st.text_area(
        "Lead institutions * (one per line)",
        value="\n".join(fs.get("lead_institutions", [])),
        height=100,
    )

    main_approach = st.selectbox(
        "Main modelling approach * (select best that applies)",
        options=[""] + MODELLING_APPROACH_OPTIONS,
        index=(0 if not fs.get("main_modelling_approach")
               else ([""] + MODELLING_APPROACH_OPTIONS).index(fs["main_modelling_approach"])),
        help="Soil-centered: mechanistic soil carbon model is the core of the OPC. Hybrid: soil carbon model is combined with data-driven components (e.g. machine learning). Ecosystem-based: A mechanistic full agro-ecosystem (soil-crop) model.",
    )

    target_raw = st.text_area(
        "Target LUST (one per line)",
        value="\n".join(fs.get("target_lusts", [])),
        height=80,
        help="Land-use and tenure systems targeted by this OPC.",
    )

    geo_raw = st.text_area(
        "Geographic focus (one per line)",
        value="\n".join(fs.get("geographic_focus", [])),
        height=80,
    )

    ghgs = st.multiselect(
        "GHGs covered (select all that apply)",
        options=GHG_OPTIONS,
        default=[g for g in fs.get("ghgs_covered", []) if g in GHG_OPTIONS],
    )

    cf_practices = st.multiselect(
        "CF practices covered (select all that apply)",
        options=CF_PRACTICES_OPTIONS,
        default=[p for p in fs.get("cf_practices_covered", []) if p in CF_PRACTICES_OPTIONS],
    )

    scales = st.multiselect(
        "Reporting scale (select all that apply)",
        options=SCALE_OPTIONS,
        default=[s for s in fs.get("reporting_scale", []) if s in SCALE_OPTIONS],
    )

    update_freq = st.selectbox(
        "Update frequency (if multiple, select the most frequent one)",
        options=[""] + UPDATE_FREQUENCY_OPTIONS,
        index=(0 if not fs.get("update_frequency")
               else ([""] + UPDATE_FREQUENCY_OPTIONS).index(fs["update_frequency"])),
    )

    user_orient = st.multiselect(
        "User orientation (select all that apply)",
        options=USER_ORIENTATION_OPTIONS,
        default=[u for u in fs.get("user_orientation", []) if u in USER_ORIENTATION_OPTIONS],
    )

    op_maturity = st.selectbox(
        "Operational maturity",
        options=[""] + OPERATIONAL_MATURITY_OPTIONS,
        index=(0 if not fs.get("operational_maturity")
               else ([""] + OPERATIONAL_MATURITY_OPTIONS).index(fs["operational_maturity"])),
    )

    openness = st.selectbox(
        "Openness level",
        options=[""] + OPENNESS_LEVEL_OPTIONS,
        index=(0 if not fs.get("openness_level")
               else ([""] + OPENNESS_LEVEL_OPTIONS).index(fs["openness_level"])),
    )

    val_status = st.selectbox(
        "Validation status (select best that applies)",
        options=[""] + VALIDATION_STATUS_OPTIONS,
        index=(0 if not fs.get("validation_status")
               else ([""] + VALIDATION_STATUS_OPTIONS).index(fs["validation_status"])),
    )

    val_notes = st.text_area(
        "Validation status notes",
        value=fs.get("validation_status_notes", ""),
        height=80,
    )

    submitted = st.form_submit_button("Save")

# ── On save ───────────────────────────────────────────────────────────────────

if submitted:
    rec["factsheet"].update({
        "opc_name":                opc_name.strip(),
        "opc_fullname":            opc_fullname.strip(),
        "lead_institutions":       [l.strip() for l in lead_raw.splitlines() if l.strip()],
        "main_modelling_approach": main_approach,
        "target_lusts":            [l.strip() for l in target_raw.splitlines() if l.strip()],
        "geographic_focus":        [l.strip() for l in geo_raw.splitlines() if l.strip()],
        "ghgs_covered":            ghgs,
        "cf_practices_covered":    cf_practices,
        "reporting_scale":         scales,
        "update_frequency":        update_freq,
        "user_orientation":        user_orient,
        "operational_maturity":    op_maturity,
        "openness_level":          openness,
        "validation_status":       val_status,
        "validation_status_notes": val_notes.strip(),
    })
    _s.set_record(rec)
    storage.save_opc(rec)
    st.success("Saved.")
