# AgriCare/server/utils/service.py

from server.schemas.service import ServiceBase, ServiceResponse
from sqlalchemy.orm import Session, joinedload
from server.models.service import Service
from server.models.farmer import Farmer
from server.utils.location import reverse_geocode
from server.utils.geogrid import get_h3_index, get_k_ring
from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError
from typing import List

async def create_service(farmer_id: int, service_data: ServiceBase, db: Session):
    try:
        h3_index = get_h3_index(service_data.latitude, service_data.longitude)
        
        # Try to get location address, use fallback if it fails
        try:
            location = await reverse_geocode(service_data.latitude, service_data.longitude)
        except Exception as e:
            print(f"⚠️ Using fallback location due to geocoding error: {e}")
            location = f"Location: {service_data.latitude:.4f}, {service_data.longitude:.4f}"

        new_service = Service(
            farmer_id=farmer_id,
            service_name=service_data.service_name,
            description=service_data.description,
            latitude=service_data.latitude,
            longitude=service_data.longitude,
            cost=service_data.cost,
            status=service_data.status,
            h3_index=h3_index,
            location=location
        )

        db.add(new_service)
        db.commit()
        db.refresh(new_service)

        return {"message": "Service created successfully."}
    except SQLAlchemyError as e:
        db.rollback()
        print(f"❌ Database error: {e}")
        raise HTTPException(status_code=500, detail="Database error. Failed to create service.")

async def get_services(farmer_id: int, db: Session) -> List[Service]:
    try:
        return db.query(Service).filter(Service.farmer_id == farmer_id).all()
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Database error. Failed to fetch services.")

async def delete_service(service_id: int, farmer_id: int, db: Session):
    try:
        service = db.query(Service).filter(Service.id == service_id, Service.farmer_id == farmer_id).first()

        if not service:
            raise HTTPException(status_code=404, detail="Service not found.")

        db.delete(service)
        db.commit()
        return {"message": "Service deleted successfully."}
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error. Failed to delete service.")

async def nearby_services(farmer_id: int, latitude: float, longitude: float, k: int, db: Session) -> List[ServiceResponse]:
    try:
        h3_indices = get_k_ring(latitude, longitude, k)
        services = (
            db.query(Service)
            .options(joinedload(Service.farmer).joinedload(Farmer.user))
            .filter(Service.h3_index.in_(h3_indices), Service.farmer_id != farmer_id)
            .all()
        )

        return [
            ServiceResponse(
                id=service.id,
                service_name=service.service_name,
                description=service.description,
                latitude=service.latitude,
                longitude=service.longitude,
                cost=float(service.cost),
                status=service.status,
                location=service.location,
                h3_index=service.h3_index,
                farmer_name=service.farmer.user.name,
                farmer_id=service.farmer_id
            )
            for service in services
        ]
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Database error. Failed to fetch nearby services.")
