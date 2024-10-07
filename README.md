# AI Chatbot

This project is an AI chatbot using Langchain and Gemini, built with FastAPI for the backend and React with Vite for the frontend.

## Setup

### Backend

1. Navigate to the directory: `cd backend/`.
2. Create virtual environment: `python -m venv .venv`
3. Activate virtual environment: `source .venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
6. Rename `.env.dev` file to `.env` and replace              `your_api_key_here` with your actual Google API key
5. Run the server: `uvicorn app.main:app --port 8003 --reload`
6. The server should be running at `http://127.0.0.1:8003`
7. Visit `http://127.0.0.1:8003/docs` for the API docs 

### Frontend

1. Navigate to the directory: `cd frontend/`.
2. Install dependencies: `npm install`
3. Start the development server: `npm run dev`
4. The UI should be running at `http://127.0.0.1:5173`

## Deployment

Use Docker to containerize the application. A `Dockerfile` is provided for the backend.
