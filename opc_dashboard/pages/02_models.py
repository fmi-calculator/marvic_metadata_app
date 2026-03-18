"""Page 2 — Models (opc_models.csv)."""
import sys
import pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

import streamlit as st

from core import state as _s
from core import storage
from core.enums import MODEL_ROLE_OPTIONS

_s.ensure_session_state()
st.title("Models")

if not _s.is_loaded():
    st.warning("No OPC record loaded. Return to the Home page to load or create one.")
    st.stop()

rec    = _s.get_record()
models = rec.get("models", [])

st.caption(f"Editing: **{rec['record_metadata']['opc_id']}**")
st.markdown(
    "Each OPC may have one or more model components (e.g. an upstream productivity model "
    "and a core soil carbon model). Add one entry per component."
)

# ── Model selector ────────────────────────────────────────────────────────────
labels = [f"{i+1}. {m.get('model_name', '(unnamed)')}" for i, m in enumerate(models)]

if "model_idx" not in st.session_state or st.session_state["model_idx"] >= len(models):
    st.session_state["model_idx"] = 0

col_sel, col_add = st.columns([3, 1])

with col_sel:
    if models:
        chosen_label = st.selectbox("Model component", options=labels,
                                    index=st.session_state["model_idx"])
        st.session_state["model_idx"] = labels.index(chosen_label)
    else:
        st.info("No model components yet. Click **Add model** to create one.")

with col_add:
    st.write("")  # vertical alignment
    if st.button("＋ Add model", use_container_width=True):
        models.append({
            "model_name":                  "",
            "model_role":                  "",
            "model_version":               "",
            "model_repository":            "",
            "scientific_publication_dois": [],
            "notes":                       "",
        })
        rec["models"] = models
        _s.set_record(rec)
        st.session_state["model_idx"] = len(models) - 1
        st.rerun()

st.divider()

# ── Detail form ───────────────────────────────────────────────────────────────
if not models:
    st.stop()

idx = st.session_state["model_idx"]
m   = models[idx]

with st.form("model_form"):
    st.subheader(f"Model component {idx + 1} of {len(models)}")

    model_name = st.text_input(
        "Model name *",
        value=m.get("model_name", ""),
        help="Short unique name for this component, e.g. RothC, CENTURY, LPJ-GUESS",
    )

    role_opts = [""] + MODEL_ROLE_OPTIONS
    model_role = st.selectbox(
        "Model role * (select best that applies)",
        options=role_opts,
        index=(0 if not m.get("model_role")
               else role_opts.index(m["model_role"])),
        help=(
            "core: the primary carbon/GHG model, especially if it's the only model in your OPC. "
            "upstream: provides inputs to the core (e.g. biomass, weather preprocessing). "
            "plant: simulates plant growth and productivity. "
            "soil: simulates soil processes (e.g. carbon, water, nitrogen). "
            "ecosystem: simulates the whole soil-plant system. "
            "downstream: post-processes outputs (e.g. aggregation, reporting). "
            "assimilation: data assimilation layer. "
            "auxiliary: any other supporting component."
        ),
    )

    model_version = st.text_input(
        "Version",
        value=m.get("model_version", ""),
        help="Version string, e.g. 2.1.0 or git commit SHA",
    )

    model_repository = st.text_input(
        "Repository URL",
        value=m.get("model_repository", ""),
        placeholder="https://github.com/org/model",
        help="URL to the code repository or model home page",
    )

    dois_raw = st.text_area(
        "Scientific publication DOIs (one per line)",
        value="\n".join(m.get("scientific_publication_dois", [])),
        height=100,
        placeholder="10.1234/example.2024",
        help="Enter one DOI per line, without the https://doi.org/ prefix",
    )

    notes = st.text_area(
        "Notes (optional)",
        value=m.get("notes", ""),
        height=80,
    )

    col_save, col_delete = st.columns([4, 1])
    with col_save:
        submitted = st.form_submit_button("Save", use_container_width=True)
    with col_delete:
        delete = st.form_submit_button("🗑 Delete", use_container_width=True,
                                       type="secondary")

# ── On save ───────────────────────────────────────────────────────────────────
if submitted:
    models[idx] = {
        "model_name":                  model_name.strip(),
        "model_role":                  model_role,
        "model_version":               model_version.strip(),
        "model_repository":            model_repository.strip(),
        "scientific_publication_dois": [
            d.strip() for d in dois_raw.splitlines() if d.strip()
        ],
        "notes":                       notes.strip(),
    }
    rec["models"] = models
    _s.set_record(rec)
    storage.save_opc(rec)
    st.success("Saved.")

if delete:
    models.pop(idx)
    rec["models"] = models
    _s.set_record(rec)
    storage.save_opc(rec)
    st.session_state["model_idx"] = max(0, idx - 1)
    st.rerun()
