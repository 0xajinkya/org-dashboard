import streamlit as st
from components.organization_list_item import render_organization_item
from services.organizations import OrganizationsService
from models.organizations import Organizations

PER_PAGE = 4

def organization_listings():
    if "page" not in st.session_state:
        st.session_state.page = 1
    if "cached_pages" not in st.session_state:
        st.session_state.cached_pages = {}
    if "enrichment_results" not in st.session_state:
        st.session_state.enrichment_results = {}
    if "active_org_dialog" not in st.session_state:
        st.session_state.active_org_dialog = None
    if "current_enrichment_results" not in st.session_state:
        st.session_state.current_enrichment_results = {}

    current_page = st.session_state.page

    if current_page not in st.session_state.cached_pages:
        with st.spinner(f"Fetching page {current_page}..."):
            orgs = OrganizationsService.find_many(
                filters=[Organizations.domain_url.is_(None)],
                page=current_page,
                limit=PER_PAGE
            )
            st.session_state.cached_pages[current_page] = orgs

    orgs = st.session_state.cached_pages[current_page]

    for org in orgs:
        if org.id not in st.session_state.current_enrichment_results:
            st.session_state.current_enrichment_results[org.id] = {}
        render_organization_item(org)

    nav_prev, nav_next = st.columns(2)
    with nav_prev:
        if st.button("⬅️ Prev", disabled=current_page == 1):
            st.session_state.page -= 1
            st.rerun()
    with nav_next:
        if st.button("Next ➡️"):
            st.session_state.page += 1
            st.rerun()

    st.caption(f"Page {current_page}")