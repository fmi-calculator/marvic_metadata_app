"""Page 7 — Export CSVs."""
import sys
import pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

import streamlit as st

from core import state as _s
from core import storage
from core.flatten import (
    flatten_factsheet,
    flatten_models,
    flatten_uncertainty,
    flatten_validation_evidence,
    flatten_crcf_matrix,
    export_all_csvs,
)

_s.ensure_session_state()
st.title("Export")

if not _s.is_loaded():
    st.warning("No OPC record loaded. Return to the Home page to load or create one.")
    st.stop()

rec    = _s.get_record()
opc_id = rec["record_metadata"]["opc_id"]

st.caption(f"Exporting: **{opc_id}**")

# ── Download raw JSON ─────────────────────────────────────────────────────────
import json, csv, io
import pandas as pd

st.download_button(
    "⬇ Download OPC JSON",
    data=json.dumps(rec, indent=2),
    file_name=f"{opc_id}.json",
    mime="application/json",
)

st.divider()

# ── Previews ──────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs(["Factsheet", "Models", "Uncertainty", "Validation", "CRCF"])

with tab1:
    st.subheader("Factsheet row preview")
    fs_row = flatten_factsheet(rec)
    st.dataframe(pd.DataFrame([fs_row]).T.rename(columns={0: "value"}), use_container_width=True)

with tab2:
    st.subheader("Models rows preview")
    model_rows = flatten_models(rec)
    if model_rows:
        st.dataframe(pd.DataFrame(model_rows), use_container_width=True)
    else:
        st.info("No model components recorded yet.")

with tab3:
    st.subheader("Uncertainty propagation rows preview")
    unc_rows = flatten_uncertainty(rec)
    if unc_rows:
        st.dataframe(pd.DataFrame(unc_rows), use_container_width=True)
    else:
        st.info("No uncertainty propagation entries recorded yet.")

with tab4:
    st.subheader("Validation evidence rows preview")
    val_rows = flatten_validation_evidence(rec)
    if val_rows:
        st.dataframe(pd.DataFrame(val_rows), use_container_width=True)
    else:
        st.info("No validation evidence entries recorded yet.")

with tab5:
    st.subheader("CRCF model readiness rows preview")
    crcf_rows = flatten_crcf_matrix(rec)
    if crcf_rows:
        st.dataframe(pd.DataFrame(crcf_rows), use_container_width=True)
    else:
        st.info("No CRCF matrix entries recorded yet.")

st.divider()

# ── Single-record export ──────────────────────────────────────────────────────
st.subheader("Export this OPC")

col1, col2, col3, col4, col5, col6 = st.columns(6)

with col1:
    fs_row = flatten_factsheet(rec)
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=list(fs_row.keys()))
    writer.writeheader()
    writer.writerow(fs_row)
    st.download_button(
        "⬇ Factsheet CSV",
        data=buf.getvalue(),
        file_name=f"{opc_id}_factsheet.csv",
        mime="text/csv",
        use_container_width=True,
    )

with col2:
    model_rows = flatten_models(rec)
    if model_rows:
        buf2 = io.StringIO()
        writer2 = csv.DictWriter(buf2, fieldnames=list(model_rows[0].keys()))
        writer2.writeheader()
        writer2.writerows(model_rows)
        st.download_button(
            "⬇ Models CSV",
            data=buf2.getvalue(),
            file_name=f"{opc_id}_models.csv",
            mime="text/csv",
            use_container_width=True,
        )
    else:
        st.button("⬇ Models CSV", disabled=True, use_container_width=True,
                  help="No model components to export yet.")

with col3:
    unc_rows = flatten_uncertainty(rec)
    if unc_rows:
        buf3 = io.StringIO()
        writer3 = csv.DictWriter(buf3, fieldnames=list(unc_rows[0].keys()))
        writer3.writeheader()
        writer3.writerows(unc_rows)
        st.download_button(
            "⬇ Uncertainty CSV",
            data=buf3.getvalue(),
            file_name=f"{opc_id}_uncertainty_propagation.csv",
            mime="text/csv",
            use_container_width=True,
        )
    else:
        st.button("⬇ Uncertainty CSV", disabled=True, use_container_width=True,
                  help="No uncertainty propagation entries to export yet.")

with col4:
    val_rows = flatten_validation_evidence(rec)
    if val_rows:
        buf4 = io.StringIO()
        writer4 = csv.DictWriter(buf4, fieldnames=list(val_rows[0].keys()))
        writer4.writeheader()
        writer4.writerows(val_rows)
        st.download_button(
            "⬇ Validation CSV",
            data=buf4.getvalue(),
            file_name=f"{opc_id}_validation_evidence.csv",
            mime="text/csv",
            use_container_width=True,
        )
    else:
        st.button("⬇ Validation CSV", disabled=True, use_container_width=True,
                  help="No validation evidence entries to export yet.")

with col5:
    crcf_rows = flatten_crcf_matrix(rec)
    if crcf_rows:
        buf5 = io.StringIO()
        writer5 = csv.DictWriter(buf5, fieldnames=list(crcf_rows[0].keys()))
        writer5.writeheader()
        writer5.writerows(crcf_rows)
        st.download_button(
            "⬇ CRCF CSV",
            data=buf5.getvalue(),
            file_name=f"{opc_id}_crcf_matrix.csv",
            mime="text/csv",
            use_container_width=True,
        )
    else:
        st.button("⬇ CRCF CSV", disabled=True, use_container_width=True,
                  help="No CRCF matrix entries to export yet.")

with col6:
    if st.button("💾 Save all to exports/", use_container_width=True):
        export_all_csvs([rec], storage.EXPORTS_DIR)
        st.success(f"Saved to {storage.EXPORTS_DIR}")

st.divider()

# ── All-records export ────────────────────────────────────────────────────────
st.subheader("Export all OPCs")

all_ids = storage.list_opcs()
st.write(f"Records found: {len(all_ids)}")

if st.button("💾 Export all to exports/ folder"):
    all_records = [storage.load_opc(i) for i in all_ids]
    export_all_csvs(all_records, storage.EXPORTS_DIR)
    st.success(f"5 CSV tables written to {storage.EXPORTS_DIR}")
