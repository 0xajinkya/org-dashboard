import streamlit as st

from models.organizations import Organizations
from services.organizations import OrganizationsService
from utils.session_state_manager import SessionStateManager


def render_update_button(org: Organizations):
    if st.button("Update Organization", key=f"btn-update-org-{org.id}"):
        try:
            name_state = SessionStateManager(
                lambda oid: f"org-update-dialog-{oid}-name"
            )
            domain_state = SessionStateManager(
                lambda oid: f"org-update-dialog-{oid}-domain"
            )

            OrganizationsService.update_one(
                id=org.id,
                name=name_state.get(org.id),
                domain_url=domain_state.get(org.id),
            )
            st.success("✅ Organization updated successfully!")
        except Exception as e:
            st.error(f"❌ Failed to update organization: {e}")
