from db import get_session
get_session()

from components.organization_listings import organization_listings

organizations = organization_listings()