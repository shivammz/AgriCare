# AgriCare/server/api/service.py

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from server.schemas.service import ServiceBase
from server.db import get_db
from server.utils.service import create_service, get_services, delete_service, nearby_services
from server.utils.helper import request_to_token
from server.utils.token import require_role, token_to_farmer_id

service_router = APIRouter(prefix="/api", tags=["Services"])

@service_router.post("/service")
async def create__service(request: Request, service_data: ServiceBase, db: Session = Depends(get_db), dep=require_role(0)):
    token = request_to_token(request)
    farmer_id = token_to_farmer_id(db, token)
    result = await create_service(farmer_id, service_data, db)
    return result

@service_router.get("/service")
async def get__services(request: Request, db: Session = Depends(get_db), dep=require_role(0)):
    token = request_to_token(request)
    farmer_id = token_to_farmer_id(db, token)
    services = await get_services(farmer_id, db)
    return services

@service_router.delete("/service/{service_id}")
async def delete__service(service_id: int, request: Request, db: Session = Depends(get_db), dep=require_role(0)):
    token = request_to_token(request)
    farmer_id = token_to_farmer_id(db, token)
    result = await delete_service(service_id, farmer_id, db)
    return result

@service_router.get("/nearby-services")
async def nearby__services(request: Request, latitude: float, longitude: float, k: int = 2, db: Session = Depends(get_db), dep=require_role(0)):
    token = request_to_token(request)
    farmer_id = token_to_farmer_id(db, token)
    services = await nearby_services(farmer_id, latitude, longitude, k, db)
    return services
