import streamlit as st

from streamlit_components.trigger_enrichment import trigger_enrichment


def render_run_enrichment_button(org_id: str):
    if st.button(
        "Create Enrichment",
        key=f"test-fetch-{org_id}",
        use_container_width=True,
        type="primary",
    ):
        trigger_enrichment(org_id)
        st.rerun()
