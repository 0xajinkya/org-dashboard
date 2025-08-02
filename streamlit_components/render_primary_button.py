from typing import Optional

from models.organizations import Organizations
from schemas.organization_enrichment import OrganizationEnrichment
from streamlit_components.fetch_parent_button import render_fetch_parent_button
from streamlit_components.render_parent_organization_dialog import (
    render_parent_organization_dialog,
)
from streamlit_components.render_run_enrichment_button import (
    render_run_enrichment_button,
)
from streamlit_components.replace_with_fetched_button import (
    render_replace_with_fetched_button,
)
from utils.session_state_manager import SessionStateManager


def render_primary_button(
    org: Organizations, result: Optional[OrganizationEnrichment]
):
    # Dynamic session state managers
    state_flag = SessionStateManager(
        lambda org_id: f"show_parent_dialog_{org_id}"
    )
    added_state = SessionStateManager(
        lambda org_id: f"newly_added_parent_{org_id}"
    )

    org_id = org.id
    enrichment = result.get("enrichment") if result else None
    extra_info = enrichment.get("extra_info") if enrichment else None

    # Initialize default session state if not set
    if state_flag.get(org_id) is None:
        state_flag.add(False, org_id)
    if added_state.get(org_id) is None:
        added_state.add(None, org_id)

    if result is None:
        render_run_enrichment_button(org_id)
    elif result and not extra_info:
        render_replace_with_fetched_button(org_id, enrichment)
    elif extra_info:
        state_key = f"show_parent_dialog_{org_id}"
        added_key = f"newly_added_parent_{org_id}"
        render_fetch_parent_button(org_id, state_key)
        render_parent_organization_dialog(
            org_id,
            name=extra_info["name"],
            domain_url=extra_info["domain_url"],
            state_key=state_key,
            added_key=added_key,
        )
