"""Organization Information Card Component."""

import streamlit as st

from components.render_basic_info_verdict import render_basic_info_verdict
from streamlit_components.render_acquirer_lookup import render_acquirer_lookup
from streamlit_components.render_verdict_details import render_verdict_details


def organization_information_card(
    org_id: str,
    info: dict,
    matched_verdict: dict | None,
    full_verdict: dict | None,
):
    info_id = str(info["id"])
    state_key = f"acquirer_lookup_{info_id}"

    extra_info = matched_verdict.get("extraInfo") if matched_verdict else None
    with st.container(border=True):
        render_basic_info_verdict(info_id, info)
        if matched_verdict and full_verdict:
            render_verdict_details(
                org_id, info_id, matched_verdict, full_verdict
            )
            if (
                matched_verdict["type_of_match"] in {"acquired"}
                and extra_info is not None
            ):
                render_acquirer_lookup(
                    info_id, extra_info, matched_verdict, state_key
                )
