import os
import requests
from schemas.organization_enrichment import OrganizationEnrichment, OrganizationEnrichmentJsonSchema, Usage
import json
from typing import List
from schemas.custom import OrganizationInformationInput, OrganizationVerdict

class PerplexityService:
    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or os.getenv("PERPLEXITY_API_KEY")
        self.api_url = "https://api.perplexity.ai/chat/completions"
        self.headers = {"Authorization": f"Bearer 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"}
    
    def build_enrich_prompt(self, company_name: str) -> str:
        return (
            f"You are given the name of a company: '{company_name}'. "
            "Return a JSON object with the following strictly defined keys:\n\n"
            "1. `official_company_name`: The most likely official or registered name of the company. "
            "If no suitable name can be found, return `null`.\n\n"
            "2. `domain_url`: A valid company domain URL in bare format (e.g., 'https://verbio.de'), "
            "not a subpage or social media profile. If the domain cannot be confidently determined, return `null`.\n\n"
            "Return the response in **strict JSON** format. Do not include any additional commentary, explanation, or markdown formatting. "
            "Ensure that field values match the following schema types:\n"
            "- `official_company_name`: string or null\n"
            "- `domain_url`: valid URL or null\n"
            "- `citations`: array of valid URLs (AnyHttpUrl)\n\n"
            "Example valid output:\n"
            "{\n"
            '  "official_company_name": "Verve Therapeutics, Inc.",\n'
            '  "domain_url": "https://vervetx.com"\n'
            "}"
        )

    def enrich_organization(self, company_name: str) -> tuple[OrganizationEnrichment | None, Exception | None]:
        prompt = self.build_enrich_prompt(company_name)
        payload = {
            "model": "sonar",
            "messages": [
                {"role": "system", "content": "Be concise and use reliable sources."},
                {"role": "user", "content": (prompt)},
            ],
            "response_format": {
                "type": "json_schema",
                "json_schema": {
                    "schema": OrganizationEnrichmentJsonSchema.model_json_schema()
                }
            }
        }

        try:
            response = requests.post(self.api_url, headers=self.headers, json=payload)
            response.raise_for_status()
            response_json = response.json()

            # Extract fields
            json_content_raw = response_json["choices"][0]["message"]["content"]
            citations = response_json.get("citations", [])
            usage_raw = response_json.get("usage", {})

            # Remove `search_context_size` if present
            usage_clean = {
                k: v for k, v in usage_raw.items()
                if k in {"prompt_tokens", "completion_tokens", "total_tokens"}
            }

            usage = Usage.model_validate(usage_clean)

            # Merge and parse content JSON
            content_data = json.loads(json_content_raw)
            content_data["citations"] = citations
            content_data["usage"] = usage
            print(content_data)
            enrichment = OrganizationEnrichment.model_validate(content_data)
            return enrichment, None

        except Exception as e:
            return None, e
    
    def build_match_prompt(
        self,
        organization: OrganizationEnrichment,
        related_information: List[OrganizationInformationInput]
    ) -> str:
        domain_part = f" and its domain is '{organization.domain_url}'" if organization.domain_url else ""

        return (
            "You are given:\n\n"
            f"1. A new organization with the name '{organization.official_company_name}'{domain_part}.\n"
            f"   Its unique ID is '{organization.id}'.\n\n"
            "2. A list of organization information records. Each record includes:\n"
            "- Its unique identifier (organization_information_id)\n"
            "- Name and preprocessed name\n"
            "- A linked organization (if any), which includes its ID, name, and domain_url\n\n"
            f"{[info.model_dump() for info in related_information]}\n\n"
            "Your task is to determine whether each organization information record belongs to the given organization.\n"
            "You must return an array of decisions.\n\n"
            "Instructions:\n"
            "- Compare the names and preprocessed names against the organization's name.\n"
            "- Consider whether the linked organization (if any) is likely the same as the current organization.\n"
            "- Rely on string similarity, semantic closeness, and context clues from domains and names.\n"
            "- Return a boolean `true` if the information belongs to the given organization, otherwise `false`.\n"
            "- Provide a concise justification for each decision.\n\n"
            "Respond in the following JSON format:\n"
            "{\n"
            '  "organization_id": "<id>",\n'
            '  "organization_name": "<name>",\n'
            '  "domain_url": "<domain_url or null>",\n'
            '  "information_verdicts": [\n'
            '    {\n'
            '      "organization_information_id": "<id>",\n'
            '      "belongs": true | false,\n'
            '      "reasoning": "<concise explanation>"\n'
            '    },\n'
            '    ...\n'
            '  ]\n'
            "}"
        )

    def find_match(
        self,
        organization: OrganizationEnrichment,
        related_information: List[OrganizationInformationInput]
    ) -> tuple[OrganizationVerdict | None, Exception | None]:
        prompt = self.build_match_prompt(organization, related_information)

        payload = {
            "model": "sonar",
            "messages": [
                {"role": "system", "content": "Be concise and use reliable sources."},
                {"role": "user", "content": prompt},
            ],
            "response_format": {
                "type": "json_schema",
                "json_schema": {
                    "schema": OrganizationVerdict.model_json_schema()
                }
            }
        }

        try:
            response = requests.post(self.api_url, headers=self.headers, json=payload)
            response.raise_for_status()
            response_json = response.json()

            json_content_raw = response_json["choices"][0]["message"]["content"]
            json_content = json.loads(json_content_raw)

            usage_raw = response_json.get("usage", {})
            usage_clean = {
                k: v for k, v in usage_raw.items()
                if k in {"prompt_tokens", "completion_tokens", "total_tokens"}
            }

            json_content["usage"] = Usage.model_validate(usage_clean)

            return OrganizationVerdict.model_validate(json_content), None

        except Exception as e:
            return None, e
