from typing import List, Literal, Optional

from pydantic import AnyHttpUrl, BaseModel


class Usage(BaseModel):
    prompt_tokens: Optional[int]
    completion_tokens: Optional[int]
    total_tokens: Optional[int]


class ExtraInfo(BaseModel):
    name: Optional[str]
    domain_url: Optional[AnyHttpUrl]


class OrganizationEnrichmentJsonSchema(BaseModel):
    official_name: Optional[str]
    status: Literal["standalone", "acquired", "subsidiary"]
    domain_url: Optional[AnyHttpUrl]
    extra_info: Optional[ExtraInfo]


class OrganizationEnrichment(BaseModel):
    enrichment: OrganizationEnrichmentJsonSchema
    citations: List[AnyHttpUrl]
    usage: Optional[Usage]
