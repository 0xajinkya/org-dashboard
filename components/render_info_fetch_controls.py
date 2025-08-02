"""Render controls for fetching and generating perplexity verdicts."""

import streamlit as st
from sqlalchemy import or_

from models.organizations import OrganizationInformation, Organizations
from schemas.custom import LinkedOrganization
from schemas.organization_enrichment import OrganizationEnrichment
from services.organization_information import OrganizationInformationService
from streamlit_components.generate_perplexity_verdict import (
    generate_perplexity_verdict,
)
from utils.session_state_manager import SessionStateManager


def render_info_fetch_controls(
    org: Organizations, enrichment: OrganizationEnrichment
):
    fetch_state = SessionStateManager(lambda oid: f"org-info-fetched-{oid}")
    verdict_state = SessionStateManager(
        lambda oid: f"org-info-perplexity-{oid}"
    )
    loading_state = SessionStateManager(
        lambda oid: f"org-info-perplexity-loading-{oid}"
    )
    dialog_state = SessionStateManager(lambda: "active_org_dialog")

    col1, col2 = st.columns(2)

    with col1:
        if _should_fetch_info(fetch_state, org.id) and enrichment:
            _fetch_related_info(org, fetch_state)
        elif fetch_state.get(org.id) is None:
            st.button(
                "Enrichment not created",
                key=f"enrichment-not-created-{org.id}",
                disabled=True,
            )
        elif fetch_state.get(org.id) == "none":
            st.button(
                "No records found", key=f"no-records-{org.id}", disabled=True
            )
        elif not verdict_state.get(org.id):
            render_verdict_button(
                org,
                enrichment,
                fetch_state,
                verdict_state,
                loading_state,
            )
        else:
            st.button(
                "Perplexity Verdict Generated",
                key=f"verdict-ready-{org.id}",
                disabled=True,
            )

    with col2:
        st.button(
            "❌ Close",
            key=f"close-dialog-{org.id}",
            on_click=lambda: dialog_state.add(None),
        )


def _should_fetch_info(fetch_state: SessionStateManager, org_id: str) -> bool:
    return not fetch_state.get(org_id)


def _fetch_related_info(org: Organizations, fetch_state: SessionStateManager):
    if st.button(
        "Fetch Related Organization Info", key=f"fetch-info-{org.id}"
    ):
        term = org.name
        results = OrganizationInformationService.find_many(
            filters=[
                or_(
                    OrganizationInformation.name.match(term),
                    OrganizationInformation.preprocessed_name.match(term),
                    OrganizationInformation.name.ilike(f"%{term}%"),
                    OrganizationInformation.preprocessed_name.ilike(
                        f"%{term}%"
                    ),
                )
            ],
            fetch_all=True,
        )
        payload = [format_org_info(r) for r in results] if results else "none"
        fetch_state.add(payload, org.id)
        st.rerun()


def render_verdict_button(
    org: Organizations,
    enrichment: OrganizationEnrichment,
    fetch_state: SessionStateManager,
    verdict_state: SessionStateManager,
    loading_state: SessionStateManager,
):
    if loading_state.get(org.id):
        st.button(
            "Generating verdict...",
            key=f"generating-verdict-{org.id}",
            disabled=True,
        )
    elif st.button(
        "Generate Perplexity Verdict", key=f"generate-verdict-{org.id}"
    ):
        generate_perplexity_verdict(
            enrichment,
            fetch_state.key_builder(org.id),
            verdict_state.key_builder(org.id),
            loading_state.key_builder(org.id),
            org,
        )


def format_org_info(r: OrganizationInformation) -> dict:
    return {
        "id": r.id,
        "name": r.name,
        "preprocessed_name": r.preprocessed_name,
        "organization_id": r.organization_id,
        "is_hospital_or_university": r.is_hospital_or_university,
        "linked_organization": (
            LinkedOrganization(
                id=str(r.organization.id),
                name=r.organization.name,
                domain_url=r.organization.domain_url,
            )
            if r.organization
            else None
        ),
    }
