import streamlit as st

from components.add_organization import add_organization
from utils.session_state_manager import SessionStateManager


def render_add_new_organization_section(
    org_id: str, name: str, domain_url: str, added_key: str
):
    st.markdown("#### ➕ Add a New Organization")

    added_state = SessionStateManager(lambda oid: added_key)

    if st.button("Add New Organization", key=f"add-org-{org_id}"):
        new_org = add_organization(name=name, domain_url=domain_url)
        if new_org:
            added_state.add(new_org, org_id)
            st.success("✅ New organization created and added to dropdown.")
            st.rerun()
