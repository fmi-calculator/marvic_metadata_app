"""Streamlit session state helpers."""
import streamlit as st


def ensure_session_state() -> None:
    """Initialise all required session state keys if not already set."""
    defaults = {
        "opc_record":      None,
        "opc_id":          None,
        "dirty":           False,
        "last_validation": None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def get_record() -> dict | None:
    return st.session_state.get("opc_record")


def set_record(record: dict) -> None:
    st.session_state["opc_record"] = record


def mark_dirty() -> None:
    st.session_state["dirty"] = True


def is_loaded() -> bool:
    return st.session_state.get("opc_record") is not None
