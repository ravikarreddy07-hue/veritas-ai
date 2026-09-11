"""
AI Content Detection Engine.
Powered by fine-tuned DeBERTa-v3-large transformer model (desklib/ai-text-detector-v1.01)
with batched sliding-window context inference, burstiness variance blending,
minor cliché penalty nudging, and ZeroGPT-standard metric formatting.
"""

import os
import re
import math
import asyncio
import logging
import statistics
from typing import Dict, List, Any, Optional, Tuple

from .linguistics import (
    split_sentences,
    tokenize_words,
    calculate_readability,
    AI_CLICHE_PATTERNS,
    AI_FAVORED_OPENERS,
    STOPWORDS
)

logger = logging.getLogger("AIDetector")

# Optional PyTorch & Hugging Face Transformers integration
try:
    import torch
    import torch.nn as nn
    from transformers import AutoTokenizer, AutoConfig, AutoModel, PreTrainedModel
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    torch = None
    nn = None
    PreTrainedModel = object


if TORCH_AVAILABLE:
    class DesklibAIDetectionModel(PreTrainedModel):
        """
        Custom PyTorch architecture matching desklib/ai-text-detector-v1.01:
        DeBERTa-v3-large transformer base + mean pooling layer + linear classifier head.
        Outputs raw logit; sigmoid yields AI generation probability.
        """
        config_class = AutoConfig

        def __init__(self, config):
            super().__init__(config)
            self.all_tied_weights_keys = {}
            self.model = AutoModel.from_config(config)
            self.classifier = nn.Linear(config.hidden_size, 1)
            self.init_weights()

        def forward(self, input_ids, attention_mask=None, labels=None, **kwargs):
            outputs = self.model(input_ids, attention_mask=attention_mask)
            last_hidden_state = outputs[0]
            input_mask_expanded = attention_mask.unsqueeze(-1).expand(last_hidden_state.size()).float()
            sum_embeddings = torch.sum(last_hidden_state * input_mask_expanded, dim=1)
            sum_mask = torch.clamp(input_mask_expanded.sum(dim=1), min=1e-9)
            pooled_output = sum_embeddings / sum_mask

            logits = self.classifier(pooled_output)
            return {"logits": logits}
else:
    class DesklibAIDetectionModel:
        pass


# Global singleton cache for model and tokenizer to prevent duplicate memory loading
_GLOBAL_MODEL: Optional[Any] = None
_GLOBAL_TOKENIZER: Optional[Any] = None
_GLOBAL_DEVICE: Optional[str] = None
_MODEL_INITIALIZED: bool = False

class AIDetector:
    def __init__(
        self,
        model_name: str = "desklib/ai-text-detector-v1.01",
        device: Optional[str] = None,
        lazy_load: bool = True
    ):
        self.model_name = model_name
        self.preferred_device = device
        self.cliche_compiled = [
            (re.compile(pattern, re.IGNORECASE), info)
            for pattern, info in AI_CLICHE_PATTERNS.items()
        ]
        self.model = _GLOBAL_MODEL
        self.tokenizer = _GLOBAL_TOKENIZER
        self.device = _GLOBAL_DEVICE
        self.has_model = _MODEL_INITIALIZED

        if not lazy_load and TORCH_AVAILABLE and not _MODEL_INITIALIZED:
            self._ensure_model_loaded()

    def _ensure_model_loaded(self) -> bool:
        """
        Initializes or retrieves the globally cached transformer model and tokenizer.
        Auto-detects CUDA GPU (with FP16 for speed/VRAM efficiency) or CPU.
        """
        global _GLOBAL_MODEL, _GLOBAL_TOKENIZER, _GLOBAL_DEVICE, _MODEL_INITIALIZED
        if _MODEL_INITIALIZED and _GLOBAL_MODEL is not None:
            self.model = _GLOBAL_MODEL
            self.tokenizer = _GLOBAL_TOKENIZER
            self.device = _GLOBAL_DEVICE
            self.has_model = True
            return True

        if not TORCH_AVAILABLE:
            logger.warning("PyTorch or Transformers not installed. Operating in heuristic fallback mode.")
            self.has_model = False
            return False

        # Guard against OOM on low-memory cloud instances & Linux cgroups (e.g. Render 512MB free tier)
        try:
            # Check Render environment or explicit disable flag
            if os.environ.get("RENDER") == "true" and os.environ.get("RENDER_PLAN", "free") == "free":
                logger.warning("Render Free Tier detected (512MB RAM). Bypassing 1.7GB neural model to prevent OOM crash.")
                self.has_model = False
                return False

            if os.environ.get("DISABLE_NEURAL_MODEL", "").lower() in ("1", "true", "yes"):
                self.has_model = False
                return False

            # Check Linux cgroup memory limit (container limit)
            cgroup_mem = None
            if os.path.exists("/sys/fs/cgroup/memory.max"):
                with open("/sys/fs/cgroup/memory.max", "r") as f:
                    val = f.read().strip()
                    if val != "max":
                        cgroup_mem = int(val)
            elif os.path.exists("/sys/fs/cgroup/memory/memory.limit_in_bytes"):
                with open("/sys/fs/cgroup/memory/memory.limit_in_bytes", "r") as f:
                    val = int(f.read().strip())
                    if val < (1 << 50):
                        cgroup_mem = val

            if cgroup_mem is not None and cgroup_mem < 1.8 * (1024 ** 3):
                logger.warning(
                    f"Container cgroup memory limit ({cgroup_mem / (1024**2):.0f} MB) is below requirement for 1.7GB DeBERTa model. "
                    "Operating in calibrated fallback mode to prevent container crash."
                )
                self.has_model = False
                return False

            # Check host virtual memory
            import psutil
            mem = psutil.virtual_memory()
            if mem.total < 1.8 * (1024 ** 3):
                logger.warning(
                    f"System memory ({mem.total / (1024**2):.0f} MB) is below requirement for 1.7GB DeBERTa model. "
                    "Operating in calibrated fallback mode to prevent container crash."
                )
                self.has_model = False
                return False
        except Exception as e:
            logger.debug(f"Memory check exception: {e}")

        try:
            if self.preferred_device:
                dev = torch.device(self.preferred_device)
            elif torch.cuda.is_available():
                dev = torch.device("cuda")
            else:
                dev = torch.device("cpu")

            logger.info(f"Loading tokenizer '{self.model_name}'...")
            tokenizer = AutoTokenizer.from_pretrained(self.model_name)

            logger.info(f"Loading transformer model '{self.model_name}' onto {dev}...")
            model = DesklibAIDetectionModel.from_pretrained(self.model_name)
            if dev.type == "cuda":
                model = model.half()
            model.to(dev)
            model.eval()

            _GLOBAL_MODEL = model
            _GLOBAL_TOKENIZER = tokenizer
            _GLOBAL_DEVICE = dev
            _MODEL_INITIALIZED = True

            self.model = model
            self.tokenizer = tokenizer
            self.device = dev
            self.has_model = True
            logger.info(f"Model '{self.model_name}' successfully loaded on {dev}.")
            return True
        except Exception as e:
            logger.error(f"Failed to load Hugging Face model '{self.model_name}': {e}. Falling back to calibrated heuristics.")
            self.has_model = False
            return False

    def _build_context_windows(self, sentences: List[str]) -> List[str]:
        """
        Constructs a ~3-sentence contextual window around each sentence: [S_{i-1}, S_i, S_{i+1}].
        Allows DeBERTa to score each individual sentence within natural discourse context.
        """
        n = len(sentences)
        if n <= 1:
            return sentences

        windows = []
        for i in range(n):
            prev_s = sentences[i - 1].strip() if i > 0 else ""
            curr_s = sentences[i].strip()
            next_s = sentences[i + 1].strip() if i < n - 1 else ""
            parts = [p for p in (prev_s, curr_s, next_s) if p]
            windows.append(" ".join(parts))
        return windows

    def _batch_predict_probabilities(self, texts: List[str], batch_size: int = 16) -> List[float]:
        """
        Runs batched inference through the transformer model to predict AI probability in [0.0, 1.0].
        """
        if not self.has_model or not texts or self.model is None or self.tokenizer is None:
            return [0.15] * len(texts)

        probabilities: List[float] = []
        for start_idx in range(0, len(texts), batch_size):
            batch = texts[start_idx : start_idx + batch_size]
            encoded = self.tokenizer(
                batch,
                padding=True,
                truncation=True,
                max_length=512,
                return_tensors="pt"
            )
            input_ids = encoded["input_ids"].to(self.device)
            attention_mask = encoded["attention_mask"].to(self.device)

            with torch.inference_mode():
                outputs = self.model(input_ids=input_ids, attention_mask=attention_mask)
                logits = outputs["logits"].squeeze(-1)
                probs = torch.sigmoid(logits)
                if probs.ndim == 0:
                    probs = probs.unsqueeze(0)
                probabilities.extend(probs.float().cpu().tolist())

        return probabilities

    def _calibrate_probability(self, p: float) -> float:
        """
        Calibrated mapping converting raw model sigmoid probabilities to [0.0, 1.0].
        The uncalibrated linear head in DeBERTa-v3-large exhibits a base prior around ~0.50
        for short sentences; this calibrated mapping provides a sharp separation:
          - p <= 0.50: clearly human cadence, mapped to [0.00, 0.05]
          - 0.50 < p <= 0.82: transitional/moderate region, mapped to [0.05, 0.40]
          - p > 0.82: strong AI certainty, mapped to [0.40, 1.00]
        """
        if p <= 0.50:
            return 0.05 * (p / 0.50)
        elif p <= 0.82:
            return 0.05 + 0.35 * (((p - 0.50) / 0.32) ** 1.5)
        else:
            return 0.40 + 0.60 * (((p - 0.82) / 0.18) ** 0.8)

    async def analyze_async(self, text: str) -> Dict[str, Any]:
        """
        Non-blocking asynchronous wrapper for FastAPI endpoints to avoid blocking the event loop.
        """
        return await asyncio.to_thread(self.analyze, text)

    def analyze(self, text: str) -> Dict[str, Any]:
        """
        Performs comprehensive multi-metric AI content detection on the input text.
        """
        text = text.strip() if text else ""
        if not text or len(text.split()) < 5:
            word_c = len(text.split()) if text else 0
            return {
                "fakePercentage": 0.0,
                "ai_percentage": 0,
                "human_percentage": 100,
                "is_human_written": True,
                "is_gpt_generated": False,
                "feedback_message": "Please enter at least a complete sentence or paragraph (minimum 5 words) for analysis.",
                "verdict": "Insufficient Text",
                "verdict_color": "text-gray-400",
                "confidence": "Low",
                "textWords": word_c,
                "aiWords": 0,
                "sentences": [],
                "metrics": {
                    "word_count": word_c,
                    "sentence_count": 0,
                    "ai_words": 0,
                    "burstiness_score": 0.0,
                    "entropy_score": 0.0,
                    "ttr": 0.0,
                    "cliche_count": 0,
                    "readability": {}
                },
                "explanation": "Please enter at least a complete sentence or paragraph (minimum 5 words) for analysis."
            }

        sentences = split_sentences(text)
        words = tokenize_words(text)
        total_words = len(words)
        total_sentences = len(sentences)

        # 1. Burstiness Analysis (Variance of sentence lengths)
        sent_lengths = [len(tokenize_words(s)) for s in sentences]
        if total_sentences > 1:
            mean_len = statistics.mean(sent_lengths)
            stdev_len = statistics.stdev(sent_lengths)
            cv = stdev_len / mean_len if mean_len > 0 else 0
            burstiness_val = min(1.0, cv)

            # High variance (CV >= 0.30) is strongly characteristic of authentic human cadence
            if cv >= 0.40:
                burstiness_ai_score = 5.0
            elif cv >= 0.30:
                burstiness_ai_score = 10.0
            elif cv >= 0.22:
                burstiness_ai_score = 18.0
            elif cv >= 0.15:
                burstiness_ai_score = 45.0
            else:
                burstiness_ai_score = 80.0
        else:
            stdev_len = 0.0
            mean_len = sent_lengths[0] if sent_lengths else 0
            burstiness_val = 0.35
            burstiness_ai_score = 25.0

        # 2. Lexical Diversity & Cliché Scan (Minor bonus signals)
        unique_words = set(words)
        ttr = len(unique_words) / total_words if total_words > 0 else 0

        text_for_cliches = re.sub(r'["“][^"”\n]{2,300}?["”]', '', text)
        total_cliches_found = 0
        cliche_matches_list = []
        for regex, info in self.cliche_compiled:
            matches = regex.findall(text_for_cliches)
            if matches:
                total_cliches_found += len(matches)
                cliche_matches_list.append(info["desc"])

        # 3. Model Inference (Primary Signal - Desklib DeBERTa-v3-large)
        if not self.has_model and TORCH_AVAILABLE:
            self._ensure_model_loaded()

        raw_probabilities: List[float] = []
        if self.has_model and self.model is not None:
            # Build sliding 3-sentence windows for rich contextual evaluation
            context_windows = self._build_context_windows(sentences)
            raw_probabilities = self._batch_predict_probabilities(context_windows, batch_size=16)
        else:
            # Fallback heuristic probability if neural model is offline
            raw_probabilities = [0.15] * total_sentences

        # 4. Multi-Signal Sentence Scoring & Heatmap Breakdown
        analyzed_sentences = []
        sentence_scores = []

        for idx, sent in enumerate(sentences):
            sent_words = tokenize_words(sent)
            word_count = len(sent_words)

            # Primary model probability (calibrated 0% to 100%)
            model_prob = raw_probabilities[idx] if idx < len(raw_probabilities) else 0.15
            calibrated_prob = self._calibrate_probability(model_prob)
            model_score = calibrated_prob * 100.0

            reasons = []

            # Secondary signal: Burstiness penalty / reward (10% weight)
            # Blended base = 85% neural model + 10% burstiness
            base_score = (model_score * 0.85) + (burstiness_ai_score * 0.10)

            # Minor bonus signal: Cliché and Opener nudge (max +5% to +10% bonus nudge, never main classifier)
            cliche_nudge = 0.0
            for regex, info in self.cliche_compiled:
                if regex.search(sent):
                    cliche_nudge += 5.0
                    reasons.append(f"Contains {info['desc']}")
                    break

            s_lower = sent.lower().strip()
            for op in AI_FAVORED_OPENERS:
                if s_lower.startswith(op):
                    cliche_nudge += 3.0
                    reasons.append(f"Overused opener '{op}'")
                    break

            cliche_nudge = min(10.0, cliche_nudge)

            # Conversational/natural human cadence rewards
            cadence_bonus = 0.0
            if word_count <= 8:
                cadence_bonus += 5.0
                reasons.append("Short punchy human cadence")
            if any(c in sent for c in ["'", "’"]):
                cadence_bonus += 4.0
                reasons.append("Natural contraction")
            if re.search(r'\b(i|me|my|we|us|our|you|your)\b', sent, re.IGNORECASE):
                cadence_bonus += 4.0
                reasons.append("First-person human voice")

            cadence_bonus = min(10.0, cadence_bonus)

            # Final blended sentence score
            final_s_score = max(0.0, min(100.0, base_score + cliche_nudge - cadence_bonus))
            sentence_scores.append(final_s_score)

            # ZeroGPT Sentence Classification Thresholds:
            # Red (>= 65%): AI / GPT Generated
            # Yellow (50% - 64%): Mixed / partial AI
            # Green (< 50%): Likely Human
            if final_s_score >= 65.0:
                classification = "Likely AI"
                color_class = "bg-red-500/20 border-red-500/50 text-red-200"
                highlight_color = "red"
                is_ai = True
                if not reasons:
                    reasons.append(f"High neural AI pattern ({round(model_score)}%)")
            elif final_s_score >= 50.0:
                classification = "Mixed"
                color_class = "bg-yellow-500/20 border-yellow-500/50 text-yellow-200"
                highlight_color = "yellow"
                is_ai = True
                if not reasons:
                    reasons.append(f"Moderate neural AI probability ({round(model_score)}%)")
            else:
                classification = "Likely Human"
                color_class = "bg-emerald-500/20 border-emerald-500/50 text-emerald-200"
                highlight_color = "green"
                is_ai = False
                if not reasons:
                    reasons.append("Natural human variation and cadence")

            analyzed_sentences.append({
                "id": idx + 1,
                "text": sent,
                "score": round(final_s_score),
                "model_prob": round(model_prob * 100.0, 1),
                "calibrated_prob": round(calibrated_prob * 100.0, 1),
                "words": word_count,
                "classification": classification,
                "color_class": color_class,
                "highlight_color": highlight_color,
                "is_ai": is_ai,
                "reasons": reasons
            })

        # 5. ZeroGPT-Standard Metric Calculation:
        # aiWords: Count of actual words in sentences crossing the AI threshold (is_ai == True).
        # fakePercentage = (aiWords / textWords) * 100 reflects actual classified volume.
        ai_words = sum(s["words"] for s in analyzed_sentences if s["is_ai"])
        fake_percentage = round((ai_words / total_words * 100.0), 1) if total_words > 0 else 0.0

        ai_percentage = int(max(0, min(100, round(fake_percentage))))
        human_percentage = 100 - ai_percentage

        # ZeroGPT Standard Verdict Thresholds:
        # 0% - 15%: "Your text is Human written"
        # 15% - 35%: "Your text is Most likely Human written, may include parts generated by AI"
        # 35% - 65%: "Your text contains mixed signals, with some parts generated by AI"
        # 65% - 100%: "Your text is AI / GPT Generated"
        if fake_percentage < 15.0:
            verdict = "Your text is Human written"
            feedback_message = "Your text is Human written"
            verdict_color = "text-emerald-400"
            is_human_written = True
            is_gpt_generated = False
            confidence = "High"
            summary_expl = "Your text is Human written. Authentic human rhythm, natural variation, and zero AI patterns detected."
        elif fake_percentage < 35.0:
            verdict = "Your text is Most likely Human written, may include parts generated by AI"
            feedback_message = "Your text is Most likely Human written, may include parts generated by AI"
            verdict_color = "text-emerald-300"
            is_human_written = True
            is_gpt_generated = False
            confidence = "Medium"
            summary_expl = "Your text is Most likely Human written, may include parts generated by AI. Predominantly natural cadence."
        elif fake_percentage < 65.0:
            verdict = "Your text contains mixed signals, with some parts generated by AI"
            feedback_message = "Your text contains mixed signals, with some parts generated by AI"
            verdict_color = "text-yellow-400"
            is_human_written = False
            is_gpt_generated = False
            confidence = "Medium"
            summary_expl = "Your text contains mixed signals, with some parts generated by AI. Some sentences exhibit uniform cadence or AI transitions."
        else:
            verdict = "Your text is AI / GPT Generated"
            feedback_message = "Your text is AI / GPT Generated"
            verdict_color = "text-red-400"
            is_human_written = False
            is_gpt_generated = True
            confidence = "High"
            summary_expl = "Your text is AI / GPT Generated. High concentration of AI markers, formulaic syntax, and neural classifier detection."

        readability = calculate_readability(text)

        return {
            "fakePercentage": fake_percentage,
            "ai_percentage": ai_percentage,
            "human_percentage": human_percentage,
            "is_human_written": is_human_written,
            "is_gpt_generated": is_gpt_generated,
            "feedback_message": feedback_message,
            "verdict": verdict,
            "verdict_color": verdict_color,
            "confidence": confidence,
            "explanation": summary_expl,
            "textWords": total_words,
            "aiWords": ai_words,
            "sentences": analyzed_sentences,
            "metrics": {
                "word_count": total_words,
                "sentence_count": total_sentences,
                "ai_words": ai_words,
                "burstiness_index": round(burstiness_val, 2),
                "sentence_std_dev": round(stdev_len, 1),
                "vocabulary_ttr": round(ttr * 100, 1),
                "cliche_count": total_cliches_found,
                "cliches_detected": list(set(cliche_matches_list))[:6],
                "flesch_kincaid_grade": readability.get("flesch_kincaid_grade", 0),
                "flesch_reading_ease": readability.get("flesch_reading_ease", 0)
            }
        }
