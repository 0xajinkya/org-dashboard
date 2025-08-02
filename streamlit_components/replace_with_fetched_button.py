import streamlit as st

from services.organizations import OrganizationsService


def render_replace_with_fetched_button(org_id: str, enrichment: dict):
    if st.button(
        "Replace With Fetched Content",
        key=f"enrichment-{org_id}",
        use_container_width=True,
        type="primary",
    ):
        OrganizationsService.update_one(
            id=org_id,
            name=enrichment["official_name"],
            domain_url=str(enrichment["domain_url"]),
        )
        st.success("✅ Organization info updated in the database.")
        st.rerun()
