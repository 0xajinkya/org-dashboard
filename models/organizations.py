from typing import Any, List, Optional

from sqlalchemy import Boolean, DateTime, ForeignKeyConstraint, Identity, Index, Integer, PrimaryKeyConstraint, String, Text, UniqueConstraint, text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from custom.schemas.vector import Vector
import datetime

class Base(DeclarativeBase):
    pass


class Organizations(Base):
    __tablename__ = 'organizations'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='organizations_pkey'),
        Index('idx_organizations_domain', 'domain_url'),
        Index('idx_organizations_name', 'name'),
        {'schema': 'organization'}
    )

    id: Mapped[str] = mapped_column(Text, primary_key=True)
    name: Mapped[str] = mapped_column(Text)
    domain_url: Mapped[Optional[str]] = mapped_column(Text)

    organization_knowledge: Mapped[List['OrganizationKnowledge']] = relationship('OrganizationKnowledge', back_populates='organization')

class OrganizationInformation(Base):
    __tablename__ = 'organization_information'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='organization_information_pkey'),
        UniqueConstraint('name', name='organization_information_name_key'),
        Index('idx_name_trgm', 'name'),
        {'schema': 'organization'}
    )

    id: Mapped[int] = mapped_column(Integer, Identity(...), primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    preprocessed_name: Mapped[str] = mapped_column(String(255))
    organization_id: Mapped[Optional[int]] = mapped_column(Integer)
    is_hospital_or_university: Mapped[Optional[bool]] = mapped_column(Boolean)

    organization: Mapped[Optional[Organizations]] = relationship(
        "Organizations",
        primaryjoin="foreign(OrganizationInformation.organization_id) == Organizations.id",
        lazy="selectin"
    )

class OrganizationKnowledge(Base):
    __tablename__ = 'organization_knowledge'
    __table_args__ = (
        ForeignKeyConstraint(['organization_id'], ['organization.organizations.id'], name='fk_org_knowledge_org_id'),
        PrimaryKeyConstraint('id', name='organization_knowledge_pkey'),
        UniqueConstraint('organization_name', 'knowledge_type', 'details_hash', name='uk_org_knowledge_content'),
        Index('idx_org_knowledge_date', 'knowledge_date'),
        Index('idx_org_knowledge_knowledge_type', 'knowledge_type'),
        Index('idx_org_knowledge_org_id', 'organization_id'),
        Index('idx_org_knowledge_org_name', 'organization_name'),
        Index('idx_org_knowledge_org_type', 'organization_id', 'source_data_type'),
        Index('idx_org_knowledge_typesense_meta', 'knowledge_type', 'typesense_original_id'),
        Index('idx_org_knowledge_unique_details', 'organization_name', 'knowledge_type', unique=True),
        Index('organization_knowledge_typesense_embedding_idx', 'typesense_embedding'),
        {'schema': 'organization'}
    )

    id: Mapped[str] = mapped_column(Text, primary_key=True)
    organization_name: Mapped[str] = mapped_column(Text)
    knowledge_type: Mapped[str] = mapped_column(Text)
    organization_id: Mapped[Optional[str]] = mapped_column(Text)
    source_data_type: Mapped[Optional[str]] = mapped_column(Text)
    details: Mapped[Optional[str]] = mapped_column(Text)
    knowledge_date: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    sourcelink: Mapped[Optional[str]] = mapped_column(Text)
    description: Mapped[Optional[str]] = mapped_column(Text)
    org_type: Mapped[Optional[str]] = mapped_column(Text)
    product_categories: Mapped[Optional[str]] = mapped_column(Text)
    indication_categories: Mapped[Optional[str]] = mapped_column(Text)
    webpage: Mapped[Optional[str]] = mapped_column(Text)
    webpage_category: Mapped[Optional[str]] = mapped_column(Text)
    personnel_name: Mapped[Optional[str]] = mapped_column(Text)
    personnel_role: Mapped[Optional[str]] = mapped_column(Text)
    personnel_contact: Mapped[Optional[str]] = mapped_column(Text)
    country: Mapped[Optional[str]] = mapped_column(Text)
    city: Mapped[Optional[str]] = mapped_column(Text)
    state: Mapped[Optional[str]] = mapped_column(Text)
    address: Mapped[Optional[str]] = mapped_column(Text)
    location_label: Mapped[Optional[str]] = mapped_column(Text)
    product_name: Mapped[Optional[str]] = mapped_column(Text)
    product_moa: Mapped[Optional[str]] = mapped_column(Text)
    product_category: Mapped[Optional[str]] = mapped_column(Text)
    product_indications: Mapped[Optional[str]] = mapped_column(Text)
    product_modality: Mapped[Optional[str]] = mapped_column(Text)
    product_phase: Mapped[Optional[str]] = mapped_column(Text)
    product_status: Mapped[Optional[str]] = mapped_column(Text)
    manufacturing_facility_location: Mapped[Optional[str]] = mapped_column(Text)
    manufacturing_capability: Mapped[Optional[str]] = mapped_column(Text)
    manufacturing_capacity: Mapped[Optional[str]] = mapped_column(Text)
    partner_name: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('now()'))
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('now()'))
    details_hash: Mapped[Optional[str]] = mapped_column(String(64))
    typesense_embedding: Mapped[Optional[Vector]] = mapped_column(Vector)
    typesense_original_id: Mapped[Optional[str]] = mapped_column(Text)

    organization: Mapped[Optional['Organizations']] = relationship('Organizations', back_populates='organization_knowledge')
