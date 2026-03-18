"""Entry point — defines sidebar navigation for the OPC Metadata app."""
import sys
import pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))

import streamlit as st

from core import state as _s

st.set_page_config(page_title="OPC Metadata", layout="centered")
_s.ensure_session_state()

pg = st.navigation([
    st.Page("home.py",                             title="Start"),
    st.Page("pages/01_factsheet.py",               title="Factsheet"),
    st.Page("pages/02_models.py",                  title="Models"),
    st.Page("pages/03_uncertainty_propagation.py", title="Uncertainty"),
    st.Page("pages/04_validation_evidence.py",     title="Validation"),
    st.Page("pages/05_crcf_matrix.py",             title="CRCF"),
    st.Page("pages/06_review_validate.py",         title="Review"),
    st.Page("pages/07_export.py",                  title="Export"),
])
pg.run()

