import streamlit as st

from models.organizations import OrganizationInformation
from services.organization_information import OrganizationInformationService


def render_existing_organization_info(org_id: str, parent_organizations: list):
    st.markdown("#### 📄 Existing Organization Information(s):")

    old_infos = OrganizationInformationService.find_many(
        filters=[OrganizationInformation.organization_id == org_id]
    )

    if not old_infos:
        return

    options = {
        f"{porg.name} ({porg.domain_url or 'N/A'})": porg.id
        for porg in parent_organizations
    }

    for info in old_infos:
        with st.container(border=True):
            st.markdown(f"**ID:** `{info.id}`")
            st.markdown(f"**Name:** `{info.name}`")
            st.markdown(f"**Preprocessed Name:** `{info.preprocessed_name}`")
            st.markdown(
                f"**Hospital/University:** {
                    '✅ Yes' if info.is_hospital_or_university else '❌ No'
                }"
            )

            dropdown_key = f"dropdown-parent-org-{info.id}"
            selected_org_id = st.selectbox(
                "Select Parent Organization to Attach",
                options.keys(),
                key=dropdown_key,
            )

            if st.button(
                "Attach",
                key=f"attach-btn-{info.id}",
                disabled=len(options.keys()) == 0,
            ):
                OrganizationInformationService.update_one(
                    id=info.id,
                    organization_id=options[selected_org_id],
                )
                st.success(
                    "✅ Organization Information reassigned successfully."
                )
                st.rerun()
