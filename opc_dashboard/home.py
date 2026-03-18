"""Start page — select or create an OPC record."""
import re
import sys
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).parent))

import streamlit as st

from core import state as _s
from core import storage
from core import defaults

_s.ensure_session_state()

st.title("OPC Metadata — Home")

# ── Load / select existing OPC ────────────────────────────────────────────────
existing = storage.list_opcs()

st.subheader("Load existing OPC")
if existing:
    sel = st.selectbox("Select OPC ID from the list and load to continue editing or create a new record.", options=["— select —"] + existing)
    if sel != "— select —":
        if st.button("Load", key="load_btn"):
            record = storage.load_opc(sel)
            _s.set_record(record)
            st.success(f"Loaded: {sel}")
            st.rerun()
else:
    st.info("No OPC records found. Create one below.")

if _s.is_loaded():
    rec = _s.get_record()
    meta = rec["record_metadata"]
    st.success(
        f"Currently loaded: **{meta['opc_id']}** "
        f"(last updated: {meta['last_updated']})"
    )
    st.markdown("Continue with the tabs on the sidebar to fill/edit in each section.")

st.divider()

# ── Create new OPC ────────────────────────────────────────────────────────────
st.subheader("Create new OPC record")

with st.form("new_opc_form"):
    new_id   = st.text_input(
        "OPC ID *",
        placeholder="A specific string to identify your entry, e.g.: fi_carbs_hybrid_arable_opc_testv0",
        help="A string of lowercase letters, numbers, underscores, and hyphens. Pattern: ^[a-z0-9_-]+$",
    )
    creator  = st.text_input("Created by *", placeholder="Your name and organisation")
    notes_in = st.text_area("Notes (optional)", height=80)
    submitted = st.form_submit_button("Create")

if submitted:
    _id_pattern = re.compile(r"^[a-z0-9_\-]+$")
    errors = []
    if not new_id:
        errors.append("OPC ID is required.")
    elif not _id_pattern.match(new_id):
        errors.append("OPC ID must match ^[a-z0-9_-]+$ (lowercase, digits, underscores, hyphens only).")
    elif storage.record_exists(new_id):
        errors.append(f"OPC '{new_id}' already exists. Load it instead.")
    if not creator:
        errors.append("Created by is required.")

    if errors:
        for err in errors:
            st.error(err)
    else:
        record = defaults.new_opc_record(new_id, creator, notes_in)
        storage.save_opc(record)
        _s.set_record(record)
        st.success(f"Created: {new_id}")
        st.rerun()

if not _s.is_loaded():
    st.warning("No OPC record loaded. Load or create one above.")
