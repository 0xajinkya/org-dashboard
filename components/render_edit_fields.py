import streamlit as st

from models.organizations import Organizations


def render_edit_fields(org: Organizations):
    dialog_prefix = f"org-update-dialog-{org.id}"
    st.text_input(
        "Organization Name", value=org.name, key=f"{dialog_prefix}-name"
    )
    st.text_input(
        "Domain URL", value=org.domain_url or "", key=f"{dialog_prefix}-domain"
    )
