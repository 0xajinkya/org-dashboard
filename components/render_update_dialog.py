from components.organization_update_dialog import organization_update_dialog
from models.organizations import Organizations
from schemas.organization_enrichment import OrganizationEnrichment
from utils.session_state_manager import SessionStateManager


def render_update_dialog(
    org: Organizations, result: OrganizationEnrichment | None
):
    active_dialog_state = SessionStateManager(lambda: "active_org_dialog")

    if active_dialog_state.get() == org.id:
        organization_update_dialog(org, result or None)
