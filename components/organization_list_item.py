from typing import Dict

import streamlit as st

from components.render_action_buttons import render_action_buttons
from components.render_basic_info import render_basic_info
from components.render_enrichment_status import render_enrichment_status
from components.render_update_dialog import render_update_dialog
from models.organizations import Organizations
from schemas.organization_enrichment import OrganizationEnrichment
from services.perplexity import PerplexityService
from utils.session_state_manager import SessionStateManager

# Static session manager
enrichment_results_state = SessionStateManager(lambda: "enrichment_results")
perplexity_service = PerplexityService()


def organization_list_item(org: Organizations):
    """Render a single organization item with enrichment controls and manual update dialog."""
    enrichment_results: Dict[str, OrganizationEnrichment] = (
        enrichment_results_state.get(default={})
    )
    org_result = enrichment_results.get(org.id)

    with st.container(border=True):
        render_basic_info(org)
        render_enrichment_status(org_result)
        render_action_buttons(org, org_result)
        render_update_dialog(org, org_result)
