import streamlit as st

from utils.session_state_manager import SessionStateManager


def render_pagination_controls():
    """Render pagination navigation buttons with abstracted session state management."""
    page_state = SessionStateManager(lambda: "page")
    current_page = page_state.get() or 1

    col_prev, col_next = st.columns(2)

    with col_prev:
        if st.button("⬅️ Prev", disabled=current_page == 1):
            page_state.add(current_page - 1)
            st.rerun()

    with col_next:
        if st.button("Next ➡️"):
            page_state.add(current_page + 1)
            st.rerun()

    st.caption(f"Page {current_page}")
