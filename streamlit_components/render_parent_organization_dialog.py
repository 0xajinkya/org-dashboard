import streamlit as st
from sqlalchemy import or_

from components.existing_organization_info import (
    render_existing_organization_info,
)
from components.render_add_new_organization_section import (
    render_add_new_organization_section,
)
from models.organizations import Organizations
from services.organizations import OrganizationsService
from utils.session_state_manager import SessionStateManager


def render_parent_organization_dialog(
    org_id: str, name: str, domain_url: str, state_key: str, added_key: str
):
    # Instantiate session managers with direct key usage
    state_flag = SessionStateManager(lambda: state_key)
    added_state = SessionStateManager(lambda: added_key)

    # Guard clause – only show dialog if state is active
    if not state_flag.get(default=False):
        return

    st.markdown("#### 🔍 Searching for Matching Parent Organizations...")

    # Construct filters for fuzzy matching
    domain_str = str(domain_url)
    parent_organizations = OrganizationsService.find_many(
        filters=[
            or_(
                Organizations.name.match(name),
                Organizations.name.ilike(f"%{name}%"),
                Organizations.name.like(f"{name}%"),
                Organizations.domain_url.match(domain_str),
                Organizations.domain_url.ilike(f"%{domain_str}%"),
                Organizations.domain_url.like(f"{domain_str}%"),
            )
        ]
    )

    # Add the newly added org if present in session
    added_org = added_state.get()
    if added_org:
        parent_organizations.append(added_org)

    # Render existing matches and UI to add new organization
    render_existing_organization_info(org_id, parent_organizations)
    render_add_new_organization_section(org_id, name, domain_url, added_key)

    # Handle close dialog
    if st.button("❌ Close", key=f"close-dialog-{org_id}"):
        state_flag.add(False)
        added_state.add(None)
        st.rerun()
