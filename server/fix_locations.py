"""
Script to update all jobs and services with proper geocoded addresses
"""
import asyncio
import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from db import SessionLocal
from models.job import Job
from models.service import Service
from utils.location import reverse_geocode

async def fix_job_locations():
    """Update all jobs with proper geocoded addresses"""
    db = SessionLocal()
    try:
        jobs = db.query(Job).all()
        print(f"📋 Found {len(jobs)} jobs to process")
        
        updated_count = 0
        for job in jobs:
            # Check if location looks like coordinates (starts with "Location:")
            if job.location and job.location.startswith("Location:"):
                print(f"\n🔄 Updating Job #{job.id}: {job.title}")
                print(f"   Old location: {job.location}")
                
                try:
                    new_location = await reverse_geocode(job.latitude, job.longitude)
                    job.location = new_location
                    print(f"   ✅ New location: {new_location}")
                    updated_count += 1
                except Exception as e:
                    print(f"   ❌ Failed: {e}")
        
        if updated_count > 0:
            db.commit()
            print(f"\n✅ Successfully updated {updated_count} job locations")
        else:
            print("\n✅ All job locations are already correct")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

async def fix_service_locations():
    """Update all services with proper geocoded addresses"""
    db = SessionLocal()
    try:
        services = db.query(Service).all()
        print(f"\n📋 Found {len(services)} services to process")
        
        updated_count = 0
        for service in services:
            # Check if location looks like coordinates (starts with "Location:")
            if service.location and service.location.startswith("Location:"):
                print(f"\n🔄 Updating Service #{service.id}: {service.service_name}")
                print(f"   Old location: {service.location}")
                
                try:
                    new_location = await reverse_geocode(service.latitude, service.longitude)
                    service.location = new_location
                    print(f"   ✅ New location: {new_location}")
                    updated_count += 1
                except Exception as e:
                    print(f"   ❌ Failed: {e}")
        
        if updated_count > 0:
            db.commit()
            print(f"\n✅ Successfully updated {updated_count} service locations")
        else:
            print("\n✅ All service locations are already correct")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

async def main():
    print("🚀 Starting location fix script...\n")
    await fix_job_locations()
    await fix_service_locations()
    print("\n✨ Done!")

if __name__ == "__main__":
    asyncio.run(main())
