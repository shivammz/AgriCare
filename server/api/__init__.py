# AgriCare/server/api/__init__.py

from api.auth.signup import signup_router
from api.auth.login import login_router
from api.job import job_router
from api.service import service_router

__all__ = ["signup_router", "login_router", "job_router", "service_router"]
