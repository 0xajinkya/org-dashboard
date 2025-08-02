"""Organization Listings Component"""

from streamlit_components.fetch_organizations_for_current_page import (
    fetch_organizations_for_current_page,
)
from streamlit_components.initialize_session_state import (
    initialize_session_state,
)
from streamlit_components.render_organization_list import (
    render_organization_list,
)
from streamlit_components.render_pagination_controls import (
    render_pagination_controls,
)


def organization_listings():
    """Main entry point to render the paginated list of organizations."""
    initialize_session_state()
    organizations = fetch_organizations_for_current_page()
    render_organization_list(organizations)
    render_pagination_controls()
