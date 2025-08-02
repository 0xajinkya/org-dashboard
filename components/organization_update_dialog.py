import streamlit as st

from components.info_card import organization_information_card
from components.render_edit_fields import render_edit_fields
from components.render_header import render_header
from components.render_info_fetch_controls import render_info_fetch_controls
from components.render_update_button import render_update_button
from models.organizations import Organizations
from schemas.organization_enrichment import OrganizationEnrichment
from utils.session_state_manager import SessionStateManager


def organization_update_dialog(
    org: Organizations, enrichment: OrganizationEnrichment | None
):
    """Render the organization update dialog and associated enrichment UI."""
    with st.container(border=True):
        render_header(org)
        render_edit_fields(org)
        render_update_button(org)
        st.markdown("---")
        render_info_fetch_controls(org, enrichment)
        render_close_button(org)
        render_fetched_information(org.id)


def render_close_button(org: Organizations):
    """Renders the 'Close' button and resets active dialog state if clicked."""
    active_dialog_state = SessionStateManager(lambda: "active_org_dialog")

    if st.button(
        "❌ Close Dialog",
        key=f"close-update-dialog-{org.id}",
        type="secondary",
    ):
        active_dialog_state.add(None)
        st.rerun()


def render_fetched_information(org_id: str):
    """Displays fetched organization information and verdicts."""
    fetch_state = SessionStateManager(lambda oid: f"org-info-fetched-{oid}")
    verdict_state = SessionStateManager(
        lambda oid: f"org-info-perplexity-{oid}"
    )

    fetched_info = fetch_state.get(org_id)
    verdict = verdict_state.get(org_id)

    if fetched_info and fetched_info != "none":
        st.markdown("#### 📋 Related Organization Information")
        for info in fetched_info:
            matched_verdict = match_verdict(verdict, info["id"])
            organization_information_card(
                org_id, info, matched_verdict, verdict
            )


def match_verdict(verdict: dict, info_id: str):
    """Matches a verdict entry to a specific organization information ID."""
    if not isinstance(verdict, dict):
        return None

    for iv in verdict.get("information_verdicts", []):
        if iv.get("organization_information_id") == str(info_id):
            return iv
    return None
