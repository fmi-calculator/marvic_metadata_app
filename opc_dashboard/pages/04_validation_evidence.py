"""Page 4 — Validation Evidence Overview (opc_validation_evidence_overview.csv)."""
import sys
import pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

import streamlit as st

from core import state as _s
from core import storage

_s.ensure_session_state()
st.title("Validation Evidence")

if not _s.is_loaded():
    st.warning("No OPC record loaded. Return to the Home page to load or create one.")
    st.stop()

rec     = _s.get_record()
ev_list = rec.get("validation_evidence_overview", [])

st.caption(f"Editing: **{rec['record_metadata']['opc_id']}**")
st.markdown(
    "Add one entry per validated variable or process. "
    "For each entry, describe the dataset used, the metrics computed, "
    "and the key findings."
)

# ── Entry selector ────────────────────────────────────────────────────────────
labels = [
    f"{i+1}. {e.get('variable_validated', '(unnamed)')}"
    for i, e in enumerate(ev_list)
]

if "val_idx" not in st.session_state or st.session_state["val_idx"] >= len(ev_list):
    st.session_state["val_idx"] = 0

col_sel, col_add = st.columns([3, 1])

with col_sel:
    if ev_list:
        chosen_label = st.selectbox(
            "Validation entry",
            options=labels,
            index=st.session_state["val_idx"],
        )
        st.session_state["val_idx"] = labels.index(chosen_label)
    else:
        st.info("No entries yet. Click **Add entry** to create one.")

with col_add:
    st.write("")  # vertical alignment
    if st.button("＋ Add entry", use_container_width=True):
        ev_list.append({
            "variable_validated": "",
            "dataset_type":       "",
            "geography":          "",
            "period":             "",
            "validation_metrics": [],
            "summary_result":     "",
            "remaining_gap":      "",
        })
        rec["validation_evidence_overview"] = ev_list
        _s.set_record(rec)
        st.session_state["val_idx"] = len(ev_list) - 1
        st.rerun()

st.divider()

if not ev_list:
    st.stop()

idx = st.session_state["val_idx"]
e   = ev_list[idx]

# ── Detail form ───────────────────────────────────────────────────────────────
with st.form("val_form"):
    st.subheader(f"Validation entry {idx + 1} of {len(ev_list)}")

    variable_validated = st.text_input(
        "Variable validated *",
        value=e.get("variable_validated", ""),
        placeholder="e.g. delta SOC, N2O flux, yield",
        help="The model output variable or process that was validated.",
    )

    dataset_type = st.text_input(
        "Dataset type *",
        value=e.get("dataset_type", ""),
        placeholder="e.g. on-farm monitoring, benchmark site, farmer records",
        help="Type of independent data used for validation.",
    )

    geography = st.text_input(
        "Geography *",
        value=e.get("geography", ""),
        placeholder="e.g. Finland, Northern Europe, global",
        help="Geographic extent or region covered by the validation dataset.",
    )

    period = st.text_input(
        "Period *",
        value=e.get("period", ""),
        placeholder="e.g. 2016–2025, 2020",
        help="Time period spanned by the validation dataset.",
    )

    metrics_raw = st.text_area(
        "Validation metrics * (one per line)",
        value="\n".join(e.get("validation_metrics", [])),
        height=90,
        placeholder="RMSE\nbias\nR2",
        help="Enter one metric name per line.",
    )

    summary_result = st.text_area(
        "Summary result",
        value=e.get("summary_result", ""),
        height=90,
        placeholder="Brief description of the main validation findings.",
    )

    remaining_gap = st.text_area(
        "Remaining gap",
        value=e.get("remaining_gap", ""),
        height=90,
        placeholder="Known limitations or domains where validation is still lacking.",
    )

    col_save, col_delete = st.columns([4, 1])
    with col_save:
        submitted = st.form_submit_button("Save", use_container_width=True)
    with col_delete:
        delete = st.form_submit_button("🗑 Delete", use_container_width=True,
                                       type="secondary")

# ── On save ───────────────────────────────────────────────────────────────────
if submitted:
    errors = []
    if not variable_validated.strip():
        errors.append("Variable validated is required.")
    metrics_list = [m.strip() for m in metrics_raw.splitlines() if m.strip()]
    if not metrics_list:
        errors.append("At least one validation metric is required.")
    if not dataset_type.strip():
        errors.append("Dataset type is required.")
    if not geography.strip():
        errors.append("Geography is required.")
    if not period.strip():
        errors.append("Period is required.")

    if errors:
        for err in errors:
            st.error(err)
    else:
        ev_list[idx] = {
            "variable_validated": variable_validated.strip(),
            "dataset_type":       dataset_type.strip(),
            "geography":          geography.strip(),
            "period":             period.strip(),
            "validation_metrics": metrics_list,
            "summary_result":     summary_result.strip(),
            "remaining_gap":      remaining_gap.strip(),
        }
        rec["validation_evidence_overview"] = ev_list
        _s.set_record(rec)
        storage.save_opc(rec)
        st.success("Saved.")

if delete:
    ev_list.pop(idx)
    rec["validation_evidence_overview"] = ev_list
    _s.set_record(rec)
    storage.save_opc(rec)
    st.session_state["val_idx"] = max(0, idx - 1)
    st.rerun()
