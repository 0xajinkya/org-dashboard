from typing import Sequence

from sqlalchemy.orm import selectinload
from sqlalchemy.sql.elements import ColumnElement

from db import db
from models.organizations import OrganizationInformation


class OrganizationInformationService:
    @staticmethod
    def find_many(
        filters: Sequence[ColumnElement[bool]] = (),
        page: int = 1,
        limit: int = 10,
        fetch_all: bool = False,
    ):
        query = db.query(OrganizationInformation).options(
            selectinload(OrganizationInformation.organization)
        )
        if filters:
            query = query.filter(*filters)

        if not fetch_all:
            query = query.limit(limit).offset((page - 1) * limit)

        return query.all()

    @staticmethod
    def get_one(id: int):
        return (
            db.query(OrganizationInformation)
            .filter(OrganizationInformation.id == id)
            .first()
        )

    @staticmethod
    def update_one(id: int, **kwargs):
        try:
            result = (
                db.query(OrganizationInformation)
                .filter(OrganizationInformation.id == id)
                .update(kwargs)
            )
            db.commit()
            return result
        except Exception as e:
            db.rollback()
            raise e
