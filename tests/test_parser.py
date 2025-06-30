import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.parser import extract_query_data
import pytest
from app.parser import extract_query_data

def test_extract_query_data():
    queries = [
        {
            "input": "Going to France in July for tourism on an Indian passport. What’s the visa process?",
            "expected": {
                "destination": "France",
                "passport_country": "India",
                "travel_date": "July",
                "purpose": "tourism"
            }
        },
        {
            "input": "I need to travel to Germany for business in September with a US passport.",
            "expected": {
                "destination": "Germany",
                "passport_country": "US",
                "travel_date": "September",
                "purpose": "business"
            }
        },
        {
            "input": "What are the visa requirements for an Australian passport holder traveling to Japan for a vacation in December?",
            "expected": {
                "destination": "Japan",
                "passport_country": "Australia",
                "travel_date": "December",
                "purpose": "vacation"
            }
        },
        {
            "input": "Visa process for a Canadian passport holder going to Italy for study in August.",
            "expected": {
                "destination": "Italy",
                "passport_country": "Canada",
                "travel_date": "August",
                "purpose": "study"
            }
        },
        {
            "input": "Traveling to Spain for a family visit on a British passport next March.",
            "expected": {
                "destination": "Spain",
                "passport_country": "UK",
                "travel_date": "March",
                "purpose": "family visit"
            }
        }
    ]

    for query in queries:
        result = extract_query_data(query["input"])
        assert result == query["expected"], f"Expected {query['expected']} but got {result}"