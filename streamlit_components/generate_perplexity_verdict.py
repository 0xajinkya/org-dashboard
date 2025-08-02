"""Generate Perplexity Verdict for an organization based on related information."""

import streamlit as st
from pydantic import BaseModel

from models.organizations import Organizations
from schemas.custom import LinkedOrganization, OrganizationInformationInput
from schemas.organization_enrichment import OrganizationEnrichment
from services.perplexity import PerplexityService
from utils.session_state_manager import SessionStateManager


def generate_perplexity_verdict(
    enrichment: OrganizationEnrichment,
    fetch_key: str,
    verdict_key: str,
    loading_key: str,
    org: Organizations,
):
    """
    Generates a verdict using the Perplexity service based on previously fetched organization information.

    Args:
        enrichment (OrganizationEnrichment): The enrichment payload used for context.
        fetch_key (str): Session state key to retrieve fetched organization information.
        verdict_key (str): Session state key to store the generated verdict.
        loading_key (str): Session state key to manage loading UI state.
        org (Organizations): The current organization entity under evaluation.
    """
    fetch_state = SessionStateManager(lambda: fetch_key)
    verdict_state = SessionStateManager(lambda: verdict_key)
    loading_state = SessionStateManager(lambda: loading_key)

    try:
        loading_state.add(True)

        fetched_info = fetch_state.get()
        if not fetched_info or fetched_info == "none":
            st.error(
                "No organization information available for verdict generation."
            )
            return

        inputs = []
        for info in fetched_info:
            linked = info.get("linked_organization")
            linked_org = (
                LinkedOrganization(**linked.model_dump())
                if isinstance(linked, BaseModel)
                else linked
            )

            inputs.append(
                OrganizationInformationInput(
                    organization_information_id=str(info["id"]),
                    name=info.get("name"),
                    preprocessed_name=info.get("preprocessed_name"),
                    linked_organization=linked_org,
                )
            )

        verdict, error = PerplexityService().find_match(
            enrichment, inputs, org
        )

        if error:
            st.error(f"Error generating verdict: {error}")
        elif verdict:
            verdict_state.add(_structure_verdict(verdict))
            st.success("Perplexity verdict generated successfully!")
        else:
            st.error("Verdict generation returned no result.")

    except Exception as e:
        st.error(f"Unexpected error during verdict generation: {e}")
    finally:
        loading_state.add(False)
        st.rerun()


def _structure_verdict(verdict):
    """
    Transforms the raw PerplexityVerdict object into a streamlined dict structure
    suitable for serialization and display.

    Args:
        verdict: A complex Pydantic model representing verdict metadata.

    Returns:
        dict: Simplified verdict suitable for session storage.
    """
    return {
        "organization_id": verdict.matches.organization_id,
        "organization_name": verdict.matches.organization_name,
        "domain_url": verdict.matches.domain_url,
        "information_verdicts": [
            {
                "organization_information_id": iv.organization_information_id,
                "type_of_match": iv.type_of_match,
                "reasoning": iv.reasoning,
                "extraInfo": iv.extraInfo,
            }
            for iv in getattr(verdict.matches, "information_verdicts", [])
        ],
        "usage": verdict.usage,
    }
