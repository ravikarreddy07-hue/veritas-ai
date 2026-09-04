# Veritas AI: Paragraph Detector & Humanizer (Localhost)

A local web application that runs 100% privately on your machine to analyze paragraphs for AI patterns and transform them into natural, human-written text.

---

## 🌟 Key Features

### 1. AI Paragraph Detector
- **Sentence-Level Heatmap**: Color-codes every sentence (Green for Human, Yellow for Mixed, Red for Likely AI) with hoverable forensic tooltips showing exact triggers.
- **Burstiness (Rhythm Variance)**: Measures sentence length variability (humans write in bursts with varied cadence; AI has rigid, predictable rhythm).
- **Lexical Richness (Type-Token Ratio & Entropy)**: Detects formulaic token distribution and vocabulary repetition.
- **AI Trope Detection**: Identifies overused LLM phrases like *"delve into"*, *"testament to"*, *"plays a crucial role"*, *"foster"*, *"multifaceted"*, etc.
- **Readability Indices**: Computes Flesch-Kincaid Grade Level and Reading Ease.

### 2. Intelligent Humanizer & Rewriter
- **Cadence Restructuring**: Injects natural burstiness by splitting monotonous sentences and inserting punchy beats.
- **Trope De-Toxification**: Swaps artificial clichés for natural, contextual human phrasing.
- **4 Tone Modes**:
  - 🌿 **Natural / Conversational**: Casual, active voice, colloquial transitions, natural contractions.
  - 🎓 **Academic**: Scholarly rigor without cliché filler.
  - 💼 **Business**: Crisp, action-oriented corporate phrasing.
  - 🎨 **Creative**: Expressive pacing and rhythmic variation.
- **3 Intensity Settings**: Mild, Balanced, and Deep Rewrite.
- **Diff Inspector**: Side-by-side `<ins>` and `<del>` highlighting of every phrase transformed.
- **Instant Before & After Comparison**: Automatically re-scans the rewritten text to show the exact reduction in AI likelihood.
- **Optional Local LLM Hook**: Toggle support for local Ollama instances (`http://localhost:11434`).

---

## 🚀 How to Run on Localhost

### Quick Start
Double-click `run.bat` or run:

```powershell
python -m uvicorn app:app --host 127.0.0.1 --port 8000 --reload
```

Open your browser at:
👉 **`http://localhost:8000`**

---

## 📁 Project Structure

```
ai-detector-humanizer/
├── app.py                  # FastAPI web server and REST API endpoints
├── test_engine.py          # Automated verification test suite
├── requirements.txt        # Python dependencies
├── run.bat                 # One-click Windows batch launcher
├── run.ps1                 # Windows PowerShell launcher
├── engine/
│   ├── __init__.py
│   ├── detector.py         # Multi-metric AI detection algorithm
│   ├── humanizer.py        # Humanization & cadence restructuring
│   └── linguistics.py      # Trope lexicons, readability, and tokenizers
├── static/
│   ├── app.js              # Frontend UI logic and sentence heatmap
│   └── styles.css          # Glassmorphism styling and custom animations
└── templates/
    └── index.html          # Interactive dual-pane web studio
```
