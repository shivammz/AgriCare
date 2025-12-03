# AgriCare/server/api/job.py

from fastapi import APIRouter, Depends, Request
from server.schemas.job import JobBase
from sqlalchemy.orm import Session
from server.db import get_db
from server.utils.job import create_job, get_jobs, delete_job, nearby_jobs
from server.utils.helper import request_to_token
from server.utils.token import require_role, token_to_farmer_id

job_router = APIRouter(prefix="/api", tags=["Jobs"])

@job_router.post("/job")
async def create__job(request: Request, job_data: JobBase, db: Session = Depends(get_db), dep=require_role(0)):
    token = request_to_token(request)
    farmer_id = token_to_farmer_id(db, token)
    result = await create_job(farmer_id, job_data, db)
    return result

@job_router.get("/job")
async def get__jobs(request: Request, db: Session = Depends(get_db), dep=require_role(0)):
    token = request_to_token(request)
    farmer_id = token_to_farmer_id(db, token)
    jobs = await get_jobs(farmer_id, db)
    return jobs

@job_router.delete("/job/{job_id}")
async def delete__job(job_id: int, request: Request, db: Session = Depends(get_db), dep=require_role(0)):
    token = request_to_token(request)
    farmer_id = token_to_farmer_id(db, token)
    result = await delete_job(job_id, farmer_id, db)
    return result

@job_router.get("/nearby-jobs")
async def nearby__jobs(latitude: float, longitude: float, k: int = 2, db: Session = Depends(get_db)):
    jobs = await nearby_jobs(latitude, longitude, k, db)
    return jobs