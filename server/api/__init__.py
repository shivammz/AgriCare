# AgriCare/server/api/__init__.py

from server.api.auth.signup import signup_router
from server.api.auth.login import login_router
from server.api.job import job_router
from server.api.service import service_router

__all__ = ["signup_router", "login_router", "job_router", "service_router"]
