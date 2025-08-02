import streamlit as st

from models.organizations import Organizations
from schemas.organization_enrichment import OrganizationEnrichment
from streamlit_components.render_primary_button import render_primary_button
from utils.session_state_manager import SessionStateManager

# Static session manager
active_org_dialog_state = SessionStateManager(lambda: "active_org_dialog")


def render_action_buttons(
    org: Organizations, result: OrganizationEnrichment | None
):
    """Render manual update trigger and primary enrichment controls."""
    # --- Update Organization Manually (Full Width Button) ---
    if st.button(
        "Update Organization Manually",
        key=f"show-dialog-{org.id}",
        use_container_width=True,
        type="secondary",
    ):
        active_org_dialog_state.add(org.id)

    st.markdown(" ")  # Spacer for visual clarity

    # --- Render Primary Button Group ---
    render_primary_button(org, result)
