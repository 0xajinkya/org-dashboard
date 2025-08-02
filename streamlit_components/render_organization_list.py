from components.organization_list_item import organization_list_item
from utils.session_state_manager import SessionStateManager

# Static session state manager
current_enrichment_results_state = SessionStateManager(
    lambda: "current_enrichment_results"
)


def render_organization_list(organizations):
    """Render each organization item and initialize enrichment results if absent."""
    enrichment_results = current_enrichment_results_state.get(default={})

    for org in organizations:
        if org.id not in enrichment_results:
            enrichment_results[org.id] = {}

        organization_list_item(org)

    # Update session state after potential mutation
    current_enrichment_results_state.update(enrichment_results)
