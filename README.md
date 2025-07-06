# Saathi GenAI Visa System

## Overview

Saathi GenAI Visa System is a production-ready backend service that:
- Integrates with multiple simulated visa partners (API & HTML).
- Normalizes and stores visa requirements in both MongoDB and SQLite.
- Provides REST APIs to create and retrieve visa requirements.
- Offers a GenAI-powered microservice (using Google Gemini) to parse free-text visa queries into structured data.
- Is ready for deployment on Azure using Docker.

---

## Features

- **/visa-requirements (POST/GET):** Integrate, normalize, and store visa requirements from multiple partners.
- **/parse-query (POST):** Extracts structured visa info from free-text queries using Gemini LLM (with regex fallback).
- **Async, robust error handling, and logging.**
- **Unit tested and production-ready.**
- **Docker and Azure deployment support.**

---

## Project Structure

```
saathi-genai-query-parser/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── parser.py
│   ├── schemas.py
│   ├── utils.py
│   └── visa_requirements.py
├── tests/
│   ├── __init__.py
│   └── test_parser.py
├── requirements.txt
├── Dockerfile
├── .dockerignore
├── .env.example
├── .env
├── README.md
├── azure-deploy.yaml
└── create_tables.py
```

---

## Setup Instructions

1. **Clone the repository:**
   ```sh
   git clone https://github.com/manikantpandey/Saathi-visa-system.git
   cd saathi-genai-query-parser
   ```

2. **Create a virtual environment (recommended):**
   ```sh
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On Linux/Mac:
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```sh
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   - Copy `.env.example` to `.env` and fill in your values (Gemini API key, DB URIs, etc).

5. **Initialize the SQLite database (run once):**
   ```sh
   python create_tables.py
   ```

6. **Run the application:**
   ```sh
   uvicorn app.main:app --reload
   ```

---

## API Usage

### 1. **Parse Free-text Visa Query (GenAI-powered)**

**POST** `/parse-query`

**Request:**
```json
{
  "query": "Going to France in July for tourism on an Indian passport. What’s the visa process?"
}
```

**Response:**
```json
{
  "destination": "France",
  "passport_country": "India",
  "travel_date": "July",
  "purpose": "tourism"
}
```

---

### 2. **Create Visa Requirement**

**POST** `/visa-requirements`

**Request:**
```json
{
  "country": "France",
  "passport": "India",
  "travel_dates": "July",
  "purpose": "tourism"
}
```

**Response:**
```json
{
  "country": "France",
  "passport": "India",
  "travel_dates": "July",
  "purpose": "tourism",
  "requirements": "Partner A: India passport holders need a visa for France for tourism during July.\nPartner B: India passport holders must apply for a tourism visa to France for travel in July."
}
```

---

### 3. **Get Visa Requirement by Country**

**GET** `/visa-requirements/{country}`

**Response:**
```json
{
  "country": "France",
  "passport": "India",
  "travel_dates": "July",
  "purpose": "tourism",
  "requirements": "Partner A: India passport holders need a visa for France for tourism during July.\nPartner B: India passport holders must apply for a tourism visa to France for travel in July."
}
```

---

## Testing

To run the tests:
```sh
pytest tests/
```

---

## Deployment

- **Docker:**  
  Build and run the container:
  ```sh
  docker build -t saathi-genai .
  docker run -p 8000:8000 --env-file .env saathi-genai
  ```

- **Azure:**  
  Use the provided `azure-deploy.yaml` for Azure App Service deployment.  
  Ensure all environment variables are set in your Azure portal.

---

## Environment Variables

- `API_KEY` – Your Google Gemini API key.
- `DATABASE_URL` – SQLite or MySQL connection string.
- `MONGODB_URI` – MongoDB Atlas connection string.
- `LOG_LEVEL`, `PORT`, `DEBUG` – Optional settings.

---

## License

This project is licensed under the MIT License.
Feel free to modify and use it as per your requirements.

---
