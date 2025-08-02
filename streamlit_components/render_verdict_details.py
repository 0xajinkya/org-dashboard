import streamlit as st

from services.organization_information import OrganizationInformationService


def render_verdict_details(
    org_id: str, info_id: str, matched_verdict: dict, full_verdict: dict
):
    st.markdown("---")
    st.text(f"Match Type: {matched_verdict['type_of_match'].capitalize()}")

    st.text_area(
        "Reasoning",
        matched_verdict["reasoning"] or "N/A",
        height=100,
        disabled=True,
        key=f"textarea-reasoning-{org_id}-{info_id}",
    )

    if matched_verdict["type_of_match"] == "same":
        if st.button(
            "Update Info Record", key=f"btn-update-info-{org_id}-{info_id}"
        ):
            try:
                OrganizationInformationService.update_one(
                    id=info_id, organization_id=full_verdict["organization_id"]
                )
                st.success("✅ Organization Information updated successfully!")
            except Exception as e:
                st.error(f"❌ Failed to update: {e}")
