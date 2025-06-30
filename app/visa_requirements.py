from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import Optional
import requests
from bs4 import BeautifulSoup
import motor.motor_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import Column, Integer, String, Text, select
import os
from app.utils import log_message

# MongoDB setup
MONGODB_URI = os.getenv("MONGODB_URI")
mongo_client = motor.motor_asyncio.AsyncIOMotorClient(MONGODB_URI)
mongo_db = mongo_client["saathi"]
mongo_collection = mongo_db["visa_requirements"]

# SQLite setup (async)
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./saathi.db")
engine = create_async_engine(DATABASE_URL, echo=False, future=True)
SessionLocal = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
Base = declarative_base()

class VisaRequirement(Base):
    __tablename__ = "visa_requirements"
    id = Column(Integer, primary_key=True, index=True)
    country = Column(String, index=True)
    passport = Column(String)
    travel_dates = Column(String)
    purpose = Column(String)
    requirements = Column(Text)

class VisaRequirementRequest(BaseModel):
    country: str
    passport: str
    travel_dates: str
    purpose: str

class VisaRequirementResponse(VisaRequirementRequest):
    requirements: str

router = APIRouter()

# Simulate Partner A (JSON API)
def fetch_partner_a(country, passport, travel_dates, purpose):
    # Simulated response
    return {
        "requirements": f"Partner A: {passport} passport holders need a visa for {country} for {purpose} during {travel_dates}."
    }

# Simulate Partner B (HTML page)
def fetch_partner_b(country, passport, travel_dates, purpose):
    # Simulated HTML (in real use, fetch and parse with requests+BeautifulSoup)
    html = f"""
    <html>
        <body>
            <div id="requirements">
                Partner B: {passport} passport holders must apply for a {purpose} visa to {country} for travel in {travel_dates}.
            </div>
        </body>
    </html>
    """
    soup = BeautifulSoup(html, "html.parser")
    req = soup.find(id="requirements").text.strip()
    return {"requirements": req}

def normalize_data(partner_data):
    # In real use, normalize fields as needed
    return partner_data["requirements"]

@router.post("/visa-requirements", response_model=VisaRequirementResponse)
async def create_visa_requirement(req: VisaRequirementRequest):
    # Simulate fetching from both partners and merging
    try:
        partner_a_data = fetch_partner_a(req.country, req.passport, req.travel_dates, req.purpose)
        partner_b_data = fetch_partner_b(req.country, req.passport, req.travel_dates, req.purpose)
        normalized = f"{normalize_data(partner_a_data)}\n{normalize_data(partner_b_data)}"
    except Exception as e:
        log_message(f"Partner integration failed: {e}", level="error")
        raise HTTPException(status_code=502, detail="Partner integration failed")

    # Store in MongoDB
    mongo_doc = req.dict()
    mongo_doc["requirements"] = normalized
    await mongo_collection.insert_one(mongo_doc)

    # Store in SQLite
    async with SessionLocal() as session:
        visa_obj = VisaRequirement(
            country=req.country,
            passport=req.passport,
            travel_dates=req.travel_dates,
            purpose=req.purpose,
            requirements=normalized
        )
        session.add(visa_obj)
        await session.commit()

    return VisaRequirementResponse(**mongo_doc)

@router.get("/visa-requirements/{country}", response_model=VisaRequirementResponse)
async def get_visa_requirement(country: str):
    # Try MongoDB first
    doc = await mongo_collection.find_one({"country": country})
    if doc:
        return VisaRequirementResponse(
            country=doc["country"],
            passport=doc["passport"],
            travel_dates=doc["travel_dates"],
            purpose=doc["purpose"],
            requirements=doc["requirements"]
        )
    # Fallback: Try SQLite
    async with SessionLocal() as session:
        result = await session.execute(select(VisaRequirement).where(VisaRequirement.country == country))
        visa = result.scalars().first()
        if visa:
            return VisaRequirementResponse(
                country=visa.country,
                passport=visa.passport,
                travel_dates=visa.travel_dates,
                purpose=visa.purpose,
                requirements=visa.requirements
            )
    raise HTTPException(status_code=404, detail="Visa requirements not found")