import streamlit as st

from models.organizations import Organizations


def render_header(org: Organizations):
    st.markdown("### ✏️ Update Organization Info")
    st.text_input("Organization ID", value=org.id, disabled=True)
