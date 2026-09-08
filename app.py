"""
FastAPI Server for AI Paragraph Detector and Humanizer.
Runs locally on http://127.0.0.1:8000
"""

import os
import re
import uuid
from typing import Optional
from fastapi import FastAPI, HTTPException, Request, UploadFile, File, Form, Response
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from engine.detector import AIDetector
from engine.humanizer import AIHumanizer
from engine.document_processor import (
    extract_text_from_document,
    humanize_document_structured,
    generate_docx_document,
    generate_pdf_document,
    generate_txt_document,
    document_cache,
    sanitize_filename
)

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
    academic_shield: bool = Field(default=True, description="Preserve in-text citations, bracketed numbers, and quotes")

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
        ollama_model=req.ollama_model,
        academic_shield=req.academic_shield
    )

    # 3. Analyze newly humanized text
    humanized_analysis = detector.analyze(h_result["humanized_text"])

    # 4. Generate and cache real download files
    doc_id = str(uuid.uuid4())
    paragraphs = [p.strip() for p in h_result["humanized_text"].split("\n\n") if p.strip()]
    if not paragraphs:
        paragraphs = [h_result["humanized_text"]]
    
    docx_bytes = generate_docx_document(paragraphs, title="Humanized Text")
    pdf_bytes = generate_pdf_document(paragraphs, title="Humanized Text")
    txt_bytes = generate_txt_document(paragraphs)

    document_cache.store(doc_id, {
        "stem": "veritas_document",
        "docx_bytes": docx_bytes,
        "pdf_bytes": pdf_bytes,
        "txt_bytes": txt_bytes,
        "text": h_result["humanized_text"]
    })

    return JSONResponse(content={
        "original_analysis": original_analysis,
        "humanization": h_result,
        "humanized_analysis": humanized_analysis,
        "score_delta": original_analysis["ai_percentage"] - humanized_analysis["ai_percentage"],
        "doc_id": doc_id,
        "download_urls": {
            "pdf": f"/api/document/download/{doc_id}?format=pdf",
            "docx": f"/api/document/download/{doc_id}?format=docx",
            "txt": f"/api/document/download/{doc_id}?format=txt"
        }
    })

@app.post("/api/document/process")
async def process_document_endpoint(
    file: UploadFile = File(...),
    tone: str = Form("natural"),
    intensity: str = Form("balanced"),
    academic_shield: bool = Form(True)
):
    """
    End-to-end document processing pipeline:
    Upload -> Validation -> Extraction -> AI Analysis -> Humanization -> Re-analysis -> File Generation -> Download Ready
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file uploaded.")

    # Read file content safely
    try:
        file_bytes = await file.read()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to read uploaded file: {str(e)}")

    clean_filename = sanitize_filename(file.filename)
    stem, ext = os.path.splitext(clean_filename)
    stem = re.sub(r'[^a-zA-Z0-9_\-]', '_', stem)[:40] or "document"

    # 1. Text Extraction
    try:
        extraction = extract_text_from_document(file_bytes, clean_filename)
    except ValueError as val_err:
        raise HTTPException(status_code=400, detail=str(val_err))
    except Exception as err:
        raise HTTPException(status_code=500, detail=f"Error extracting document text: {str(err)}")

    original_text = extraction["text"].strip()
    if not original_text:
        raise HTTPException(status_code=400, detail="Extracted document text is empty.")

    # 2. AI Analysis of Original Document
    try:
        original_analysis = detector.analyze(original_text)
    except Exception as det_err:
        raise HTTPException(status_code=500, detail=f"Failed to analyze original document: {str(det_err)}")

    # 3. Structure-preserving Humanization
    try:
        h_result = humanize_document_structured(
            humanizer=humanizer,
            text=original_text,
            tone=tone,
            intensity=intensity,
            academic_shield=academic_shield
        )
    except Exception as hum_err:
        raise HTTPException(status_code=500, detail=f"Failed to humanize document: {str(hum_err)}")

    humanized_text = h_result["humanized_text"].strip()
    paragraphs = h_result["paragraphs"]

    # 4. AI Re-Analysis of Humanized Document
    try:
        humanized_analysis = detector.analyze(humanized_text)
    except Exception as re_err:
        raise HTTPException(status_code=500, detail=f"Failed to re-analyze humanized document: {str(re_err)}")

    # 5. Generate Real Binary Document Files
    doc_id = str(uuid.uuid4())
    doc_title = f"{stem.replace('_', ' ').title()} - Humanized"

    try:
        docx_bytes = generate_docx_document(paragraphs, title=doc_title)
        pdf_bytes = generate_pdf_document(paragraphs, title=doc_title)
        txt_bytes = generate_txt_document(paragraphs)
    except Exception as gen_err:
        raise HTTPException(status_code=500, detail=f"Failed to generate download files: {str(gen_err)}")

    # 6. Store in Session Cache
    document_cache.store(doc_id, {
        "stem": stem,
        "filename": clean_filename,
        "format": extraction["format"],
        "docx_bytes": docx_bytes,
        "pdf_bytes": pdf_bytes,
        "txt_bytes": txt_bytes,
        "text": humanized_text,
        "paragraphs": paragraphs
    })

    score_delta = original_analysis["ai_percentage"] - humanized_analysis["ai_percentage"]
    orig_fmt = extraction["format"]
    default_fmt = "docx" if orig_fmt == "docx" else ("pdf" if orig_fmt == "pdf" else "txt")

    return JSONResponse(content={
        "status": "success",
        "doc_id": doc_id,
        "filename": clean_filename,
        "file_stem": stem,
        "file_size": len(file_bytes),
        "format": orig_fmt,
        "page_count": extraction.get("page_count", 1),
        "word_count": len(original_text.split()),
        "char_count": len(original_text),
        "humanized_word_count": len(humanized_text.split()),
        "humanized_char_count": len(humanized_text),
        "original_text": original_text,
        "humanized_text": humanized_text,
        "original_analysis": original_analysis,
        "humanized_analysis": humanized_analysis,
        "score_delta": score_delta,
        "changes_applied": h_result.get("changes_applied", []),
        "shielded_items_count": h_result.get("shielded_items_count", 0),
        "download_urls": {
            "pdf": f"/api/document/download/{doc_id}?format=pdf",
            "docx": f"/api/document/download/{doc_id}?format=docx",
            "txt": f"/api/document/download/{doc_id}?format=txt",
            "default": f"/api/document/download/{doc_id}?format={default_fmt}"
        }
    })

@app.get("/api/document/download/{doc_id}")
async def download_document_endpoint(doc_id: str, format: str = "pdf"):
    """
    Downloads processed humanized document in real PDF, DOCX, or TXT format
    with preserved original naming ({original_stem}_humanized.{ext}).
    """
    cached = document_cache.get(doc_id)
    if not cached:
        raise HTTPException(
            status_code=404,
            detail="Document download session has expired or was not found. Please re-upload your document."
        )

    stem = cached.get("stem", "document")
    fmt = format.lower().strip().lstrip(".")

    if fmt == "pdf":
        content = cached["pdf_bytes"]
        media_type = "application/pdf"
        filename = f"{stem}_humanized.pdf"
    elif fmt in ["docx", "doc"]:
        content = cached["docx_bytes"]
        media_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        filename = f"{stem}_humanized.docx"
    elif fmt in ["txt", "text", "md"]:
        content = cached["txt_bytes"]
        media_type = "text/plain; charset=utf-8"
        filename = f"{stem}_humanized.txt"
    else:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported download format '{format}'. Supported formats: pdf, docx, txt."
        )

    headers = {
        "Content-Disposition": f'attachment; filename="{filename}"',
        "Access-Control-Expose-Headers": "Content-Disposition",
        "Cache-Control": "no-cache"
    }

    return Response(content=content, media_type=media_type, headers=headers)

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
