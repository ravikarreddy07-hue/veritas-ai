"""
Document Processor for Veritas AI Studio.
Handles:
- Secure file validation and sanitization
- Multi-format text extraction (PDF, DOCX, TXT, MD)
- Multi-paragraph structure-preserving humanization
- High-fidelity binary document generation (OpenXML DOCX, PDF, UTF-8 TXT)
- In-memory document session cache with automatic TTL expiration
"""

import io
import os
import re
import time
import uuid
import threading
from typing import Dict, List, Any, Optional, Tuple

import docx
from docx.shared import Inches, Pt, RGBColor
from fpdf import FPDF
from pypdf import PdfReader

# Allowed extensions and MIME types
ALLOWED_EXTENSIONS = {".pdf", ".docx", ".doc", ".txt", ".md"}
MAX_FILE_SIZE_BYTES = 15 * 1024 * 1024  # 15 MB limit


def sanitize_filename(filename: str) -> str:
    """Sanitizes user filename to prevent path traversal and shell injection."""
    if not filename:
        return "document"
    # Strip path components
    basename = os.path.basename(filename)
    # Remove null bytes, control chars, path traversal dots
    clean = re.sub(r'[\x00-\x1f\x7f/\\]', '', basename)
    clean = re.sub(r'^\.+', '', clean)
    clean = clean.strip()
    return clean if clean else "document"


def get_file_extension(filename: str) -> str:
    """Extracts lowercase file extension including dot."""
    ext = os.path.splitext(filename)[1].lower()
    return ext


def validate_file(filename: str, file_bytes: bytes) -> Tuple[str, str]:
    """
    Validates file extension and size.
    Returns (sanitized_filename, extension).
    Raises ValueError on validation failure.
    """
    clean_name = sanitize_filename(filename)
    ext = get_file_extension(clean_name)
    
    if ext not in ALLOWED_EXTENSIONS:
        raise ValueError(
            f"Unsupported file format '{ext}'. Veritas AI supports PDF (.pdf), Word (.docx, .doc), and Text (.txt, .md) documents."
        )
        
    if len(file_bytes) > MAX_FILE_SIZE_BYTES:
        mb_size = round(len(file_bytes) / (1024 * 1024), 2)
        raise ValueError(
            f"File size ({mb_size}MB) exceeds the 15MB limit. Please upload a smaller document."
        )
        
    if len(file_bytes) == 0:
        raise ValueError("The uploaded file is empty.")
        
    return clean_name, ext


def extract_text_from_document(file_bytes: bytes, filename: str) -> Dict[str, Any]:
    """
    Extracts text while preserving paragraphs, headings, and document structure.
    Returns:
    {
        "text": full_text_str,
        "paragraphs": [p1, p2, ...],
        "page_count": int,
        "format": "pdf" | "docx" | "txt"
    }
    """
    clean_name, ext = validate_file(filename, file_bytes)

    if ext == ".pdf":
        try:
            reader = PdfReader(io.BytesIO(file_bytes))
            page_count = len(reader.pages)
            if page_count == 0:
                raise ValueError("PDF document contains no readable pages.")
                
            page_texts = []
            for i, page in enumerate(reader.pages):
                pt = page.extract_text() or ""
                if pt.strip():
                    page_texts.append(pt.strip())
                    
            if not page_texts:
                raise ValueError(
                    "No readable text could be extracted from this PDF. It may contain scanned images rather than selectable text."
                )
                
            # Join pages with double newlines
            full_text = "\n\n".join(page_texts)
            # Break down into paragraphs
            paragraphs = [p.strip() for p in re.split(r'\n{2,}', full_text) if p.strip()]
            
            return {
                "text": full_text,
                "paragraphs": paragraphs if paragraphs else [full_text],
                "page_count": page_count,
                "format": "pdf"
            }
        except Exception as e:
            if isinstance(e, ValueError):
                raise
            raise ValueError(f"Failed to read PDF document: {str(e)}")

    elif ext in [".docx", ".doc"]:
        try:
            doc = docx.Document(io.BytesIO(file_bytes))
            paragraphs = []
            for p in doc.paragraphs:
                p_text = p.text.strip()
                if p_text:
                    paragraphs.append(p_text)
                    
            if not paragraphs:
                raise ValueError("No readable text paragraphs found in Word document.")
                
            full_text = "\n\n".join(paragraphs)
            return {
                "text": full_text,
                "paragraphs": paragraphs,
                "page_count": max(1, len(paragraphs) // 4),
                "format": "docx"
            }
        except Exception as e:
            if isinstance(e, ValueError):
                raise
            raise ValueError(f"Failed to read Word document (.docx): {str(e)}")

    else:
        # Text or Markdown
        try:
            # Try utf-8 first
            text = file_bytes.decode("utf-8")
        except UnicodeDecodeError:
            try:
                # Fallback to latin-1 / windows-1252
                text = file_bytes.decode("latin-1")
            except Exception as e:
                raise ValueError(f"Failed to decode text document encoding: {str(e)}")
                
        text = text.strip()
        if not text:
            raise ValueError("The text document is empty.")
            
        paragraphs = [p.strip() for p in re.split(r'\r?\n\r?\n', text) if p.strip()]
        return {
            "text": text,
            "paragraphs": paragraphs if paragraphs else [text],
            "page_count": max(1, len(text.split()) // 300),
            "format": "txt"
        }


def humanize_document_structured(
    humanizer,
    text: str,
    tone: str = "natural",
    intensity: str = "balanced",
    academic_shield: bool = True
) -> Dict[str, Any]:
    """
    Humanizes multi-paragraph documents while preserving headings, paragraph breaks,
    spacing, and academic citations.
    """
    raw_blocks = re.split(r'\r?\n\r?\n', text)
    humanized_blocks = []
    total_changes = []
    shielded_count = 0

    for block in raw_blocks:
        block_clean = block.strip()
        if not block_clean:
            continue

        # Detect if this block is a heading or title
        words = block_clean.split()
        is_heading = (
            block_clean.startswith("#") or
            (len(block_clean) < 60 and len(words) <= 8 and not block_clean.endswith((".", "!", "?", ";", ":")))
        )

        if is_heading:
            # Preserve headings intact without applying body sentence transformations
            humanized_blocks.append(block_clean)
        else:
            # Run convergent humanizer on this paragraph
            h_res = humanizer.humanize(
                block_clean,
                tone=tone,
                intensity=intensity,
                academic_shield=academic_shield
            )
            humanized_blocks.append(h_res["humanized_text"])
            total_changes.extend(h_res.get("changes_applied", []))
            shielded_count += h_res.get("shielded_items_count", 0)

    full_humanized = "\n\n".join(humanized_blocks)
    unique_changes = list(dict.fromkeys(total_changes))

    return {
        "humanized_text": full_humanized,
        "paragraphs": humanized_blocks,
        "changes_applied": unique_changes[:12],
        "shielded_items_count": shielded_count
    }


def generate_docx_document(paragraphs: List[str], title: str = "Humanized Document") -> bytes:
    """Generates a professional OpenXML Microsoft Word (.docx) document."""
    doc = docx.Document()
    
    # Configure 1-inch margins
    sections = doc.sections
    for section in sections:
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(1.0)

    # Document Header Title
    title_p = doc.add_paragraph()
    title_run = title_p.add_run(title)
    title_run.font.name = 'Calibri'
    title_run.font.size = Pt(18)
    title_run.font.bold = True
    title_run.font.color.rgb = RGBColor(30, 41, 59)
    title_p.paragraph_format.space_after = Pt(4)

    # Subtitle / Metadata
    sub_p = doc.add_paragraph()
    sub_run = sub_p.add_run("Processed with Veritas AI • Verified Human Cadence & Authenticity")
    sub_run.font.name = 'Calibri'
    sub_run.font.size = Pt(9.5)
    sub_run.font.italic = True
    sub_run.font.color.rgb = RGBColor(100, 116, 139)
    sub_p.paragraph_format.space_after = Pt(16)

    # Add paragraphs with formatting
    for p_text in paragraphs:
        p_clean = p_text.strip()
        if not p_clean:
            continue

        p = doc.add_paragraph()
        p.paragraph_format.line_spacing = 1.15
        p.paragraph_format.space_after = Pt(8)

        # Check if heading
        if p_clean.startswith("#"):
            level = len(p_clean) - len(p_clean.lstrip("#"))
            heading_text = p_clean.lstrip("#").strip()
            h_run = p.add_run(heading_text)
            h_run.font.name = 'Calibri'
            h_run.font.size = Pt(14 if level == 1 else 12)
            h_run.font.bold = True
            h_run.font.color.rgb = RGBColor(15, 23, 42)
            p.paragraph_format.space_before = Pt(12)
            p.paragraph_format.space_after = Pt(6)
        else:
            run = p.add_run(p_clean)
            run.font.name = 'Calibri'
            run.font.size = Pt(11)
            run.font.color.rgb = RGBColor(30, 41, 59)

    out_buffer = io.BytesIO()
    doc.save(out_buffer)
    out_buffer.seek(0)
    return out_buffer.getvalue()


class VeritasPDF(FPDF):
    """Custom FPDF subclass with professional header and footer."""
    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(148, 163, 184)
        self.cell(0, 10, f"Veritas AI Verified Human Document - Page {self.page_no()}", align="C")


def generate_pdf_document(paragraphs: List[str], title: str = "Humanized Document") -> bytes:
    """Generates a professional, print-ready PDF document using FPDF2."""
    pdf = VeritasPDF()
    pdf.set_auto_page_break(auto=True, margin=18)
    pdf.add_page()
    
    # Document Title
    pdf.set_font("Helvetica", "B", 16)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(0, 8, title[:60], new_x="LMARGIN", new_y="NEXT")
    
    # Subtitle
    pdf.set_font("Helvetica", "I", 9)
    pdf.set_text_color(100, 116, 139)
    pdf.cell(0, 6, "Processed with Veritas AI - Verified Human Cadence & Authenticity", new_x="LMARGIN", new_y="NEXT")
    
    # Divider Rule
    pdf.set_draw_color(226, 232, 240)
    pdf.set_line_width(0.4)
    pdf.line(pdf.get_x(), pdf.get_y() + 2, pdf.get_x() + 190, pdf.get_y() + 2)
    pdf.ln(6)

    # Body formatting
    pdf.set_text_color(30, 41, 59)

    for p_text in paragraphs:
        p_clean = p_text.strip()
        if not p_clean:
            continue

        # Sanitize typographic characters for Helvetica latin-1
        safe = (
            p_clean
            .replace('\u201c', '"')
            .replace('\u201d', '"')
            .replace('\u2018', "'")
            .replace('\u2019', "'")
            .replace('\u2014', ' - ')
            .replace('\u2013', '-')
            .replace('\u2026', '...')
        )
        safe = safe.encode('latin-1', 'replace').decode('latin-1')

        if safe.startswith("#"):
            heading = safe.lstrip("#").strip()
            pdf.ln(3)
            pdf.set_font("Helvetica", "B", 12)
            pdf.set_text_color(15, 23, 42)
            pdf.multi_cell(0, 6, heading)
            pdf.ln(2)
            pdf.set_font("Helvetica", "", 10.5)
            pdf.set_text_color(30, 41, 59)
        else:
            pdf.set_font("Helvetica", "", 10.5)
            pdf.multi_cell(0, 5.5, safe)
            pdf.ln(3)

    return bytes(pdf.output())


def generate_txt_document(paragraphs: List[str]) -> bytes:
    """Generates clean UTF-8 plain text with preserved paragraph breaks."""
    clean_paragraphs = [p.strip() for p in paragraphs if p.strip()]
    content = "\n\n".join(clean_paragraphs)
    return content.encode("utf-8")


class DocumentSessionCache:
    """
    Thread-safe in-memory cache for processed documents and download artifacts.
    Keeps documents active for 2 hours before auto-eviction.
    """
    def __init__(self, ttl_seconds: int = 7200, max_items: int = 200):
        self.ttl_seconds = ttl_seconds
        self.max_items = max_items
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.Lock()

    def store(self, doc_id: str, data: Dict[str, Any]):
        with self._lock:
            self._cleanup_expired()
            if len(self._cache) >= self.max_items:
                oldest_id = min(self._cache.keys(), key=lambda k: self._cache[k].get("timestamp", 0))
                del self._cache[oldest_id]
            data["timestamp"] = time.time()
            self._cache[doc_id] = data

    def get(self, doc_id: str) -> Optional[Dict[str, Any]]:
        with self._lock:
            entry = self._cache.get(doc_id)
            if not entry:
                return None
            if time.time() - entry.get("timestamp", 0) > self.ttl_seconds:
                del self._cache[doc_id]
                return None
            return entry

    def _cleanup_expired(self):
        now = time.time()
        expired = [k for k, v in self._cache.items() if now - v.get("timestamp", 0) > self.ttl_seconds]
        for k in expired:
            del self._cache[k]


# Global singleton instance of document cache
document_cache = DocumentSessionCache()
