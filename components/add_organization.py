from typing import Optional

import streamlit as st

from services.organization_information import OrganizationInformationService
from services.organizations import OrganizationsService
from utils.session_state_manager import SessionStateManager


def add_organization(
    name: Optional[str] = None,
    domain_url: Optional[str] = None,
    organization_information_id: Optional[str] = None,
    added_key: Optional[str] = None,
):
    st.markdown("### ➕ Add Organization")

    with st.form(key="add-org-form", border=True):
        input_name = st.text_input("Name", value=name or "")
        input_domain_url = st.text_input("Domain URL", value=domain_url or "")

        submitted = st.form_submit_button("Create Organization & Link To This")

        if submitted:
            if not input_name.strip():
                st.error("❌ Name is required.")
                return

            try:
                organization = OrganizationsService.create_one(
                    name=input_name.strip(),
                    domain_url=input_domain_url.strip() or None,
                )

                if organization_information_id:
                    OrganizationInformationService.update_one(
                        organization_information_id,
                        organization_id=organization.id,
                    )

                if added_key:
                    added_state = SessionStateManager(lambda _: added_key)
                    added_state.add(organization, key=None)

                st.success("✅ Organization created successfully!")
                st.write(f"**ID**: {organization.id}")
                st.write(f"**Name**: {organization.name}")
                st.write(f"**Domain URL**: {organization.domain_url or 'N/A'}")

                return organization

            except Exception as e:
                st.error(f"❌ Failed to create organization: {e}")
