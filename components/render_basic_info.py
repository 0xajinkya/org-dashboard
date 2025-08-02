import streamlit as st

from models.organizations import Organizations


def render_basic_info(org: Organizations):
    st.markdown(f"#### #{org.id}")
    st.markdown(f"**{org.name}**")
    st.markdown(f"`{org.domain_url or 'No domain'}`")
