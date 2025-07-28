from pydantic import BaseModel, AnyHttpUrl
from typing import List, Optional


class Usage(BaseModel):
    prompt_tokens: Optional[int]
    completion_tokens: Optional[int]
    total_tokens: Optional[int]


class OrganizationEnrichment(BaseModel):
    official_company_name: Optional[str]
    domain_url: Optional[AnyHttpUrl]
    citations: List[AnyHttpUrl]
    usage: Optional[Usage]

class OrganizationEnrichmentJsonSchema(BaseModel):
    official_company_name: Optional[str]