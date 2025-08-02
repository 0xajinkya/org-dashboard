from typing import List, Literal, Optional, TypedDict

from pydantic import AnyHttpUrl, BaseModel

from models.organizations import OrganizationInformation, Organizations
from schemas.organization_enrichment import ExtraInfo, Usage


class OrganizationResult(TypedDict):
    organization: Optional[Organizations]
    organization_information: Optional[List[OrganizationInformation]]


class LinkedOrganization(BaseModel):
    id: str
    name: Optional[str] = None
    domain_url: Optional[str] = None


class OrganizationInformationInput(BaseModel):
    organization_information_id: str
    name: Optional[str] = None
    preprocessed_name: Optional[str] = None
    linked_organization: Optional[LinkedOrganization] = None


class OrganizationInformationVerdict(BaseModel):
    organization_information_id: str
    type_of_match: Literal["same", "acquired", "no match"]
    reasoning: str
    extraInfo: Optional[ExtraInfo]


class OrganizationInformationJsonSchema(BaseModel):
    organization_id: str
    organization_name: str
    domain_url: Optional[str] = None
    information_verdicts: List[OrganizationInformationVerdict]


class OrganizationVerdict(BaseModel):
    matches: OrganizationInformationJsonSchema
    usage: Optional[Usage]
    citations: List[AnyHttpUrl] = []
