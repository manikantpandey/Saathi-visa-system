from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.parser import router as parser_router
from app.visa_requirements import router as visa_router

import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="Saathi GenAI Query Parser",
    description="Extracts structured visa query data using Gemini LLM.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "ok"}

# Include the parser router
app.include_router(parser_router, prefix="", tags=["Parser"])

# Include the visa router
app.include_router(visa_router, prefix="/visa", tags=["Visa"])