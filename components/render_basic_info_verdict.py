import streamlit as st


def render_basic_info_verdict(info_id: str, info: dict):
    st.markdown("**Record**")
    st.text(f"ID: {info_id}")
    st.text(f"Name: {info['name']}")
    st.text(f"Preprocessed Name: {info['preprocessed_name']}")
    st.text(f"Organization ID: {info.get('organization_id', 'N/A')}")
    st.text(
        f"Hospital/University: {'Yes' if info.get('is_hospital_or_university') else 'No'}"
    )
