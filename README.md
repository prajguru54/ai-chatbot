# AI Chatbot

This project is an AI chatbot using Langchain and Gemini, built with FastAPI for the backend and React with Vite for the frontend.

## Setup

### Backend

1. Navigate to the directory: `cd backend/`.
2. Create virtual environment: `python -m venv .venv`
3. Activate virtual environment: `source .venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Run the server: `uvicorn app.main:app --reload`

### Frontend

1. Navigate to the directory: `cd frontend/`.
2. Install dependencies: `npm install`
3. Start the development server: `npm run dev`

## Deployment

Use Docker to containerize the application. A `Dockerfile` is provided for the backend.
