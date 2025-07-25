import streamlit as st
import streamlit_shadcn_ui as ui
from services.organizations import OrganizationsService
from models.organizations import Organizations

PER_PAGE = 4

def organization_listings():
    # Initialize session state
    if "page" not in st.session_state:
        st.session_state.page = 1
    if "cached_pages" not in st.session_state:
        st.session_state.cached_pages = {}

    current_page = st.session_state.page

    # Fetch and cache organizations if not already
    if current_page not in st.session_state.cached_pages:
        with st.spinner(f"Fetching page {current_page}..."):
            orgs = OrganizationsService.find_many(
                filters=[Organizations.domain_url.is_(None)],
                page=current_page,
                limit=PER_PAGE
            )
            st.session_state.cached_pages[current_page] = orgs

    orgs = st.session_state.cached_pages[current_page]

    # Render cards: 2 per row
    for i in range(0, len(orgs), 2):
        col1, col2 = st.columns(2)

        for j, col in enumerate([col1, col2]):
            if i + j >= len(orgs):
                continue
            org = orgs[i + j]
            with col:
                with st.container(border=True):
                    st.markdown(f"#### #{org.id[:5]}")
                    st.markdown(f"**{org.name}**")
                    st.markdown(f"`{org.domain_url or 'No domain'}`")

                    # Buttons on same line
                    btn_col1, btn_col2 = st.columns([1, 1])
                    with btn_col1:
                        ui.button(
                            text="Fetch Info",
                            key=f"fetch-{org.id}",
                            variant="default",
                            full_width=True
                        )
                    with btn_col2:
                        ui.button(
                            text="Update Info",
                            key=f"update-{org.id}",
                            variant="secondary",
                            full_width=True
                        )

    # Pagination controls
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
