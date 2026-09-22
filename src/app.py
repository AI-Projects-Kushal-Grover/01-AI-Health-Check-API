from pathlib import Path
import logging

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException

from handler import Handler
from models import HumanHealthRequest

# Load environment variables from .env file
env_file = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(env_file)

app = FastAPI(title="AI Health Check", version="0.1.0")
handlers = Handler()

@app.post("/check_human_health")
async def check_human_health(request: HumanHealthRequest):
    try:
        logging.info("Received request for human health analysis")
        return await handlers.check_human_health(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
