import streamlit as st

from models.organizations import Organizations
from services.organizations import OrganizationsService
from utils.session_state_manager import SessionStateManager

PER_PAGE = 4

# Define static managers
page_state = SessionStateManager(lambda: "page")
cached_pages_state = SessionStateManager(lambda: "cached_pages")


def fetch_organizations_for_current_page():
    """Fetch and cache organizations for the current page if not already cached."""
    current_page = page_state.get()
    cached_pages = cached_pages_state.get(default={})

    if current_page not in cached_pages:
        with st.spinner(f"Fetching page {current_page}..."):
            organizations = OrganizationsService.find_many(
                filters=[Organizations.domain_url.is_(None)],
                page=current_page,
                limit=PER_PAGE,
            )
            cached_pages[current_page] = organizations
            cached_pages_state.update(cached_pages)

    return cached_pages[current_page]
