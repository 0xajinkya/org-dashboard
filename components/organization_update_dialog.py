import streamlit as st
from services.organization_information import OrganizationInformationService
from services.perplexity import PerplexityService
from models.organizations import OrganizationInformation, Organizations
from schemas.organization_enrichment import OrganizationEnrichment
from schemas.custom import OrganizationInformationInput
from services.organizations import OrganizationsService

def show_org_update_dialog(org: Organizations, organization_enrichment: OrganizationEnrichment):
    with st.container(border=True):
        st.markdown("### ✏️ Update Organization Info")
        st.text_input("Organization ID", value=org.id, disabled=True)
        dialog_prefix = f"org-update-dialog-{org.id}"
        name_key = f"{dialog_prefix}-name"
        domain_key = f"{dialog_prefix}-domain"
        updated_name = st.text_input("Organization Name", value=org.name, key=name_key)
        updated_domain = st.text_input("Domain URL", value=org.domain_url or "", key=domain_key)

        if st.button("Update Organization", key=f"btn-update-org-{org.id}"):
            try:
                OrganizationsService.update_one(
                    id=org.id,
                    name=updated_name,
                    domain_url=updated_domain
                )
                st.success("✅ Organization updated successfully!")
            except Exception as e:
                st.error(f"❌ Failed to update organization: {e}")

        st.markdown("---")

        fetch_key = f"org-info-fetched-{org.id}"
        perplexity_key = f"org-info-perplexity-{org.id}"
        perplexity_loading_key = f"org-info-perplexity-loading-{org.id}"

        col1, col2 = st.columns(2)

        with col1:
            if not st.session_state.get(fetch_key):
                if st.button("Fetch Related Organization Info", key=f"fetch-info-{org.id}"):
                    term = org.name
                    results = OrganizationInformationService.find_many(
                        filters=[
                            OrganizationInformation.name.match(term),
                            OrganizationInformation.preprocessed_name.match(term),
                            OrganizationInformation.name.ilike(f"%{term}%"),
                            OrganizationInformation.preprocessed_name.ilike(f"%{term}%"),
                        ],
                        fetch_all=True
                    )
                    
                    if results:
                        st.session_state[fetch_key] = [
                            {
                                "id": r.id,
                                "name": r.name,
                                "preprocessed_name": r.preprocessed_name,
                                "organization_id": r.organization_id,
                                "is_hospital_or_university": r.is_hospital_or_university,
                                "organization": r.organization
                            } for r in results
                        ]
                    else:
                        st.session_state[fetch_key] = "none"
                    st.rerun()
            elif st.session_state.get(fetch_key) == "none":
                st.button("No records found", key=f"no-records-{org.id}", disabled=True)
            elif not st.session_state.get(perplexity_key):
                if st.session_state.get(perplexity_loading_key):
                    st.button("Generating verdict...", key=f"generating-verdict-{org.id}", disabled=True)
                else:
                    if st.button("Generate Perplexity Verdict", key=f"generate-verdict-{org.id}"):
                        _generate_perplexity_verdict(organization_enrichment, fetch_key, perplexity_key, perplexity_loading_key)
            else:
                st.button("Update Organization Information", key=f"btn-update-info-{org.id}")

        with col2:
            st.button("❌ Close", key=f"close-dialog-{org.id}", on_click=lambda: _close_dialog())

        _display_fetched_info(org.id, fetch_key)
        
        _display_perplexity_verdict(org.id, perplexity_key)

def _generate_perplexity_verdict(
    organization_enrichment: OrganizationEnrichment, 
    fetch_key: str, 
    perplexity_key: str,
    perplexity_loading_key: str
):
    try:
        st.session_state[perplexity_loading_key] = True
        st.rerun()
        
        fetched_info = st.session_state.get(fetch_key, [])
        if not fetched_info or fetched_info == "none":
            st.error("No organization information available for verdict generation")
            st.session_state[perplexity_loading_key] = False
            return

        related_information = []
        for info in fetched_info:
            org_info_input = OrganizationInformationInput(
                organization_information_id=str(info["id"]),
                name=info.get("name"),
                preprocessed_name=info.get("preprocessed_name"),
                linked_organization=info.get('organization') or None
            )

            related_information.append(org_info_input)

        perplexity_service = PerplexityService()
        verdict, error = perplexity_service.find_match(organization_enrichment, related_information)
        
        if error:
            st.error(f"Error generating verdict: {str(error)}")
            st.session_state[perplexity_loading_key] = False
            return
        
        if verdict:
            st.session_state[perplexity_key] = {
                "organization_id": verdict.organization_id,
                "organization_name": verdict.organization_name,
                "domain_url": verdict.domain_url,
                "information_verdicts": [
                    {
                        "organization_information_id": iv.organization_information_id,
                        "belongs": iv.belongs,
                        "reasoning": iv.reasoning,
                    } for iv in verdict.information_verdicts
                ] if hasattr(verdict, 'information_verdicts') else [],
                "usage": verdict.usage
            }
            st.success("Perplexity verdict generated successfully!")
        else:
            st.error("Failed to generate verdict")
        
    except Exception as e:
        st.error(f"Error generating perplexity verdict: {str(e)}")
    finally:
        st.session_state[perplexity_loading_key] = False
        st.rerun()

def _display_fetched_info(org_id: str, fetch_key: str):
    fetched_info = st.session_state.get(fetch_key)
    if fetched_info and fetched_info != "none":
        st.markdown("#### 📋 Related Organization Information")
        with st.expander("View fetched information", expanded=False):
            for i, info in enumerate(fetched_info):
                st.markdown(f"**Record {i+1}:**")
                st.text(f"ID: {info['id']}")
                st.text(f"Name: {info['name']}")
                st.text(f"Preprocessed Name: {info['preprocessed_name']}")
                st.text(f"Organization ID: {info.get('organization_id', 'N/A')}")
                st.text(f"Is Hospital/University: {info.get('is_hospital_or_university', 'N/A')}")
                st.markdown("---")

def _display_perplexity_verdict(org_id: str, perplexity_key: str):
    verdict = st.session_state.get(perplexity_key)
    if verdict:
        st.markdown("#### 🎯 Perplexity Verdict")
        with st.expander("View verdict details", expanded=True):
            st.text(f"Organization ID: {verdict['organization_id']}")
            st.text(f"Organization Name: {verdict['organization_name']}")
            st.text(f"Domain URL: {verdict.get('domain_url', 'N/A')}")

            if verdict.get('information_verdicts'):
                st.markdown("**Information Verdicts:**")
                st.markdown(
                    "<div style='display: flex; overflow-x: auto; gap: 1rem;'>",
                    unsafe_allow_html=True
                )

                for i, iv in enumerate(verdict['information_verdicts']):
                    info_id = iv.get('organization_information_id')
                    info_record = OrganizationInformationService.get_one(info_id)

                    if not info_record:
                        st.warning(f"⚠️ Info record with ID {info_id} not found.")
                        continue

                    with st.container(border=True):
                        col_id = f"verdict-card-{org_id}-{info_id}"
                        st.markdown(f"**Verdict {i+1}:**")

                        st.text(f"Fetched Name: {info_record.name}")
                        st.text(f"Preprocessed: {info_record.preprocessed_name}")
                        st.text(f"Existing Org ID: {info_record.organization_id or 'None'}")
                        st.text(f"Hospital/University: {'Yes' if info_record.is_hospital_or_university else 'No'}")

                        st.text(f"Verdict - Belongs: {'✅ Yes' if iv.get('belongs') else '❌ No'}")
                        st.text_area("Reasoning", iv.get('reasoning', 'N/A'), height=100, disabled=True)

                        if st.button("Update Info Record", key=f"btn-update-info-{col_id}"):
                            try:
                                OrganizationInformationService.update_one(
                                    id=info_id,
                                    organization_id=verdict['organization_id'],
                                )
                                st.success("✅ Organization Information updated successfully!")
                            except Exception as e:
                                st.error(f"❌ Failed to update: {e}")

                st.markdown("</div>", unsafe_allow_html=True)

            if verdict.get('usage'):
                st.markdown("**API Usage:**")
                usage = verdict['usage']
                st.text(f"Prompt Tokens: {usage.get('prompt_tokens', 'N/A')}")
                st.text(f"Completion Tokens: {usage.get('completion_tokens', 'N/A')}")
                st.text(f"Total Tokens: {usage.get('total_tokens', 'N/A')}")

def _close_dialog():
    st.session_state.active_org_dialog = None