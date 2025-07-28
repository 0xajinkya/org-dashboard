import streamlit as st
import streamlit_shadcn_ui as ui
from services.perplexity import PerplexityService
from services.organizations import OrganizationsService
from models.organizations import Organizations;

perplexity_service = PerplexityService()

def render_organization_item(org: Organizations):
    with st.container(border=True):
        st.markdown(f"#### #{org.id[:5]}")
        st.markdown(f"**{org.name}**")
        st.markdown(f"`{org.domain_url or 'No domain'}`")

        enrichment_results = st.session_state.enrichment_results
        current_enrichment_results = st.session_state.current_enrichment_results[org.id]
        if org.id in enrichment_results:
            result = enrichment_results[org.id]
            if "error" in result:
                st.error(f"❌ {result['error']}")
            else:
                st.success("✅ Enrichment Complete")
                st.json(result)

        btn_col1, btn_col2 = st.columns([1, 1])

        with btn_col1:
            if org.id not in enrichment_results:
                if ui.button(
                    text="Run Enrichment",
                    key=f"fetch-{org.id}",
                    variant="default",
                    full_width=True
                ):
                    _handle_enrichment_trigger(org.id)
            else:
                if ui.button(
                    text="Update To DB",
                    key=f"update-db-{org.id}",
                    variant="default",
                    full_width=True
                ):
                    enriched_data = enrichment_results[org.id]
                    OrganizationsService.update_one(
                        id=org.id,
                        name=enriched_data["official_company_name"],
                        domain_url=str(enriched_data["domain_url"])
                    )
                    st.success("✅ Organization info updated in the database.")
                    st.rerun()

        with btn_col2:
            if ui.button(
                text="Update Organization Info",
                key=f"show-dialog-{org.id}",
                variant="secondary",
                full_width=True
            ):
                st.session_state.active_org_dialog = org.id

        if st.session_state.active_org_dialog == org.id:
            from components.organization_update_dialog import show_org_update_dialog
            show_org_update_dialog(org, current_enrichment_results)

def _handle_enrichment_trigger(org_id):
    st.session_state.triggered_enrichment_id = org_id
    orgs = st.session_state.cached_pages[st.session_state.page]
    org = next((o for o in orgs if o.id == org_id), None)
    if org:
        with st.spinner(f"Enriching: {org.name}"):
            enrichment, error = perplexity_service.enrich_organization(org.name)
            if enrichment:
                st.session_state.enrichment_results[org.id] = enrichment.model_dump()
            else:
                st.session_state.enrichment_results[org.id] = {"error": str(error)}
    st.session_state.triggered_enrichment_id = None
    st.rerun()
