from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import os

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class EvaluationRequest(BaseModel):
    idea: str
    plan: str
    roadmap: str
    currency: str = "USD"

@app.get("/")
async def read_root():
    return {"message": "The Max Appraiser API is running"}

@app.post("/evaluate/idea")
async def evaluate_idea(request: EvaluationRequest):
    # This is a placeholder response - the actual implementation would be in app/api/app.py
    return {
        "grade": "A+",
        "score": 95,
        "evaluation": "This is a placeholder response. The actual API implementation would go here.",
        "scores": {
            "originality": 95,
            "feasibility": 90,
            "market_potential": 85,
            "technical_merit": 100
        }
    }

# This is needed for Vercel to work properly
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 3000)))
