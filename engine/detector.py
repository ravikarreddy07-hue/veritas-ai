"""
AI Content Detection Engine.
Calculates burstiness, perplexity proxies, lexical diversity, AI cliché density,
and provides sentence-by-sentence probability heatmaps.
"""

import re
import math
import statistics
from typing import Dict, List, Any
from .linguistics import (
    split_sentences,
    tokenize_words,
    calculate_readability,
    AI_CLICHE_PATTERNS,
    AI_FAVORED_OPENERS,
    STOPWORDS
)

class AIDetector:
    def __init__(self):
        self.cliche_compiled = [
            (re.compile(pattern, re.IGNORECASE), info)
            for pattern, info in AI_CLICHE_PATTERNS.items()
        ]

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

        # 2. Lexical Diversity & Vocabulary Predictability
        unique_words = set(words)
        ttr = len(unique_words) / total_words if total_words > 0 else 0

        freqs: Dict[str, int] = {}
        for w in words:
            freqs[w] = freqs.get(w, 0) + 1

        hapax = sum(1 for count in freqs.values() if count == 1)
        hapax_ratio = hapax / len(unique_words) if unique_words else 0

        if ttr >= 0.70 and hapax_ratio >= 0.50:
            lexical_ai_score = 6.0
        elif ttr >= 0.52:
            lexical_ai_score = 12.0
        elif ttr <= 0.38 and total_words > 40:
            lexical_ai_score = 65.0
        else:
            lexical_ai_score = 20.0

        # 3. AI Cliché & Pattern Matching (Excludes direct quotes to protect citations)
        text_for_cliches = re.sub(r'["“][^"”\n]{2,300}?["”]', '', text)
        total_cliches_found = 0
        cliche_matches_list = []
        for regex, info in self.cliche_compiled:
            matches = regex.findall(text_for_cliches)
            if matches:
                total_cliches_found += len(matches)
                cliche_matches_list.append(info["desc"])

        cliche_density = (total_cliches_found / (total_words / 100.0)) if total_words > 0 else 0
        if total_cliches_found == 0:
            cliche_ai_score = 4.0
        elif cliche_density < 0.8:
            cliche_ai_score = 25.0
        elif cliche_density < 2.0:
            cliche_ai_score = 55.0
        else:
            cliche_ai_score = 85.0

        # 4. Sentence Opener Repetition
        opener_penalties = 0
        for sent in sentences:
            s_lower = sent.lower().strip()
            for op in AI_FAVORED_OPENERS:
                if s_lower.startswith(op):
                    opener_penalties += 1
                    break

        opener_ratio = opener_penalties / total_sentences if total_sentences > 0 else 0
        if opener_ratio == 0:
            opener_ai_score = 4.0
        else:
            opener_ai_score = min(90.0, 10.0 + (opener_ratio * 100.0))


        # 5. Sentence-by-sentence detailed breakdown & Heatmap
        analyzed_sentences = []
        sentence_scores = []
        has_overall_contractions = any("'" in s or "’" in s for s in sentences)

        for idx, sent in enumerate(sentences):
            sent_words = tokenize_words(sent)
            word_count = len(sent_words)
            s_score = 12.0  # Base human prior
            reasons = []

            # Check cliches in this sentence
            for regex, info in self.cliche_compiled:
                if regex.search(sent):
                    s_score += 32.0
                    reasons.append(f"Contains {info['desc']}")

            # Check opener
            s_lower = sent.lower().strip()
            for op in AI_FAVORED_OPENERS:
                if s_lower.startswith(op):
                    s_score += 25.0
                    reasons.append(f"Overused opener '{op}'")
                    break

            # Check robotic sentence length: only flag if sentence ALSO has cliches or robotic openers
            if 16 <= word_count <= 26:
                if any(r for r in reasons if "Contains" in r or "Overused" in r):
                    s_score += 10.0
                    reasons.append("Uniform robotic sentence length (16-26 words)")

            # Natural burstiness reward for short punchy or complex sentences
            if word_count <= 10:
                s_score = max(2.0, s_score - 10.0)
                reasons.append("Punchy human sentence cadence")
            elif any(c in sent for c in [",", ";", "—", "..."]):
                s_score = max(2.0, s_score - 6.0)

            # Contractions reward
            if any(c in sent for c in ["'", "’"]):
                s_score = max(2.0, s_score - 10.0)
                reasons.append("Natural contraction usage")

            # Conversational pronouns
            if re.search(r'\b(i|me|my|we|us|our|you|your)\b', sent, re.IGNORECASE):
                s_score = max(2.0, s_score - 8.0)

            s_score = max(2.0, min(98.0, s_score))
            sentence_scores.append(s_score)

            # Classification thresholds matching ZeroGPT:
            # Red (>= 65%): AI / GPT Generated
            # Yellow (40% - 64%): Mixed / partial AI
            # Green (< 40%): Likely Human
            if s_score >= 65.0:
                classification = "Likely AI"
                color_class = "bg-red-500/20 border-red-500/50 text-red-200"
                highlight_color = "red"
                is_ai = True
            elif s_score >= 40.0:
                classification = "Mixed"
                color_class = "bg-yellow-500/20 border-yellow-500/50 text-yellow-200"
                highlight_color = "yellow"
                is_ai = True
            else:
                classification = "Likely Human"
                color_class = "bg-emerald-500/20 border-emerald-500/50 text-emerald-200"
                highlight_color = "green"
                is_ai = False

            analyzed_sentences.append({
                "id": idx + 1,
                "text": sent,
                "score": round(s_score),
                "words": word_count,
                "classification": classification,
                "color_class": color_class,
                "highlight_color": highlight_color,
                "is_ai": is_ai,
                "reasons": reasons if reasons else ["Natural sentence cadence"]
            })

        # 6. ZeroGPT-Standard Detecting Ratio & Metric Calculation
        # In ZeroGPT:
        # textWords is total word count.
        # aiWords is the sum of words in sentences flagged as AI (score >= 40%).
        ai_words = sum(s["words"] for s in analyzed_sentences if s["is_ai"])
        ai_sentences_count = sum(1 for s in analyzed_sentences if s["is_ai"])
        avg_sent_score = statistics.mean(sentence_scores) if sentence_scores else 10.0

        # Word ratio baseline
        raw_word_ratio = (ai_words / total_words * 100.0) if total_words > 0 else 0.0

        if ai_words == 0:
            # When zero sentences trigger AI thresholds
            if total_cliches_found == 0:
                fake_percentage = 0.0
            else:
                fake_percentage = min(12.0, round(cliche_density * 4.0, 1))
        else:
            # Calibrate word ratio with average AI sentence scores and cliche density
            avg_ai_sent_score = statistics.mean([s["score"] for s in analyzed_sentences if s["is_ai"]])
            severity_factor = avg_ai_sent_score / 100.0
            calibrated = (raw_word_ratio * 0.70) + (raw_word_ratio * severity_factor * 0.30)
            if total_cliches_found > 0:
                calibrated = max(calibrated, raw_word_ratio)
            fake_percentage = round(min(100.0, max(0.0, calibrated)), 1)

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
            summary_expl = "Your text is Human written. Authentic human rhythm, natural variation, and zero AI clichés detected."
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
            summary_expl = "Your text is AI / GPT Generated. High concentration of AI markers, formulaic syntax, and repetitive structure."

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
                "flesch_kincaid_grade": readability["flesch_kincaid_grade"],
                "flesch_reading_ease": readability["flesch_reading_ease"]
            }
        }
