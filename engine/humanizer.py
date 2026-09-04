"""
AI Content Humanizer Engine.
Restructures sentence cadence, injects burstiness, eliminates AI tropes/clichés,
and converts formulaic syntax into authentic human-styled prose designed to score under 20% AI.
"""

import re
import random
from typing import Dict, Any, List, Optional
import httpx
from .linguistics import (
    split_sentences,
    tokenize_words,
    AI_CLICHE_PATTERNS,
    CONTRACTIONS
)

# Natural sentence starters by tone to replace robotic transitions
TRANSITION_REPLACEMENTS = {
    "natural": [
        ("furthermore,", ["Also,", "On top of that,", "What's more,", ""]),
        ("moreover,", ["Plus,", "Beyond that,", "And besides,", ""]),
        ("additionally,", ["Also,", "Another thing is,", "At the same time,", ""]),
        ("in addition,", ["Along with that,", "Plus,", ""]),
        ("consequently,", ["As a result,", "So,", "Because of this,"]),
        ("subsequently,", ["After that,", "Later on,", "Then,"]),
        ("importantly,", ["The key thing is,", "Notice that,", ""]),
        ("crucially,", ["Most importantly,", "The big takeaway is,", ""]),
        ("ultimately,", ["At the end of the day,", "When you look at it,", "In the end,"]),
        ("in summary,", ["All in all,", "To put it simply,", "Bottom line:"]),
        ("in conclusion,", ["Wrapping it up,", "All told,", "To wrap up,"]),
        ("on the other hand,", ["Then again,", "At the same time,", "Still,"])
    ],
    "academic": [
        ("furthermore,", ["Additionally,", "Likewise,", "Equally important,"]),
        ("moreover,", ["In tandem with this,", "Closely related,", ""]),
        ("additionally,", ["In complement,", "Further,", ""]),
        ("in addition,", ["Alongside this,", "In parallel,"]),
        ("consequently,", ["Accordingly,", "It follows that,", "Hence,"]),
        ("subsequently,", ["Following this,", "Thereafter,"]),
        ("importantly,", ["Notably,", "Saliently,"]),
        ("crucially,", ["Fundamentally,", "Central to this argument,"]),
        ("ultimately,", ["In synthesis,", "Taken together,"]),
        ("in summary,", ["In review,", "Taken as a whole,"]),
        ("in conclusion,", ["To conclude,", "In closing,"]),
        ("on the other hand,", ["In contrast,", "By comparison,"])
    ],
    "professional": [
        ("furthermore,", ["In addition,", "Also,", ""]),
        ("moreover,", ["What's more,", "Additionally,", ""]),
        ("additionally,", ["Along with this,", "Also,"]),
        ("in addition,", ["As well,", ""]),
        ("consequently,", ["Therefore,", "As such,"]),
        ("subsequently,", ["Next,", "Then,"]),
        ("importantly,", ["Notably,", "Key takeaway:"]),
        ("crucially,", ["Critically,", "Essential to note:"]),
        ("ultimately,", ["The bottom line is,", "In practice,"]),
        ("in summary,", ["In short,", "Summary:"]),
        ("in conclusion,", ["To summarize,", "In close,"]),
        ("on the other hand,", ["Alternatively,", "By contrast,"])
    ],
    "creative": [
        ("furthermore,", ["What's more,", "Even better,", ""]),
        ("moreover,", ["And then,", "Not just that—", ""]),
        ("additionally,", ["To sweeten the deal,", "Alongside it all,"]),
        ("in addition,", ["Paired with this,", ""]),
        ("consequently,", ["And so,", "Which is why,"]),
        ("subsequently,", ["Soon enough,", "Down the line,"]),
        ("importantly,", ["Here's the twist:", "Make no mistake,"]),
        ("crucially,", ["At its heart,", "The real spark is,"]),
        ("ultimately,", ["In the grand scheme,", "When the dust settles,"]),
        ("in summary,", ["The story here is simple:", "Plainly put,"]),
        ("in conclusion,", ["Where does that leave us?", "The final word:"]),
        ("on the other hand,", ["Yet,", "Flip the coin, and", "Still,"])
    ]
}

# Burstiness injection short sentences (creates high CV variance)
CADENCE_PUNCH_LINES = {
    "natural": [
        "It really makes a difference.",
        "That's just how it works.",
        "And it shows.",
        "The proof is right there.",
        "Simple as that.",
        "That's no small feat."
    ],
    "academic": [
        "This distinction is vital.",
        "The evidence supports this observation.",
        "The implications remain substantial.",
        "This warrants closer examination."
    ],
    "professional": [
        "This drives clear results.",
        "The value proposition is obvious.",
        "Execution remains key.",
        "That delivers real impact."
    ],
    "creative": [
        "Funny how that happens.",
        "Every detail counts.",
        "A striking difference indeed.",
        "The shift is palpable."
    ]
}

def match_case(original: str, replacement: str) -> str:
    """Matches the capitalization of the replacement to the original text."""
    if not original or not replacement:
        return replacement
    if original[0].isupper():
        return replacement[0].upper() + replacement[1:]
    return replacement[0].lower() + replacement[1:]

class AIHumanizer:
    def __init__(self):
        pass

    def humanize(
        self,
        text: str,
        tone: str = "natural",
        intensity: str = "balanced",
        use_ollama: bool = False,
        ollama_model: str = "llama3"
    ) -> Dict[str, Any]:
        """
        Humanizes AI-generated text by altering cadence, breaking monotonous rhythms,
        and eliminating recognizable LLM tropes to achieve human scores (< 20% AI).
        """
        text = text.strip() if text else ""
        if not text:
            return {
                "original_text": "",
                "humanized_text": "",
                "changes_applied": [],
                "tone": tone,
                "intensity": intensity,
                "source": "empty"
            }

        if use_ollama:
            llm_result = self._try_ollama_humanize(text, tone, intensity, ollama_model)
            if llm_result:
                return llm_result

        return self._heuristic_humanize(text, tone, intensity)

    def _heuristic_humanize(self, text: str, tone: str, intensity: str) -> Dict[str, Any]:
        tone = tone.lower() if tone in ["natural", "academic", "professional", "creative"] else "natural"
        intensity = intensity.lower() if intensity in ["mild", "balanced", "aggressive"] else "balanced"

        changes_applied = []
        modified = text

        # Step 1: Replace AI Cliches with tone-appropriate human phrasing
        for pattern, info in AI_CLICHE_PATTERNS.items():
            regex = re.compile(pattern, re.IGNORECASE)
            
            def replace_callback(match):
                orig = match.group(0)
                repl = info.get(tone, info.get("natural", "explore"))
                return match_case(orig, repl)

            if regex.search(modified):
                modified = regex.sub(replace_callback, modified)
                changes_applied.append(f"Replaced trope '{info['desc']}'")

        # Step 2: Fix robotic transitions & formulaic openers
        transitions = TRANSITION_REPLACEMENTS.get(tone, TRANSITION_REPLACEMENTS["natural"])
        for ai_term, repl_list in transitions:
            pattern = re.compile(re.escape(ai_term), re.IGNORECASE)
            if pattern.search(modified):
                replacement = random.choice(repl_list)
                if replacement == "":
                    modified = pattern.sub("", modified).strip()
                    modified = re.sub(r'(?<=[.!?]\s),', '', modified)
                else:
                    modified = pattern.sub(replacement, modified)
                changes_applied.append(f"Softened rigid transition '{ai_term}'")

        # Step 3: Inject natural contractions (essential for passing AI detectors < 20%)
        if tone in ["natural", "creative", "professional"] or intensity in ["balanced", "aggressive"]:
            for formal, contracted in CONTRACTIONS.items():
                pattern = re.compile(formal)
                if pattern.search(modified):
                    modified = pattern.sub(contracted, modified)
                    changes_applied.append(f"Injected natural contraction '{contracted}'")

        # Step 4: Burstiness & Cadence Restructuring
        raw_sentences = split_sentences(modified)
        restructured_sentences = []

        punch_pool = CADENCE_PUNCH_LINES.get(tone, CADENCE_PUNCH_LINES["natural"]).copy()
        random.shuffle(punch_pool)

        # In both balanced and aggressive modes, inject burstiness variance
        for idx, sent in enumerate(raw_sentences):
            words = tokenize_words(sent)
            word_count = len(words)

            # Split long monotonous compound sentences (18+ words) into natural conversational beats
            if intensity in ["balanced", "aggressive"] and word_count >= 18:
                split_points = [
                    (r',\s+and\s+', '. In fact, '),
                    (r',\s+but\s+', '. Yet, '),
                    (r',\s+while\s+', '. Meanwhile, '),
                    (r';\s+', '. '),
                    (r',\s+which\s+', '. This ')
                ]
                for sp_pattern, sp_replace in split_points:
                    if re.search(sp_pattern, sent, re.IGNORECASE):
                        sent = re.sub(sp_pattern, sp_replace, sent, count=1)
                        changes_applied.append("Broken uniform clauses into dynamic human cadence")
                        break

            if sent and sent[0].islower():
                sent = sent[0].upper() + sent[1:]

            restructured_sentences.append(sent)

            # Inject a short punchline to maximize burstiness standard deviation
            if (intensity == "aggressive" and idx == 0 and len(raw_sentences) >= 2) or \
               (intensity == "balanced" and idx == 1 and len(raw_sentences) >= 3):
                if punch_pool:
                    punch = punch_pool.pop()
                    restructured_sentences.append(punch)
                    changes_applied.append(f"Injected high-burstiness punch: '{punch}'")

        # Reassemble text
        humanized_text = " ".join(restructured_sentences)
        humanized_text = re.sub(r'\s+', ' ', humanized_text)
        humanized_text = re.sub(r'\s+([.,!?;:])', r'\1', humanized_text)
        humanized_text = re.sub(r'([.!?])\s*([a-z])', lambda m: f"{m.group(1)} {m.group(2).upper()}", humanized_text)
        humanized_text = humanized_text.strip()

        unique_changes = list(dict.fromkeys(changes_applied))

        return {
            "original_text": text,
            "humanized_text": humanized_text,
            "changes_applied": unique_changes[:8],
            "tone": tone,
            "intensity": intensity,
            "source": "heuristic_engine"
        }

    def _try_ollama_humanize(
        self,
        text: str,
        tone: str,
        intensity: str,
        model: str
    ) -> Optional[Dict[str, Any]]:
        prompt = (
            f"Rewrite the following text to sound 100% human-written, natural, and score below 15% on AI detectors. "
            f"Tone: {tone}. Intensity: {intensity}. "
            f"Drastically vary sentence lengths (mix short 3-word punchy sentences with compound sentences). "
            f"Eliminate ALL AI clichés (delve into, crucial role, testament to, rich tapestry, furthermore, moreover, in conclusion). "
            f"Use natural contractions (it's, don't, can't, we've). "
            f"Return ONLY the rewritten paragraph without commentary:\n\n{text}"
        )
        try:
            with httpx.Client(timeout=8.0) as client:
                res = client.post(
                    "http://localhost:11434/api/generate",
                    json={
                        "model": model,
                        "prompt": prompt,
                        "stream": False
                    }
                )
                if res.status_code == 200:
                    data = res.json()
                    rewritten = data.get("response", "").strip()
                    if rewritten:
                        return {
                            "original_text": text,
                            "humanized_text": rewritten,
                            "changes_applied": [
                                f"Rewritten via local Ollama ({model})",
                                f"Tone calibrated to {tone}",
                                "High burstiness & natural contractions applied"
                            ],
                            "tone": tone,
                            "intensity": intensity,
                            "source": f"ollama_{model}"
                        }
        except Exception:
            pass
        return None
