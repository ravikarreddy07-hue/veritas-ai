"""
FastAPI Server for AI Paragraph Detector and Humanizer.
Runs locally on http://127.0.0.1:8000
"""

import os
from typing import Optional
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from engine.detector import AIDetector
from engine.humanizer import AIHumanizer

app = FastAPI(
    title="AI Paragraph Detector & Humanizer",
    description="Local AI text detection and humanization studio",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize engines
detector = AIDetector()
humanizer = AIHumanizer()

# Ensure directories exist
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")

os.makedirs(STATIC_DIR, exist_ok=True)
os.makedirs(TEMPLATES_DIR, exist_ok=True)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Request Models
class DetectRequest(BaseModel):
    text: str = Field(..., description="Text paragraph to analyze for AI patterns")

class HumanizeRequest(BaseModel):
    text: str = Field(..., description="Text paragraph to humanize")
    tone: str = Field(default="natural", description="Tone: natural, academic, professional, creative")
    intensity: str = Field(default="balanced", description="Intensity: mild, balanced, aggressive")
    use_ollama: bool = Field(default=False, description="Whether to query local Ollama LLM")
    ollama_model: str = Field(default="llama3", description="Ollama model name")

class RerollRequest(BaseModel):
    sentence: str = Field(..., description="Single sentence to reroll into 3 alternative variations")
    tone: str = Field(default="natural", description="Tone for the reroll")

# Preloaded sample texts for instant testing
SAMPLE_TEXTS = {
    "ai_essay": {
        "title": "ChatGPT Standard Output (High AI)",
        "text": (
            "In today's fast-paced digital world, artificial intelligence plays a crucial role in modern society. "
            "Furthermore, it is important to note that machine learning algorithms foster innovation across multifaceted industries. "
            "A rich tapestry of computational tools serves as a testament to human ingenuity. "
            "Moreover, navigating the complexities of modern data science requires a holistic approach to succeed."
        )
    },
    "ai_corporate": {
        "title": "Corporate AI Memo (High AI)",
        "text": (
            "In the realm of enterprise operations, leveraging cloud-based solutions is paramount for long-term scalability. "
            "Additionally, it is worth noting that modern cross-functional teams must seamlessly align their core competencies. "
            "Consequently, embarking on a digital transformation journey will foster synergy and drive operational excellence. "
            "In conclusion, adopting this strategic paradigm will unlock unprecedented opportunities."
        )
    },
    "human_personal": {
        "title": "Personal Story (Authentic Human)",
        "text": (
            "I honestly never expected this project to take so long. We started back in November, thinking it'd be done by Christmas. "
            "Nope! Between frozen pipes, late deliveries, and a leaky basement, everything that could go sideways did. "
            "Still, somehow we pulled it off yesterday afternoon. Honestly, I'm just relieved we don't have to look at that drywall anymore."
        )
    },
    "human_technical": {
        "title": "Engineer's Note (Authentic Human)",
        "text": (
            "The memory leak was maddening. For three straight days I stared at heap dumps, suspecting a rogue database connection. "
            "Turns out? It was a stray closure capturing a giant buffer in the logging middleware. Two lines changed, and memory dropped right back to 45 megabytes. "
            "Never skipping a heap benchmark again."
        )
    }
}

@app.get("/", response_class=HTMLResponse)
async def serve_dashboard():
    """Serves the main web dashboard."""
    index_path = os.path.join(TEMPLATES_DIR, "index.html")
    if os.path.exists(index_path):
        with open(index_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse(content="<h1>AI Detector & Humanizer</h1><p>index.html not found. Check templates folder.</p>")

@app.post("/api/detect")
async def detect_text(req: DetectRequest):
    """Analyzes text paragraph for AI vs Human characteristics."""
    if not req.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty.")
    result = detector.analyze(req.text)
    return JSONResponse(content=result)

@app.post("/api/humanize")
async def humanize_text(req: HumanizeRequest):
    """
    Transforms text into human-like prose and automatically runs re-detection
    to return before-and-after scores.
    """
    if not req.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty.")
    
    # 1. Analyze original
    original_analysis = detector.analyze(req.text)

    # 2. Humanize
    h_result = humanizer.humanize(
        text=req.text,
        tone=req.tone,
        intensity=req.intensity,
        use_ollama=req.use_ollama,
        ollama_model=req.ollama_model
    )

    # 3. Analyze newly humanized text
    humanized_analysis = detector.analyze(h_result["humanized_text"])

    return JSONResponse(content={
        "original_analysis": original_analysis,
        "humanization": h_result,
        "humanized_analysis": humanized_analysis,
        "score_delta": original_analysis["ai_percentage"] - humanized_analysis["ai_percentage"]
    })

@app.post("/api/reroll")
async def reroll_sentence_endpoint(req: RerollRequest):
    """
    Returns 3 distinct AI-resistant alternative phrasings for an individual sentence.
    """
    if not req.sentence.strip():
        raise HTTPException(status_code=400, detail="Sentence cannot be empty.")
    
    variants = humanizer.reroll_sentence(req.sentence, tone=req.tone)
    return JSONResponse(content={
        "original": req.sentence,
        "variants": variants
    })

@app.get("/api/samples")
async def get_samples():
    """Returns preset sample texts."""
    return JSONResponse(content=SAMPLE_TEXTS)

@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "ai-detector-humanizer", "version": "1.0.0"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    host = os.environ.get("HOST", "0.0.0.0")
    print(f"Starting Veritas AI Website on http://{host}:{port} ...")
    uvicorn.run("app:app", host=host, port=port, reload=False)
