from models.organizations import OrganizationInformation, Organizations
from typing import TypedDict, List, Optional
from pydantic import BaseModel

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
    belongs: bool
    reasoning: str

class OrganizationVerdict(BaseModel):
    organization_id: str
    organization_name: str
    domain_url: Optional[str] = None
    information_verdicts: List[OrganizationInformationVerdict]
    usage: Optional[dict] = None
