# AgriCare/server/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from server.db import init_db
from server.api import *
from server.api.chat import chat_router
import server.utils.firebase

app = FastAPI(title="AgriCare API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(signup_router)
app.include_router(login_router)
app.include_router(job_router)
app.include_router(service_router)
app.include_router(chat_router)