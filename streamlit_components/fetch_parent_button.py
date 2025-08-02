import streamlit as st

from utils.session_state_manager import SessionStateManager


def render_fetch_parent_button(org_id: str, state_key: str):
    # Wrap the raw session key using a no-arg lambda for passthrough
    state_flag = SessionStateManager(lambda: state_key)

    if st.button(
        "Fetch Parent Organization",
        key=f"enrichment-fetch-parent-{org_id}",
        use_container_width=True,
        type="primary",
    ):
        state_flag.add(True)
        st.rerun()
