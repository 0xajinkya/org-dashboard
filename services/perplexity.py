"""Modules used."""

import json
import os
from typing import List

import requests

from models.organizations import Organizations
from schemas.custom import (
    OrganizationInformationInput,
    OrganizationInformationJsonSchema,
    OrganizationInformationVerdict,
    OrganizationVerdict,
)
from schemas.organization_enrichment import (
    ExtraInfo,
    OrganizationEnrichment,
    OrganizationEnrichmentJsonSchema,
    Usage,
)


class PerplexityService:
    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or os.getenv("PERPLEXITY_API_KEY")
        self.api_url = "https://api.perplexity.ai/chat/completions"
        self.headers = {"Authorization": f"Bearer {self.api_key}"}

    def build_enrich_prompt(self, company_name: str) -> str:
        return (
            f"You are given the name of a company: '{company_name}'. "
            "Return a JSON object with the following strictly defined keys:\n\n"
            "1. `official_name`: The most likely official or registered name of the company. "
            "If no suitable name can be found, return `null`.\n\n"
            "2. `status`: One of the following string literals:\n"
            '   - "standalone": The company operates independently.\n'
            '   - "acquired": The company was acquired by another entity.\n'
            '   - "subsidiary": The company is a controlled entity of a parent organization.\n\n'
            "3. `domain_url`: The valid domain URL of the company in bare format "
            "(e.g., 'https://verbio.de'). If not confidently determinable, return `null`.\n\n"
            "4. `extra_info`: An object with details about the acquiring or parent organization if the status is 'acquired' or 'subsidiary'. "
            "Otherwise, set this to `null`.\n"
            "   - `name`: Name of the parent or acquiring company. Can be null if unavailable.\n"
            "   - `domain_url`: Valid domain URL of the parent/acquirer. Can be null if unavailable.\n\n"
            "Return the response in **strict JSON** format. Do not include any additional commentary, explanation, or markdown formatting. "
            "Ensure that field values match the following schema types:\n"
            "- `official_name`: string or null\n"
            "- `status`: one of 'standalone', 'acquired', or 'subsidiary'\n"
            "- `domain_url`: valid URL or null\n"
            "- `extra_info`: object or null with the following structure:\n"
            "    - `name`: string or null\n"
            "    - `domain_url`: valid URL or null\n"
            "Example valid output:\n"
            "{\n"
            '  "official_name": "Verve Therapeutics, Inc.",\n'
            '  "status": "standalone",\n'
            '  "domain_url": "https://vervetx.com",\n'
            '  "extra_info": null,\n'
            "}"
        )

    def enrich_organization(
        self, company_name: str
    ) -> tuple[OrganizationEnrichment | None, Exception | None]:
        prompt = self.build_enrich_prompt(company_name)
        payload = {
            "model": "sonar",
            "messages": [
                {
                    "role": "system",
                    "content": "Be concise and use reliable sources.",
                },
                {"role": "user", "content": (prompt)},
            ],
            "response_format": {
                "type": "json_schema",
                "json_schema": {
                    "schema": OrganizationEnrichmentJsonSchema.model_json_schema()
                },
            },
        }
        try:
            response = requests.post(
                self.api_url, headers=self.headers, json=payload, timeout=600
            )
            response.raise_for_status()
            response_json = response.json()
            enrichment_response = json.loads(
                response_json["choices"][0]["message"]["content"]
            )
            # Parse extra_info safely
            extra_info_raw = enrichment_response.get("extra_info")
            extra_info_typed = (
                None
                if extra_info_raw is None
                else ExtraInfo.model_validate(extra_info_raw)
            )

            # Inject the typed extra_info back into the response dict
            enrichment_response["extra_info"] = extra_info_typed

            # Validate full enrichment content
            enrichment_content_typed = (
                OrganizationEnrichmentJsonSchema.model_validate(
                    enrichment_response
                )
            )

            # Extract citations and usage
            citations = response_json.get("citations", [])
            usage_raw = response_json.get("usage", {})

            usage_clean = {
                k: v
                for k, v in usage_raw.items()
                if k in {"prompt_tokens", "completion_tokens", "total_tokens"}
            }
            usage = Usage.model_validate(usage_clean)

            # Final enrichment structure
            enrichment = OrganizationEnrichment(
                enrichment=enrichment_content_typed,
                citations=citations,
                usage=usage,
            )

            return enrichment, None
        except Exception as e:
            return None, e

    def build_match_prompt(
        self,
        organization: OrganizationEnrichment,
        related_information: List[OrganizationInformationInput],
        org: Organizations,
    ) -> str:
        domain_part = (
            f" and its domain is '{organization['enrichment']['domain_url'] or org.domain_url}'"
            if organization["enrichment"]["domain_url"] or org.domain_url
            else ""
        )
        return (
            "You are given the following information:\n\n"
            f"1. A target organization with the name '{organization['enrichment']['official_name'] or org.name}'{domain_part}.\n"
            f"   Its unique ID is '{org.id}'.\n\n"
            "2. A list of organization information records. Each record includes:\n"
            "- organization_information_id (UUID)\n"
            "- name and preprocessed_name\n"
            "- linked_organization (if any), which includes its ID, name, and domain_url\n\n"
            f"{[info.model_dump() for info in related_information]}\n\n"
            "Your task is to analyze whether each organization information record corresponds to the target organization.\n"
            "For each record, determine the appropriate classification based on semantic similarity, domain overlap, and contextual alignment.\n\n"
            "Use the following classification types:\n"
            "• `same` – The information pertains to the same organization.\n"
            "• `acquired` – The information pertains to an organization that has been acquired by the target organization, or vice versa. In this case, include `extraInfo` describing the acquiring or acquired entity.\n"
            "• `no match` – The information is unrelated to the target organization.\n\n"
            "Respond **strictly in valid JSON** according to the following schema:\n\n"
            "{\n"
            '  "organization_id": "<UUID of the target organization>",\n'
            '  "organization_name": "<Name of the target organization>",\n'
            '  "domain_url": "<Domain URL of the target organization or null>",\n'
            '  "information_verdicts": [\n'
            "    {\n"
            '      "organization_information_id": "<UUID>",\n'
            '      "type_of_match": "same" | "acquired" | "no match",\n'
            '      "reasoning": "<concise explanation of the classification>",\n'
            '      "extraInfo": {\n'
            '        "name": "<Name of the related/acquiring organization>",\n'
            '        "domain_url": "<Domain of the related/acquiring organization>"\n'
            "      } | null\n"
            "    },\n"
            "    ...\n"
            "  ]\n"
            "}\n\n"
            "Ensure that the output JSON **conforms exactly** to this structure without additional commentary or deviation."
        )

    def find_match(
        self,
        organization: OrganizationEnrichment,
        related_information: List[OrganizationInformationInput],
        org: Organizations,
    ) -> tuple[OrganizationVerdict | None, Exception | None]:
        try:
            prompt = self.build_match_prompt(
                organization, related_information, org
            )
            payload = {
                "model": "sonar",
                "messages": [
                    {
                        "role": "system",
                        "content": "Be concise and use reliable sources.",
                    },
                    {"role": "user", "content": prompt},
                ],
                "response_format": {
                    "type": "json_schema",
                    "json_schema": {
                        "schema": OrganizationInformationJsonSchema.model_json_schema()
                    },
                },
            }

            # ➤ Perform API call
            response = requests.post(
                self.api_url, headers=self.headers, json=payload, timeout=60
            )
            response.raise_for_status()

            # ➤ Extract content and parse JSON
            response_json = response.json()
            content_raw = response_json["choices"][0]["message"]["content"]
            verdict_response = json.loads(content_raw)

            # ➤ Extract usage data
            citations = response_json.get("citations", [])
            usage_raw = response_json.get("usage", {})
            usage_clean = {
                k: v
                for k, v in usage_raw.items()
                if k in {"prompt_tokens", "completion_tokens", "total_tokens"}
            }
            usage = Usage.model_validate(usage_clean)

            # ➤ Construct verdicts
            information_verdicts_typed = [
                OrganizationInformationVerdict(
                    organization_information_id=str(
                        info["organization_information_id"]
                    ),
                    type_of_match=info["type_of_match"],
                    reasoning=info["reasoning"],
                    extraInfo=(
                        ExtraInfo(
                            name=info["extraInfo"]["name"],
                            domain_url=info["extraInfo"]["domain_url"],
                        )
                        if info.get("extraInfo")
                        else None
                    ),
                )
                for info in verdict_response["information_verdicts"]
            ]

            # ➤ Final model constructions
            matches = OrganizationInformationJsonSchema(
                organization_id=str(verdict_response["organization_id"]),
                organization_name=verdict_response["organization_name"],
                domain_url=verdict_response.get("domain_url"),
                information_verdicts=information_verdicts_typed,
            )

            verdict = OrganizationVerdict(
                citations=citations,
                usage=usage,
                matches=matches,
            )

            return verdict, None

        except Exception as e:
            return None, e
