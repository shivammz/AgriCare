# AgriCare/server/utils/job.py

from server.schemas.job import JobBase, JobResponse
from sqlalchemy.orm import Session
from server.models.job import Job
from server.models.farmer import Farmer
from server.utils.location import reverse_geocode
from server.utils.geogrid import get_h3_index
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException
from server.utils.geogrid import get_k_ring
from typing import List
from sqlalchemy.orm import joinedload

async def create_job(farmer_id: int, job_data: JobBase, db: Session):
    try:
        
        h3_index = get_h3_index(job_data.latitude, job_data.longitude)
        
        # Try to get location address, use fallback if it fails
        try:
            location = await reverse_geocode(job_data.latitude, job_data.longitude)
        except Exception as e:
            print(f"⚠️ Using fallback location due to geocoding error: {e}")
            location = f"Location: {job_data.latitude:.4f}, {job_data.longitude:.4f}"
            
        new_job = Job(
            title=job_data.title,
            farmer_id=farmer_id,
            description=job_data.description,
            number_of_labourers=job_data.number_of_labourers,
            required_skills=job_data.required_skills,
            latitude=job_data.latitude,
            longitude=job_data.longitude,
            daily_wage=job_data.daily_wage,
            perks=job_data.perks,
            start_date=job_data.start_date,
            end_date=job_data.end_date,
            status=job_data.status,
            h3_index=h3_index,
            location=location
        )

        db.add(new_job)
        db.commit()
        db.refresh(new_job)

        return {"message": "Job created successfully."}
    except SQLAlchemyError as e:
        db.rollback()
        print(f"❌ Database error: {e}")
        raise HTTPException(status_code=500, detail=f"Database error.{e} Failed to create job.")


async def get_jobs(farmer_id: int, db: Session)-> List[Job]:
    try:
        jobs = db.query(Job).filter(Job.farmer_id==farmer_id).all()
        return jobs
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail="Database error. Failed to fetch jobs.")
    

async def delete_job(job_id: int, farmer_id: int, db: Session):
    try:
        job = db.query(Job).filter(Job.id == job_id, Job.farmer_id == farmer_id).first()

        if not job:
            raise HTTPException(status_code=404, detail="Job not found.")

        db.delete(job)
        db.commit()
        return {"message": "Job deleted successfully."}

    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error. Failed to delete job.")
    

async def nearby_jobs(latitude: float, longitude: float, k: int, db: Session) -> List[JobResponse]:
    try:
        h3_indices = get_k_ring(latitude, longitude, k)
        jobs = (
            db.query(Job)
            .options(joinedload(Job.farmer).joinedload(Farmer.user))
            .filter(Job.h3_index.in_(h3_indices))
            .all()
        )

        return [
            JobResponse(
                id=job.id,
                title=job.title,
                description=job.description,
                number_of_labourers=job.number_of_labourers,
                required_skills=job.required_skills,
                latitude=job.latitude,
                longitude=job.longitude,
                daily_wage=float(job.daily_wage),
                perks=job.perks,
                start_date=job.start_date,
                end_date=job.end_date,
                status=job.status,
                location=job.location,
                h3_index=job.h3_index,
                farmer_name=job.farmer.user.name,
                farmer_id=job.farmer_id
            )
            for job in jobs
        ]
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Database error. Failed to fetch nearby jobs.")