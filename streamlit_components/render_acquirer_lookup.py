import streamlit as st
from sqlalchemy import or_

from components.add_organization import add_organization
from components.organization_card import organization_card
from models.organizations import Organizations
from services.organizations import OrganizationsService
from utils.session_state_manager import SessionStateManager


def render_acquirer_lookup(
    info_id: str,
    info: dict,
    matched_verdict: dict,
    state_key: str,
):
    """
    Renders an interface to search for and optionally add a parent/acquirer organization
    based on the provided organization information. Utilizes session state abstraction
    for UI control and dynamic rerendering.
    """
    dialog_state = SessionStateManager(lambda _: state_key)
    new_org_key = f"newly_added_acquirer_{info_id}"
    new_org_state = SessionStateManager(lambda _: new_org_key)

    if not dialog_state.get():
        if st.button("Look for acquirer", key=f"lookup-btn-{info_id}"):
            dialog_state.add(True)
            st.rerun()
        return

    try:
        # --- Perform fuzzy lookup based on the 'name' field ---
        matches = OrganizationsService.find_many(
            filters=[
                or_(
                    Organizations.name.match(info["name"]),
                    Organizations.name.ilike(f"%{info['name']}%"),
                    Organizations.name.like(f"{info['name']}%"),
                )
            ]
        )

        # --- Inject newly added org into results if not already present ---
        new_org = new_org_state.get()
        if new_org and new_org not in matches:
            matches.append(new_org)

        # --- Display matched results ---
        st.markdown("#### 🏢 Matching Acquirers")
        if matches:
            for org in matches:
                organization_card(
                    org,
                    [matched_verdict.get("organization_information_id")],
                )
        else:
            st.info("No matching acquirer found.")

        # --- Manual Addition Flow ---
        st.markdown("#### ➕ Add a New Organization")
        if st.button("Add a new organization", key=f"add-org-{info_id}"):
            extra_info = matched_verdict.get("extra_info", {})
            new_org = add_organization(
                name=extra_info.get("name"),
                domain_url=str(extra_info.get("domain_url", "")),
                organization_information_id=matched_verdict.get(
                    "organization_information_id"
                ),
            )
            if new_org:
                new_org_state.add(new_org)
                st.success("✅ New organization created and added.")
                st.rerun()

        # --- Close Button ---
        if st.button("❌ Close", key=f"close-lookup-{info_id}"):
            dialog_state.add(False)
            new_org_state.remove()
            st.rerun()

    except Exception as e:
        st.error(f"❌ Failed to complete acquirer lookup: {e}")
