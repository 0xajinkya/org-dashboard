from utils.session_state_manager import SessionStateManager


def initialize_session_state():
    """Initialize all requisite session state variables using SessionStateManager."""
    static_keys = {
        "page": 1,
        "cached_pages": {},
        "enrichment_results": {},
        "active_org_dialog": None,
        "current_enrichment_results": {},
    }

    for key, default_value in static_keys.items():
        manager = SessionStateManager(lambda: key)
        if manager.get(default=None) is None:
            manager.add(default_value)
