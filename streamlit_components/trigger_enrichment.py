from typing import List

import streamlit as st

from models.organizations import Organizations
from services.perplexity import PerplexityService
from utils.session_state_manager import SessionStateManager

# Session state managers
triggered_enrichment_state = SessionStateManager(
    lambda: "triggered_enrichment_id"
)
page_state = SessionStateManager(lambda: "page")
cached_pages_state = SessionStateManager(lambda: "cached_pages")
enrichment_results_state = SessionStateManager(lambda: "enrichment_results")

perplexity_service = PerplexityService()


def trigger_enrichment(org_id: str):
    triggered_enrichment_state.add(org_id)

    current_page = page_state.get()
    cached_pages = cached_pages_state.get(default={})
    orgs: List[Organizations] = cached_pages.get(current_page, [])

    org = next((o for o in orgs if o.id == org_id), None)

    if org:
        with st.spinner(f"Enriching: {org.name}"):
            enrichment, error = perplexity_service.enrich_organization(
                org.name
            )

            enrichment_results = enrichment_results_state.get(default={})
            if enrichment:
                enrichment_results[org.id] = enrichment.model_dump()
            else:
                enrichment_results[org.id] = {"error": str(error)}
            enrichment_results_state.update(enrichment_results)

    triggered_enrichment_state.add(None)
