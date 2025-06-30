from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import google.generativeai as genai
import re
import os
import json
from app.utils import log_message, retry

router = APIRouter()

class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    destination: str
    passport_country: str
    travel_date: str
    purpose: str

def extract_query_data(query: str) -> dict:
    destination = None
    patterns_destination = [
        r'going to (\w+)',
        r'travel(?:ing)? to (\w+)',
        r'traveling to (\w+)',
        r'visa requirements.*?to (\w+)',
        r'going to (\w+)',
        r'visit to (\w+)',
        r'holder traveling to (\w+)',
        r'going to (\w+)',
        r'to (\w+)',
    ]
    for pat in patterns_destination:
        m = re.search(pat, query, re.IGNORECASE)
        if m:
            destination = m.group(1)
            break

    passport_country = None
    patterns_passport = [
        r'on an? (\w+) passport',
        r'with an? (\w+) passport',
        r'for an? (\w+) passport holder',
        r'for a[n]? (\w+) passport holder',
        r'on a (\w+) passport',
        r'(\w+) passport holder',
    ]
    for pat in patterns_passport:
        m = re.search(pat, query, re.IGNORECASE)
        if m:
            passport_country = m.group(1)
            if passport_country.lower() == "us":
                passport_country = "US"
            elif passport_country.lower() == "uk" or passport_country.lower() == "british":
                passport_country = "UK"
            elif passport_country.lower() == "american":
                passport_country = "US"
            elif passport_country.lower() == "canadian":
                passport_country = "Canada"
            elif passport_country.lower() == "indian":
                passport_country = "India"
            elif passport_country.lower() == "australian":
                passport_country = "Australia"
            break

    travel_date = None
    month_names = [
        "january", "february", "march", "april", "may", "june",
        "july", "august", "september", "october", "november", "december"
    ]
    patterns_date = [
        r'next (\w+)',
        r'in (\w+)',
        r'in the month of (\w+)',
        r'for (\w+) (\d{4})',
    ]
    for pat in patterns_date:
        m = re.search(pat, query, re.IGNORECASE)
        if m:
            candidate = m.group(1)
            if candidate.lower() in month_names:
                travel_date = candidate
                break
    if not travel_date:
        for month in month_names:
            if re.search(month, query, re.IGNORECASE):
                travel_date = month.capitalize()
                break

    purpose = None
    purpose_keywords = [
        "tourism", "business", "vacation", "study", "family visit", "visit", "work", "conference"
    ]
    for keyword in purpose_keywords:
        if re.search(rf'for (a |an )?{keyword}\b', query, re.IGNORECASE):
            if keyword == "visit" and re.search(r'family visit', query, re.IGNORECASE):
                purpose = "family visit"
            else:
                purpose = keyword
            break

    if purpose:
        if purpose.lower() in ["vacation"]:
            purpose = "vacation"
        elif purpose.lower() in ["family visit"]:
            purpose = "family visit"
        elif purpose.lower() in ["study"]:
            purpose = "study"
        elif purpose.lower() in ["tourism"]:
            purpose = "tourism"
        elif purpose.lower() in ["business"]:
            purpose = "business"

    if not all([destination, passport_country, travel_date, purpose]):
        raise HTTPException(status_code=400, detail="Invalid query format")

    return {
        "destination": destination,
        "passport_country": passport_country,
        "travel_date": travel_date,
        "purpose": purpose
    }

def call_gemini_api(query: str) -> dict:
    api_key = os.getenv("API_KEY")
    if not api_key:
        log_message("Gemini API key not set", level="error")
        raise HTTPException(status_code=500, detail="Gemini API key not configured")

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-pro")
    prompt = (
        "Extract the following fields from this visa query: "
        "destination, passport_country, travel_date, purpose. "
        "Return as JSON. Query: '" + query + "'"
    )
    try:
        response = model.generate_content(prompt)
        text = response.text
        result = json.loads(text)
        return result
    except Exception as e:
        log_message(f"Gemini API call failed: {e}", level="error")
        raise HTTPException(status_code=500, detail="Gemini API call failed")

def parse_query_with_gemini(query: str) -> QueryResponse:
    def _call():
        result = call_gemini_api(query)
        for field in ["destination", "passport_country", "travel_date", "purpose"]:
            if field not in result or not result[field]:
                log_message(f"Possible hallucination: missing {field}", level="warning")
        return QueryResponse(
            destination=result.get("destination", ""),
            passport_country=result.get("passport_country", ""),
            travel_date=result.get("travel_date", ""),
            purpose=result.get("purpose", "")
        )
    return retry(_call, retries=3, delay=2)

@router.post("/parse-query", response_model=QueryResponse)
async def parse_query(request: QueryRequest):
    if not request.query or len(request.query) < 10:
        raise HTTPException(
            status_code=400,
            detail="Query must be a non-empty string with sufficient detail."
        )
    log_message(f"Received query: {request.query}", level="info")
    try:
        return parse_query_with_gemini(request.query)
    except Exception:
        log_message("Falling back to regex extraction.", level="warning")
        return extract_query_data(request.query)