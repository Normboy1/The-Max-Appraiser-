"""
FastAPI application for the AI Software Appraiser API.
"""

from fastapi import FastAPI, HTTPException, UploadFile, File, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import tempfile
import shutil
import os

from ..core.appraiser import SoftwareAppraiser
from ..models.evaluation import CodeQualityReport, ProjectEvaluation, IdeaEvaluation

app = FastAPI(
    title="AI Software Appraiser API",
    description="API for evaluating software quality using AI",
    version="0.1.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------ Idea Evaluation Models ------------
from pydantic import BaseModel
import re
import requests
from collections import Counter

class IdeaRequest(BaseModel):
    idea: str
    plan: str
    roadmap: str
    currency: str | None = "USD"

# Initialize the appraiser
appraiser = SoftwareAppraiser()

# ----------------- Mount Frontend -----------------
FRONTEND_DIR = Path(__file__).parent.parent / "frontend"
if FRONTEND_DIR.exists():
    app.mount("/app", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")

# ----------------- Evaluation Constants -----------------
KEYWORDS_FUNCTIONAL = {"solve", "automate", "reduce", "improve", "optimize", "streamline", "efficient", "productivity"}
KEYWORDS_SCALABILITY = {"scale", "cloud", "multi-tenant", "kubernetes", "api", "microservice", "serverless", "distributed"}
KEYWORDS_MARKET_POTENTIAL = {"market", "demand", "growing", "trend", "opportunity", "need", "pain point"}
KEYWORDS_TECH = {"ai", "ml", "blockchain", "iot", "ar", "vr", "blockchain", "api"}

# Market factors (weights for different aspects)
MARKET_WEIGHTS = {
    'market_size': 0.3,
    'growth_rate': 0.25,
    'competition': 0.25,
    'barriers_to_entry': 0.2
}

# Technical factors
TECH_WEIGHTS = {
    'innovation': 0.4,
    'feasibility': 0.3,
    'scalability': 0.3
}

# Business model factors
BUSINESS_WEIGHTS = {
    'revenue_potential': 0.4,
    'customer_acquisition': 0.3,
    'retention': 0.3
}

# ----------------- HuggingFace inference helper -----------------
HF_MODEL = "mistralai/Mistral-7B-Instruct"
HF_API = f"https://api-inference.huggingface.co/models/{HF_MODEL}"
HF_TOKEN = os.getenv("HF_TOKEN")

# Cache for LLM responses to save costs and improve performance
from functools import lru_cache
import hashlib

def get_text_hash(text: str) -> str:
    """Generate a hash for text to use as cache key."""
    return hashlib.md5(text.encode()).hexdigest()

@lru_cache(maxsize=100)
def _cached_llm_evaluation(prompt: str, prompt_hash: str) -> dict:
    """Cache LLM evaluations to save costs and improve performance."""
    try:
        resp = requests.post(
            HF_API,
            headers={"Authorization": f"Bearer {HF_TOKEN}", "Content-Type": "application/json"},
            json={"inputs": prompt, "parameters": {"temperature": 0.3, "max_length": 500}},
            timeout=45
        )
        if resp.ok:
            return resp.json()
    except Exception as e:
        print(f"LLM API error: {str(e)}")
    return {}

def _get_llm_evaluation(prompt: str) -> dict:
    """Get evaluation from LLM with caching."""
    if not HF_TOKEN:
        return {}
    prompt_hash = get_text_hash(prompt)
    return _cached_llm_evaluation(prompt, prompt_hash)

def _analyze_market_potential(text: str) -> dict:
    """Analyze market potential using keyword analysis and simple heuristics."""
    words = set(re.findall(r"\w+", text.lower()))
    
    # Simple keyword-based analysis
    market_terms = len(words & KEYWORDS_MARKET_POTENTIAL)
    tech_terms = len(words & KEYWORDS_TECH)
    
    # Calculate market score (0-1)
    market_score = min(market_terms / 3, 1.0)  # Cap at 1.0
    tech_score = min(tech_terms / 2, 1.0)  # Cap at 1.0
    
    return {
        'market_score': round(market_score, 2),
        'tech_score': round(tech_score, 2),
        'market_keywords': list(words & KEYWORDS_MARKET_POTENTIAL),
        'tech_keywords': list(words & KEYWORDS_TECH)
    }

def _evaluate_idea_with_llm(idea: str, plan: str, roadmap: str) -> dict:
    """Evaluate idea using LLM with structured output."""
    prompt = """You are an expert VC analyst. Analyze this software idea and provide a detailed evaluation.
    Respond with a JSON object containing these exact keys:
    {
        "originality": 0.0-1.0,  // How unique and innovative is the idea?
        "feasibility": 0.0-1.0,  // How feasible is it to build this?
        "market_need": 0.0-1.0,  // How strong is the market need?
        "competitive_edge": 0.0-1.0,  // How strong is the competitive advantage?
        "risks": ["risk1", "risk2", ...],  // List of potential risks
        "strengths": ["strength1", "strength2", ...],  // List of key strengths
        "summary": "Brief evaluation summary"  // 2-3 sentence summary
    }
    
    Idea: {idea}
    Implementation Plan: {plan}
    Roadmap: {roadmap}
    """
    
    response = _get_llm_evaluation(prompt.format(idea=idea, plan=plan, roadmap=roadmap))
    if not response:
        return {}
        
    try:
        # Extract the JSON from the response
        import json
        if isinstance(response, list):
            text = response[0].get("generated_text", "")
        else:
            text = response.get("generated_text", "")
        
        # Find JSON in the response
        json_str = text[text.find('{'):text.rfind('}')+1]
        return json.loads(json_str)
    except Exception as e:
        print(f"Error parsing LLM response: {str(e)}")
        return {}

def _calculate_valuation(scores: dict, currency: str = "USD") -> dict:
    """Calculate valuation based on evaluation scores."""
    # Base valuation factors
    base_value = 1_000_000  # Base value for a decent idea
    
    # Calculate weighted score (0-1)
    weighted_score = (
        scores.get('originality', 0.5) * 0.25 +
        scores.get('feasibility', 0.5) * 0.2 +
        scores.get('market_need', 0.5) * 0.3 +
        scores.get('competitive_edge', 0.5) * 0.25
    )
    
    # Apply exponential scaling (better ideas get disproportionately higher valuations)
    valuation = base_value * (weighted_score ** 0.5) * 100  # Scale to reasonable range
    
    # Apply currency conversion
    fx_rates = {"USD": 1.0, "EUR": 0.92, "GBP": 0.79, "JPY": 158.0}
    fx_rate = fx_rates.get(currency.upper(), 1.0)
    
    return {
        'amount': round(valuation * fx_rate, 2),
        'currency': currency.upper(),
        'base_currency': 'USD',
        'fx_rate': fx_rate
    }


@app.get("/")
async def read_root():
    """Root endpoint with API information."""
    return {
        "name": "AI Software Appraiser",
        "version": "0.1.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }

@app.post("/evaluate/code", response_model=CodeQualityReport)
async def evaluate_code(
    code: str,
    language: str = "python"
):
    """
    Evaluate the quality of a piece of code.
    
    Args:
        code: Source code to evaluate
        language: Programming language of the code
        
    Returns:
        Code quality report
    """
    try:
        return appraiser.evaluate_code_quality(code, language)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/evaluate/idea")
async def evaluate_idea(payload: IdeaRequest):
    """
    Evaluate a SaaS idea with comprehensive analysis including:
    - Originality and innovation
    - Technical feasibility
    - Market potential and competition
    - Business model viability
    - Risk assessment
    """
    # Combine all text for keyword analysis
    combined_text = f"{payload.idea} {payload.plan} {payload.roadmap}"
    
    # Get evaluation from LLM with fallback to heuristics
    llm_eval = {}
    if HF_TOKEN:
        llm_eval = _evaluate_idea_with_llm(payload.idea, payload.plan, payload.roadmap)
    
    # Get market analysis
    market_analysis = _analyze_market_potential(combined_text)
    
    # Calculate scores with fallbacks
    scores = {
        'originality': llm_eval.get('originality', 0.5),
        'feasibility': llm_eval.get('feasibility', 0.5),
        'market_need': llm_eval.get('market_need', market_analysis.get('market_score', 0.5)),
        'competitive_edge': llm_eval.get('competitive_edge', 0.5),
        'market_score': market_analysis.get('market_score', 0.5),
        'tech_score': market_analysis.get('tech_score', 0.5)
    }
    
    # Calculate overall score (weighted average)
    overall_score = round(
        (
            scores['originality'] * 0.25 +
            scores['feasibility'] * 0.2 +
            scores['market_need'] * 0.3 +
            scores['competitive_edge'] * 0.25
        ),
        3
    )
    
    # Calculate grade
    grade = (
        "A" if overall_score >= 0.9 else
        "B" if overall_score >= 0.8 else
        "C" if overall_score >= 0.7 else
        "D" if overall_score >= 0.6 else "F"
    )
    
    # Calculate valuation
    valuation = _calculate_valuation(scores, payload.currency)
    
    # Prepare detailed response
    response = {
        'scores': {
            'overall': overall_score,
            'originality': scores['originality'],
            'feasibility': scores['feasibility'],
            'market_need': scores['market_need'],
            'competitive_edge': scores['competitive_edge'],
            'market_potential': scores['market_score'],
            'technical_viability': (scores['feasibility'] + scores['tech_score']) / 2
        },
        'grade': grade,
        'valuation': valuation,
        'market_analysis': {
            'keywords': {
                'market_terms': market_analysis.get('market_keywords', []),
                'tech_terms': market_analysis.get('tech_keywords', [])
            },
            'score': market_analysis.get('market_score', 0.5)
        },
        'risks': llm_eval.get('risks', [
            'Limited market validation',
            'High competition in this space',
            'Technical complexity may be underestimated'
        ][:3]),
        'strengths': llm_eval.get('strengths', [
            'Solves a clear problem',
            'Uses modern technology stack',
            'Addresses a growing market need'
        ][:3]),
        'evaluation_summary': llm_eval.get('summary', 
            'This idea shows potential but requires further validation. Consider conducting market research '
            'and building an MVP to test assumptions.'
        ),
        'recommendations': [
            'Conduct user interviews to validate the problem',
            'Build a minimum viable product (MVP) to test core assumptions',
            'Research competitors and identify unique differentiators',
            'Develop a go-to-market strategy',
            'Consider potential partnerships or integrations'
        ],
        'explanation': llm_eval.get('summary', 'Evaluation completed successfully')
    }
    
    return response


@app.post("/evaluate/project", response_model=ProjectEvaluation)
async def evaluate_project(
    project_path: str
):
    """
    Evaluate an entire software project.
    
    Args:
        project_path: Path to the project directory or repository
        
    Returns:
        Project evaluation report
    """
    try:
        return appraiser.evaluate_project(project_path)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/evaluate/upload")
async def upload_and_evaluate(
    file: UploadFile = File(...)
):
    """
    Upload a project archive and evaluate it.
    
    Args:
        file: Project archive (zip, tar.gz, etc.)
        
    Returns:
        Project evaluation report
    """
    try:
        # Create a temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            # Save the uploaded file
            file_path = os.path.join(temp_dir, file.filename)
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            # TODO: Extract the archive if needed
            # For now, just evaluate the file directly
            if file.filename.endswith(('.py', '.js', '.java', '.c', '.cpp', '.go', '.rs')):
                with open(file_path, 'r') as f:
                    code = f.read()
                return appraiser.evaluate_code_quality(code, file.filename.split('.')[-1])
            else:
                return appraiser.evaluate_project(temp_dir)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
