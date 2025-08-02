from typing import List

import streamlit as st

from models.organizations import Organizations
from services.organization_information import OrganizationInformationService


def organization_card(
    organization: Organizations, organization_information_ids: List[int]
):
    """
    Renders a visual card in Streamlit for an Organizations entity.

    Parameters:
    - organization (Organizations): An instance of the Organizations SQLAlchemy model.
    - organization_information_ids (List[int]): List of org info IDs to reassign.
    """
    with st.container(border=True):
        st.markdown("**Organization**")
        st.text(f"ID: {organization.id}")
        st.text(f"Name: {organization.name}")
        st.text(f"Domain URL: {organization.domain_url or 'N/A'}")

        if st.button("Attach to this", key=f"attach-to-{organization.id}"):
            for info_id in organization_information_ids:
                OrganizationInformationService.update_one(
                    id=info_id,
                    organization_id=organization.id,
                )
            st.success("✅ Organization Informations updated successfully!")
