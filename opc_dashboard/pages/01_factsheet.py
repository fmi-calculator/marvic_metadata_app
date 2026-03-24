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
    CROP_TYPE_OPTIONS,
    CF_PRACTICES_OPTIONS,
    SCALE_OPTIONS,
    UPDATE_FREQUENCY_OPTIONS,
    USER_ORIENTATION_OPTIONS,
    OPERATIONAL_MATURITY_OPTIONS,
    OPENNESS_LEVEL_OPTIONS,
    VALIDATION_STATUS_OPTIONS,
    EXECUTION_TARGET_OPTIONS,
    CONTAINER_TECH_OPTIONS,
    AUTOMATION_LEVEL_OPTIONS,
    INPUT_INTERFACE_OPTIONS,
    OUTPUT_FORMAT_OPTIONS,
    BOTTLENECK_OPTIONS,
    BASELINE_TYPE_OPTIONS,
    BASELINE_AUDITABILITY_OPTIONS,
)

_s.ensure_session_state()
st.title("Factsheet")

if not _s.is_loaded():
    st.warning("No OPC record loaded. Return to the Home page to load or create one.")
    st.stop()

rec = _s.get_record()
fs = rec["factsheet"]

st.caption(f"Editing: **{rec['record_metadata']['opc_id']}**")

# ── Form ──────────────────────────────────────────────────────────────────────

with st.form("factsheet_form"):
    opc_name = st.text_input(
        "OPC name / acronym *",
        value=fs.get("opc_name", ""),
        help="Short identifier or acronym, e.g. ACEO",
    )

    opc_fullname = st.text_input(
        "OPC full name (optional)",
        value=fs.get("opc_fullname", ""),
        help="Full descriptive name, e.g. AgriCarbon Processing Chain with Earth Observation",
    )

    lead_raw = st.text_area(
        "Lead institutions * (one per line)",
        value="\n".join(fs.get("lead_institutions", [])),
        height=100,
    )

    main_approach = st.selectbox(
        "Main modelling approach * (select best that applies)",
        options=[""] + MODELLING_APPROACH_OPTIONS,
        index=(
            0
            if not fs.get("main_modelling_approach")
            else ([""] + MODELLING_APPROACH_OPTIONS).index(
                fs["main_modelling_approach"]
            )
        ),
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

    crop_types = st.multiselect(
        "Crop types supported (select all that apply)",
        options=CROP_TYPE_OPTIONS,
        default=[
            c for c in fs.get("crop_types_supported", []) if c in CROP_TYPE_OPTIONS
        ],
        help="Which crop or land-use types can this OPC simulate or be applied to?",
    )

    cf_practices = st.multiselect(
        "CF practices covered (select all that apply)",
        options=CF_PRACTICES_OPTIONS,
        default=[
            p for p in fs.get("cf_practices_covered", []) if p in CF_PRACTICES_OPTIONS
        ],
    )

    scales = st.multiselect(
        "Reporting scale (select all that apply)",
        options=SCALE_OPTIONS,
        default=[s for s in fs.get("reporting_scale", []) if s in SCALE_OPTIONS],
    )

    update_freq = st.selectbox(
        "Update frequency (if multiple, select the most frequent one)",
        options=[""] + UPDATE_FREQUENCY_OPTIONS,
        index=(
            0
            if not fs.get("update_frequency")
            else ([""] + UPDATE_FREQUENCY_OPTIONS).index(fs["update_frequency"])
        ),
    )

    user_orient = st.multiselect(
        "User orientation (select all that apply)",
        options=USER_ORIENTATION_OPTIONS,
        default=[
            u for u in fs.get("user_orientation", []) if u in USER_ORIENTATION_OPTIONS
        ],
    )

    op_maturity = st.selectbox(
        "Operational maturity",
        options=[""] + OPERATIONAL_MATURITY_OPTIONS,
        index=(
            0
            if not fs.get("operational_maturity")
            else ([""] + OPERATIONAL_MATURITY_OPTIONS).index(fs["operational_maturity"])
        ),
    )

    openness = st.selectbox(
        "Openness level",
        options=[""] + OPENNESS_LEVEL_OPTIONS,
        index=(
            0
            if not fs.get("openness_level")
            else ([""] + OPENNESS_LEVEL_OPTIONS).index(fs["openness_level"])
        ),
    )

    val_status = st.selectbox(
        "Validation status (select best that applies)",
        options=[""] + VALIDATION_STATUS_OPTIONS,
        index=(
            0
            if not fs.get("validation_status")
            else ([""] + VALIDATION_STATUS_OPTIONS).index(fs["validation_status"])
        ),
    )

    val_notes = st.text_area(
        "Validation status notes",
        value=fs.get("validation_status_notes", ""),
        height=80,
    )

    st.subheader("Baseline approach")
    st.caption("Describe how the baseline is defined and how auditable it is.")
    ba = fs.get("baseline_approach", {})

    _BT_OPTS = [""] + BASELINE_TYPE_OPTIONS
    baseline_type = st.selectbox(
        "Baseline type (select best that applies)",
        options=_BT_OPTS,
        index=_BT_OPTS.index(ba.get("baseline_type", ""))
        if ba.get("baseline_type", "") in _BT_OPTS
        else 0,
        help="How is the baseline defined for this OPC?",
    )

    baseline_history_yn = st.radio(
        "Baseline history required?",
        ["Yes", "No"],
        index=0 if ba.get("baseline_history_required", False) else 1,
        horizontal=True,
        help="Does the OPC require historical land-use or management data to establish the baseline?",
    )

    _BAD_OPTS = [""] + BASELINE_AUDITABILITY_OPTIONS
    baseline_auditability = st.selectbox(
        "Baseline auditability",
        options=_BAD_OPTS,
        index=_BAD_OPTS.index(ba.get("baseline_auditability", ""))
        if ba.get("baseline_auditability", "") in _BAD_OPTS
        else 0,
        help="How easily can an external auditor verify and reproduce the baseline calculation?",
    )

    st.subheader("Input dependency profile")
    st.caption(
        "Flag which input data types this OPC actually requires to run, "
        "then identify the single most critical bottleneck that limits operational deployment."
    )
    idp = fs.get("input_dependency_profile", {})

    col_d1, col_d2 = st.columns(2)
    with col_d1:
        req_field_mgmt = st.checkbox(
            "Field management data",
            value=idp.get("requires_field_management_data", False),
            help="Tillage, fertilisation, irrigation, sowing/harvest dates, etc.",
        )
        req_soil_sampling = st.checkbox(
            "Soil sampling",
            value=idp.get("requires_soil_sampling", False),
            help="On-site soil physical / chemical measurements (bulk density, texture, SOC, …).",
        )
        req_lab_analysis = st.checkbox(
            "Lab analysis",
            value=idp.get("requires_lab_analysis", False),
            help="Laboratory analysis of soil or plant material (e.g. mineralisation assays).",
        )
    with col_d2:
        req_optical_eo = st.checkbox(
            "Optical EO",
            value=idp.get("requires_optical_eo", False),
            help="Optical satellite or aerial imagery (e.g. Sentinel-2, Landsat).",
        )
        req_sar_eo = st.checkbox(
            "SAR EO",
            value=idp.get("requires_sar_eo", False),
            help="Synthetic Aperture Radar imagery (e.g. Sentinel-1).",
        )
        req_weather = st.checkbox(
            "Weather data",
            value=idp.get("requires_weather_data", False),
            help="Meteorological time series (precipitation, temperature, radiation, …).",
        )

    _BOTTLENECK_OPTS = [""] + BOTTLENECK_OPTIONS
    most_critical_bottleneck = st.selectbox(
        "Most critical operational bottleneck",
        options=_BOTTLENECK_OPTS,
        index=_BOTTLENECK_OPTS.index(idp.get("most_critical_bottleneck", ""))
        if idp.get("most_critical_bottleneck", "") in _BOTTLENECK_OPTS
        else 0,
        help="Which single input or resource is the hardest constraint for running this OPC at scale?",
    )

    st.subheader("Interoperability")
    iop = fs.get("interoperability", {})

    input_interfaces = st.multiselect(
        "Input interfaces (select all that apply)",
        options=INPUT_INTERFACE_OPTIONS,
        default=[
            v for v in iop.get("input_interfaces", []) if v in INPUT_INTERFACE_OPTIONS
        ],
        help="How does the OPC receive its input data?",
    )
    output_formats = st.multiselect(
        "Output formats (select all that apply)",
        options=OUTPUT_FORMAT_OPTIONS,
        default=[
            v for v in iop.get("output_formats", []) if v in OUTPUT_FORMAT_OPTIONS
        ],
        help="In what formats does the OPC deliver its results?",
    )

    st.markdown("*External system integrations*")
    col_i1, col_i2 = st.columns(2)
    with col_i1:
        int_fmis = st.checkbox(
            "Integrates with FMIS",
            value=iop.get("integrates_with_fmis", False),
            help="Farm Management Information System integration.",
        )
        int_lpis = st.checkbox(
            "Integrates with LPIS",
            value=iop.get("integrates_with_lpis", False),
            help="Land Parcel Identification System integration.",
        )
        int_lab = st.checkbox(
            "Integrates with lab data",
            value=iop.get("integrates_with_lab_data", False),
            help="Can ingest laboratory soil or plant sample data directly.",
        )
    with col_i2:
        int_eo = st.checkbox(
            "Integrates with EO pipeline",
            value=iop.get("integrates_with_eo_pipeline", False),
            help="Connects to an Earth Observation processing pipeline (e.g. Sentinel Hub, CDSE).",
        )
        int_schema = st.checkbox(
            "Machine-readable I/O schema",
            value=iop.get("machine_readable_io_schema", False),
            help="Inputs and outputs are described by a formal, machine-readable schema (e.g. JSON Schema, OpenAPI).",
        )

    st.subheader("Runtime & deployment")
    re = fs.get("runtime_environment", {})

    exec_targets = st.multiselect(
        "Execution targets (select all that apply)",
        options=EXECUTION_TARGET_OPTIONS,
        default=[
            t for t in re.get("execution_targets", []) if t in EXECUTION_TARGET_OPTIONS
        ],
        help="Where can this OPC realistically be run? Select all that apply.",
    )

    col_cont, col_par = st.columns(2)
    with col_cont:
        containerised_yn = st.radio(
            "Containerised?",
            ["Yes", "No"],
            index=0 if re.get("containerised", False) else 1,
            horizontal=True,
            help="Is the OPC packaged as a container image (Docker, Singularity, etc.)?",
        )
    with col_par:
        parallelised_yn = st.radio(
            "Requires parallelisation?",
            ["Yes", "No"],
            index=0 if re.get("requires_parallelisation", False) else 1,
            horizontal=True,
            help="Does the OPC require parallel execution (multi-core / MPI / GPU) to run in practice?",
        )

    container_tech = st.multiselect(
        "Container technology (select all that apply)",
        options=CONTAINER_TECH_OPTIONS,
        default=[
            t for t in re.get("container_tech", []) if t in CONTAINER_TECH_OPTIONS
        ],
        help="Which container technology is used?",
    )

    min_compute_notes = st.text_area(
        "Minimum compute notes (optional)",
        value=re.get("minimum_compute_notes", ""),
        height=80,
        placeholder="e.g. 16 GB RAM, 8 cores; runs in ~2 h on a modern laptop for a 100 ha project",
        help="Free-text description of the minimum or typical compute requirements.",
    )

    st.subheader("Automation profile")
    st.caption(
        "For each pipeline stage, indicate the typical level of automation: "
        "**manual** (human action required each run), "
        "**semi_automated** (scripted but needs oversight or occasional intervention), "
        "**automated** (runs end-to-end without human input)."
    )
    ap = fs.get("automation_profile", {})
    _AUTO_OPTS = [""] + AUTOMATION_LEVEL_OPTIONS

    auto_data_ingestion = st.selectbox(
        "Data ingestion",
        options=_AUTO_OPTS,
        index=_AUTO_OPTS.index(ap.get("data_ingestion", ""))
        if ap.get("data_ingestion", "") in _AUTO_OPTS
        else 0,
        help="Fetching / importing raw input data (observations, weather, farm records, EO).",
    )
    auto_preprocessing = st.selectbox(
        "Pre-processing",
        options=_AUTO_OPTS,
        index=_AUTO_OPTS.index(ap.get("preprocessing", ""))
        if ap.get("preprocessing", "") in _AUTO_OPTS
        else 0,
        help="Cleaning, formatting, and harmonising inputs before model execution.",
    )
    auto_model_execution = st.selectbox(
        "Model execution",
        options=_AUTO_OPTS,
        index=_AUTO_OPTS.index(ap.get("model_execution", ""))
        if ap.get("model_execution", "") in _AUTO_OPTS
        else 0,
        help="Running the core model(s).",
    )
    auto_qa_qc = st.selectbox(
        "QA / QC",
        options=_AUTO_OPTS,
        index=_AUTO_OPTS.index(ap.get("qa_qc", ""))
        if ap.get("qa_qc", "") in _AUTO_OPTS
        else 0,
        help="Quality assurance and quality control checks on model outputs.",
    )
    auto_report_generation = st.selectbox(
        "Report generation",
        options=_AUTO_OPTS,
        index=_AUTO_OPTS.index(ap.get("report_generation", ""))
        if ap.get("report_generation", "") in _AUTO_OPTS
        else 0,
        help="Producing the final certificate, report, or structured output delivered to the user.",
    )

    submitted = st.form_submit_button("Save")

# ── On save ───────────────────────────────────────────────────────────────────

if submitted:
    rec["factsheet"].update(
        {
            "opc_name": opc_name.strip(),
            "opc_fullname": opc_fullname.strip(),
            "lead_institutions": [
                l.strip() for l in lead_raw.splitlines() if l.strip()
            ],
            "main_modelling_approach": main_approach,
            "target_lusts": [l.strip() for l in target_raw.splitlines() if l.strip()],
            "geographic_focus": [l.strip() for l in geo_raw.splitlines() if l.strip()],
            "ghgs_covered": ghgs,
            "crop_types_supported": crop_types,
            "cf_practices_covered": cf_practices,
            "reporting_scale": scales,
            "update_frequency": update_freq,
            "user_orientation": user_orient,
            "operational_maturity": op_maturity,
            "openness_level": openness,
            "validation_status": val_status,
            "validation_status_notes": val_notes.strip(),
            "baseline_approach": {
                "baseline_type": baseline_type,
                "baseline_history_required": baseline_history_yn == "Yes",
                "baseline_auditability": baseline_auditability,
            },
            "input_dependency_profile": {
                "requires_field_management_data": req_field_mgmt,
                "requires_soil_sampling": req_soil_sampling,
                "requires_lab_analysis": req_lab_analysis,
                "requires_optical_eo": req_optical_eo,
                "requires_sar_eo": req_sar_eo,
                "requires_weather_data": req_weather,
                "most_critical_bottleneck": most_critical_bottleneck,
            },
            "interoperability": {
                "input_interfaces": input_interfaces,
                "output_formats": output_formats,
                "integrates_with_fmis": int_fmis,
                "integrates_with_lpis": int_lpis,
                "integrates_with_lab_data": int_lab,
                "integrates_with_eo_pipeline": int_eo,
                "machine_readable_io_schema": int_schema,
            },
            "runtime_environment": {
                "execution_targets": exec_targets,
                "containerised": containerised_yn == "Yes",
                "container_tech": container_tech,
                "requires_parallelisation": parallelised_yn == "Yes",
                "minimum_compute_notes": min_compute_notes.strip(),
            },
            "automation_profile": {
                "data_ingestion": auto_data_ingestion,
                "preprocessing": auto_preprocessing,
                "model_execution": auto_model_execution,
                "qa_qc": auto_qa_qc,
                "report_generation": auto_report_generation,
            },
        }
    )
    _s.set_record(rec)
    storage.save_opc(rec)
    st.success("Saved.")
