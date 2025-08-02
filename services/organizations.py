from typing import Sequence

from sqlalchemy.sql.elements import ColumnElement

from db import db
from models.organizations import Organizations


class OrganizationsService:
    @staticmethod
    def find_many(
        filters: Sequence[ColumnElement[bool]] = (),
        page: int = 1,
        limit: int = 10,
    ):
        query = db.query(Organizations)
        if filters:
            query = query.filter(*filters)
        return query.limit(limit).offset((page - 1) * limit).all()

    @staticmethod
    def update_one(id: str, **kwargs):
        try:
            result = (
                db.query(Organizations)
                .filter(Organizations.id == id)
                .update(kwargs)
            )
            db.commit()
            return result
        except Exception as e:
            db.rollback()
            raise e

    @staticmethod
    def create_one(**kwargs):
        try:
            organization = Organizations(**kwargs)
            db.add(organization)
            db.commit()
            return organization
        except Exception as e:
            db.rollback()
            raise e
