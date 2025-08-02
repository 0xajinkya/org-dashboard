"""Imports modules."""

from components.organization_listings import organization_listings
from db import connect_to_db

connect_to_db()


organization_listings()
