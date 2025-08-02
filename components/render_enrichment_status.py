import streamlit as st

from schemas.organization_enrichment import OrganizationEnrichment


def render_enrichment_status(result: OrganizationEnrichment | None):
    if not result:
        return

    if "error" in result:
        st.error(f"❌ {result['error']}")
    else:
        st.success("✅ Enrichment Complete")
        st.json(result)
