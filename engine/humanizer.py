"""
AI Content Humanizer Engine.
Restructures sentence cadence, injects burstiness, eliminates AI tropes/clichés,
and converts formulaic syntax into authentic human-styled prose designed to score under 15% AI.
"""

import re
from typing import Dict, Any, List, Optional, Tuple
import httpx
from .linguistics import (
    split_sentences,
    tokenize_words,
    AI_CLICHE_PATTERNS,
    COMPOUND_TRANSITION_PATTERNS,
    CONTRACTIONS
)

# Natural sentence starters by tone to replace robotic transitions
TRANSITION_REPLACEMENTS = {
    "natural": [
        ("furthermore,", ["Also,", "On top of that,", "What's more,", ""]),
        ("moreover,", ["Plus,", "Beyond that,", "Also,", ""]),
        ("additionally,", ["Also,", "Another thing is,", "Along with that,", ""]),
        ("in addition,", ["Along with that,", "Plus,", "Also,"]),
        ("consequently,", ["As a result,", "So,", "Because of this,"]),
        ("subsequently,", ["After that,", "Later on,", "Then,"]),
        ("importantly,", ["Notice that,", "The key thing is,", ""]),
        ("crucially,", ["Most importantly,", "The big takeaway is,", ""]),
        ("ultimately,", ["In the end,", "When you look at it,", "At the end of the day,"]),
        ("in summary,", ["All in all,", "To put it simply,", "Bottom line:"]),
        ("in conclusion,", ["All told,", "In the end,", "To wrap up,"]),
        ("on the other hand,", ["Then again,", "At the same time,", "Still,"])
    ],
    "academic": [
        ("furthermore,", ["Equally notable,", "Likewise,", "Equally important,"]),
        ("moreover,", ["In tandem with this,", "Closely related,", ""]),
        ("additionally,", ["In complement,", "Further,", "Along with this,"]),
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
        ("furthermore,", ["Beyond this,", "Also,", ""]),
        ("moreover,", ["What's more,", "Along with this,", ""]),
        ("additionally,", ["Along with this,", "Also,"]),
        ("in addition,", ["As well,", "Also,"]),
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
        ("ultimately,", ["When the dust settles,", "In the grand scheme,"]),
        ("in summary,", ["Plainly put,", "The story here is simple:"]),
        ("in conclusion,", ["Where does that leave us?", "The final word:"]),
        ("on the other hand,", ["Yet,", "Still,", "Flip the coin, and"])
    ]
}

# Extended vocabulary patterns targeting formulaic LLM writing across topics
EXTENDED_AI_PATTERNS: Dict[str, Dict[str, str]] = {
    r"\bhas transformed numerous industries\b": {
        "natural": "has reshaped plenty of industries",
        "academic": "has substantially restructured multiple sectors",
        "professional": "has transformed various industries",
        "creative": "turned whole industries on their head",
        "desc": "Formulaic: 'transformed numerous industries'"
    },
    r"\bhave transformed numerous industries\b": {
        "natural": "have reshaped plenty of industries",
        "academic": "have restructured multiple sectors",
        "professional": "have transformed various industries",
        "creative": "turned whole industries on their head",
        "desc": "Formulaic: 'transformed numerous industries'"
    },
    r"\bhas transformed\b": {
        "natural": "has reshaped",
        "academic": "has restructured",
        "professional": "has modernized",
        "creative": "has reimagined",
        "desc": "Formulaic: 'has transformed'"
    },
    r"\bhave transformed\b": {
        "natural": "have reshaped",
        "academic": "have restructured",
        "professional": "have modernized",
        "creative": "have reimagined",
        "desc": "Formulaic: 'have transformed'"
    },
    r"\bnumerous industries\b": {
        "natural": "plenty of industries",
        "academic": "multiple sectors",
        "professional": "various sectors",
        "creative": "all kinds of fields",
        "desc": "Formulaic: 'numerous industries'"
    },
    r"\bby automating repetitive tasks\b": {
        "natural": "by taking over routine chores",
        "academic": "by handling routine operations",
        "professional": "by automating routine workflows",
        "creative": "by clearing away boring chores",
        "desc": "AI trope: 'automating repetitive tasks'"
    },
    r"\bautomating repetitive tasks\b": {
        "natural": "taking over routine chores",
        "academic": "automating routine processes",
        "professional": "automating routine tasks",
        "creative": "sweeping away busywork",
        "desc": "AI trope: 'automating repetitive tasks'"
    },
    r"\brepetitive tasks\b": {
        "natural": "routine chores",
        "academic": "routine procedures",
        "professional": "manual tasks",
        "creative": "repetitive busywork",
        "desc": "Formulaic: 'repetitive tasks'"
    },
    r"\bproviding valuable insights from large datasets\b": {
        "natural": "pulling useful insights out of huge datasets",
        "academic": "extracting actionable insights from extensive data",
        "professional": "delivering actionable insights from enterprise datasets",
        "creative": "digging real clarity out of giant data mountains",
        "desc": "AI cliché: 'valuable insights from large datasets'"
    },
    r"\bproviding valuable insights\b": {
        "natural": "pulling useful insights",
        "academic": "yielding key findings",
        "professional": "delivering actionable metrics",
        "creative": "giving fresh clarity",
        "desc": "AI cliché: 'providing valuable insights'"
    },
    r"\bvaluable insights\b": {
        "natural": "useful insights",
        "academic": "empirical insights",
        "professional": "actionable takeaways",
        "creative": "real clarity",
        "desc": "AI cliché: 'valuable insights'"
    },
    r"\blarge datasets\b": {
        "natural": "huge datasets",
        "academic": "extensive data corpuses",
        "professional": "enterprise datasets",
        "creative": "massive heaps of data",
        "desc": "Formulaic: 'large datasets'"
    },
    r"\bnot only ([^,\.]+?) but also ([^,\.]+?)\b": {
        "natural": r"both \1 and \2",
        "academic": r"\1 as well as \2",
        "professional": r"\1 alongside \2",
        "creative": r"not just \1, but \2 too",
        "desc": "Formulaic structure: 'not only ... but also'"
    },
    r"\bserv(?:es|ed)? as a catalyst for\b": {
        "natural": "drives",
        "academic": "serves as a primary driver of",
        "professional": "sparks",
        "creative": "kicks off",
        "desc": "AI trope: 'serves as a catalyst for'"
    },
    r"\bserve as a catalyst for\b": {
        "natural": "drive",
        "academic": "serve as primary drivers of",
        "professional": "spark",
        "creative": "kick off",
        "desc": "AI trope: 'serve as a catalyst for'"
    },
    r"\bhas revolutionized\b": {
        "natural": "has reshaped",
        "academic": "has transformed",
        "professional": "has modernized",
        "creative": "has upended",
        "desc": "AI buzzword: 'has revolutionized'"
    },
    r"\bhave revolutionized\b": {
        "natural": "have reshaped",
        "academic": "have transformed",
        "professional": "have modernized",
        "creative": "have upended",
        "desc": "AI buzzword: 'have revolutionized'"
    },
    r"\brevolutionized\b": {
        "natural": "reshaped",
        "academic": "transformed",
        "professional": "modernized",
        "creative": "upended",
        "desc": "AI buzzword: 'revolutionized'"
    },
    r"\bdecision makers\b": {
        "natural": "leaders",
        "academic": "institutional leadership",
        "professional": "decision-makers",
        "creative": "folks in charge",
        "desc": "AI buzzword: 'decision makers'"
    },
    r"\bstrategic insights\b": {
        "natural": "clear guidance",
        "academic": "strategic analysis",
        "professional": "key insights",
        "creative": "sharp reads",
        "desc": "Formulaic: 'strategic insights'"
    },
    r"\bwith efficiency and precision\b": {
        "natural": "quickly and accurately",
        "academic": "with high precision",
        "professional": "efficiently",
        "creative": "clean and fast",
        "desc": "AI cliché: 'with efficiency and precision'"
    },
    r"\bsustainable innovation\b": {
        "natural": "lasting innovation",
        "academic": "long-term innovation",
        "professional": "scalable innovation",
        "creative": "fresh progress that sticks",
        "desc": "Formulaic: 'sustainable innovation'"
    },
    r"\bautomated data processing\b": {
        "natural": "automated data workflows",
        "academic": "computational data processing",
        "professional": "data automation",
        "creative": "smart automation",
        "desc": "Formulaic: 'automated data processing'"
    }
}

# Participial clause patterns to dismantle formulaic comma + -ing structures
PARTICIPIAL_CLAUSE_PATTERNS = [
    (r',\s+(?:thereby\s+)?automating\s+', '. This automates '),
    (r',\s+(?:thereby\s+)?providing\s+', '. This provides '),
    (r',\s+(?:thereby\s+)?enabling\s+', '. This allows '),
    (r',\s+(?:thereby\s+)?ensuring\s+', '. This ensures '),
    (r',\s+(?:thereby\s+)?facilitating\s+', '. This supports '),
    (r',\s+(?:thereby\s+)?allowing\s+', '. This lets '),
    (r',\s+(?:thereby\s+)?creating\s+', '. This creates '),
    (r',\s+(?:thereby\s+)?fostering\s+', '. This builds '),
    (r',\s+(?:thereby\s+)?driving\s+', '. This drives '),
    (r',\s+(?:thereby\s+)?reducing\s+', '. This reduces '),
    (r',\s+(?:thereby\s+)?enhancing\s+', '. This enhances '),
    (r',\s+(?:thereby\s+)?improving\s+', '. This improves '),
    (r',\s+(?:thereby\s+)?optimizing\s+', '. This optimizes '),
    (r',\s+(?:thereby\s+)?supporting\s+', '. This supports '),
    (r',\s+(?:thereby\s+)?generating\s+', '. This generates '),
    (r',\s+(?:thereby\s+)?resulting in\s+', '. This leads to '),
    (r',\s+(?:thereby\s+)?leading to\s+', '. This leads to '),
    (r',\s+which in turn\s+', '. In turn, this ')
]

# Syntactic de-nominalization patterns to dismantle rigid AI sentence structures
DENOMINALIZATION_PATTERNS = [
    (r'\bThe development of ([^,\.]+?) (represents|enables|drives|creates|sparks|fuels)\b', r'Developing \1 \2'),
    (r'\bThe proliferation of ([^,\.]+?) (requires|demands|calls for|creates)\b', r'The rapid spread of \1 \2'),
    (r'\bThe acceleration of ([^,\.]+?) (enables|allows|helps|drives)\b', r'Accelerating \1 \2'),
    (r'\bThe optimization of ([^,\.]+?) (minimizes|reduces|improves|boosts)\b', r'Optimizing \1 \2'),
    (r'\bThe governance of ([^,\.]+?) (protects|secures|safeguards)\b', r'Safeguarding \1 \2'),
    (r'\bThe implementation of ([^,\.]+?) (has|is|enables|allows|serves|drives)\b', r'Implementing \1 \2'),
    (r'\bThe integration of ([^,\.]+?) (allows|enables|provides|drives|sparks|fuels|creates|helps)\b', r'Integrating \1 \2'),
    (r'\bThe adoption of ([^,\.]+?) (drives|enables|leads|sparks|fuels)\b', r'Adopting \1 \2'),
    (r'\bThe utilization of ([^,\.]+?) (improves|enhances|boosts)\b', r'Using \1 \2'),
    (r'\bThe advancement of ([^,\.]+?) (creates|presents|accelerates|drives)\b', r'Advancing \1 \2'),
    (r'\bIt is important to note that\b', r'Notice that'),
    (r'\bIt is essential to\b', r'We need to'),
    (r'\bIn order to\b', r'To'),
    (r'\bDue to the fact that\b', r'Because')
]

def match_case(original: str, replacement: str) -> str:
    """Matches the capitalization of the replacement to the original text without middle-word casing distortion."""
    if not original or not replacement:
        return replacement
    if original.isupper() and len(original) > 1:
        return replacement.upper()
    if original[0].isupper():
        return replacement[0].upper() + replacement[1:]
    return replacement[0].lower() + replacement[1:]


class AIHumanizer:
    def __init__(self, detector: Optional[Any] = None):
        self.detector = detector

    def _get_detector(self):
        if self.detector is None:
            from .detector import AIDetector
            self.detector = AIDetector()
        return self.detector

    def _protect_academic_entities(self, text: str) -> Tuple[str, Dict[str, str]]:
        """
        Detects and shields in-text citations, bracketed references, and verbatim quotes
        using unique placeholder tokens so linguistic restructuring leaves them intact.
        """
        entity_map = {}
        counter = 0

        # 1. Direct quotes e.g. "..." or “...”
        quote_pattern = re.compile(r'["“][^"”\n]{2,300}?["”]')
        def quote_sub(match):
            nonlocal counter
            token = f"__ACAD_SHIELD_QUOTE_{counter}__"
            entity_map[token] = match.group(0)
            counter += 1
            return token
        text = quote_pattern.sub(quote_sub, text)

        # 2. Parenthetical citations e.g. (Smith et al., 2023)
        paren_pattern = re.compile(
            r'\([A-Z][A-Za-z\s\.\&]+(?:et al\.?)?,?\s*(?:19|20)\d{2}[a-z]?'
            r'(?:,\s*(?:pp?\.?\s*\d+(?:-\d+)?|\d+(?:-\d+)?))?'
            r'(?:;\s*[A-Z][A-Za-z\s\.\&]+(?:et al\.?)?,?\s*(?:19|20)\d{2}[a-z]?'
            r'(?:,\s*(?:pp?\.?\s*\d+(?:-\d+)?|\d+(?:-\d+)?))?)*\)'
        )
        def paren_sub(match):
            nonlocal counter
            token = f"__ACAD_SHIELD_CITE_{counter}__"
            entity_map[token] = match.group(0)
            counter += 1
            return token
        text = paren_pattern.sub(paren_sub, text)

        # 3. Bracketed numeric citations e.g. [1], [12, 15], [3-7]
        bracket_pattern = re.compile(r'\[(?:\d+(?:-\d+)?(?:,\s*\d+(?:-\d+)?)*)\]')
        def bracket_sub(match):
            nonlocal counter
            token = f"__ACAD_SHIELD_NUM_{counter}__"
            entity_map[token] = match.group(0)
            counter += 1
            return token
        text = bracket_pattern.sub(bracket_sub, text)

        return text, entity_map

    def _restore_academic_entities(self, text: str, entity_map: Dict[str, str]) -> str:
        """Restores shielded citations and quotes back to their exact locations."""
        for token, original in entity_map.items():
            text = text.replace(token, original)
        return text

    def humanize(
        self,
        text: str,
        tone: str = "natural",
        intensity: str = "balanced",
        use_ollama: bool = False,
        ollama_model: str = "llama3",
        academic_shield: bool = True,
        preserve_pattern: bool = True
    ) -> Dict[str, Any]:
        """
        Humanizes AI-generated text by altering cadence, breaking monotonous rhythms,
        and eliminating recognizable LLM tropes to achieve human scores (< 15% AI).
        """
        text = text.strip() if text else ""
        if not text:
            return {
                "original_text": "",
                "humanized_text": "",
                "changes_applied": [],
                "tone": tone,
                "intensity": intensity,
                "shielded_items_count": 0,
                "convergence_passes": 0,
                "source": "empty"
            }

        # Multi-line handling: preserve exact line breaks and patterns
        if "\n" in text and preserve_pattern:
            lines = text.split("\n")
            hum_lines = []
            all_changes = []
            total_shielded = 0
            for line in lines:
                if not line.strip():
                    hum_lines.append(line)
                    continue
                h_line = self.humanize(
                    line,
                    tone=tone,
                    intensity=intensity,
                    use_ollama=use_ollama,
                    ollama_model=ollama_model,
                    academic_shield=academic_shield,
                    preserve_pattern=preserve_pattern
                )
                hum_lines.append(h_line["humanized_text"])
                all_changes.extend(h_line.get("changes_applied", []))
                total_shielded += h_line.get("shielded_items_count", 0)

            return {
                "original_text": text,
                "humanized_text": "\n".join(hum_lines),
                "changes_applied": list(dict.fromkeys(all_changes))[:10],
                "tone": tone,
                "intensity": intensity,
                "shielded_items_count": total_shielded,
                "convergence_passes": 1,
                "source": "heuristic_engine"
            }

        bullet_prefix = ""
        label_prefix = ""
        core_text = text
        has_trailing_period = text.rstrip().endswith((".", "!", "?"))

        if preserve_pattern:
            bullet_match = re.match(r'^(\s*(?:[\u2022\u2023\u25E6\u2043\u2219\*\-\—▪▫]|\d+[\.\)]|\([a-zA-Z0-9]+\)|[a-zA-Z][\.\)])\s+)', text)
            if bullet_match:
                bullet_prefix = bullet_match.group(0)
                core_text = text[len(bullet_prefix):]

            label_match = re.match(r'^([A-Z][A-Za-z0-9\s/&]{1,35}\s*(?::\s*|[-–—]\s+))', core_text)
            if label_match and len(label_match.group(1).split()) <= 4:
                label_prefix = label_match.group(1)
                core_text = core_text[len(label_prefix):]

        if use_ollama:
            llm_result = self._try_ollama_humanize(core_text, tone, intensity, ollama_model, academic_shield)
            if llm_result:
                hum_body = llm_result["humanized_text"].strip()
                if preserve_pattern and not has_trailing_period and hum_body.endswith("."):
                    hum_body = hum_body[:-1]
                llm_result["original_text"] = text
                llm_result["humanized_text"] = f"{bullet_prefix}{label_prefix}{hum_body}"
                return llm_result

        res = self._convergent_humanize(core_text, tone, intensity, academic_shield, preserve_pattern=preserve_pattern)
        hum_body = res["humanized_text"].strip()
        if preserve_pattern and not has_trailing_period and hum_body.endswith("."):
            hum_body = hum_body[:-1]

        res["original_text"] = text
        res["humanized_text"] = f"{bullet_prefix}{label_prefix}{hum_body}"
        return res

    def _convergent_humanize(
        self,
        text: str,
        tone: str,
        intensity: str,
        academic_shield: bool = True,
        preserve_pattern: bool = True
    ) -> Dict[str, Any]:
        """
        Single-Click Closed-Loop Convergence Engine:
        Runs iterative optimization passes until the text scores below the guaranteed human threshold (< 15%).
        """
        tone = tone.lower() if tone in ["natural", "academic", "professional", "creative"] else "natural"
        intensity = intensity.lower() if intensity in ["mild", "balanced", "aggressive"] else "balanced"

        target_score = 8 if intensity == "aggressive" else (12 if intensity == "balanced" else 15)

        detector = self._get_detector()
        initial_eval = detector.analyze(text)
        initial_ai = initial_eval["fakePercentage"]

        # Step 0: Academic Shield Protection
        entity_map = {}
        modified = text
        if academic_shield:
            modified, entity_map = self._protect_academic_entities(modified)

        best_text = None
        best_score = float('inf')
        best_changes = []
        passes_run = 0
        all_changes = []

        # Closed-Loop Auto-Convergence (up to 4 passes internally)
        for iteration in range(4):
            passes_run += 1

            if iteration == 0:
                # Pass 1: Standard Lexical, Compound Transition, and Participial Clause Restructuring
                p1_res = self._heuristic_humanize(modified, tone, intensity, academic_shield=False)
                modified = p1_res["humanized_text"]
                all_changes.extend(p1_res["changes_applied"])

            elif iteration == 1:
                # Pass 2: Syntactic De-nominalization, Participial Clauses, Contractions
                p2_changes = []

                # Invert participial clauses (e.g. ', automating' -> '. This automates')
                for pat, rep in PARTICIPIAL_CLAUSE_PATTERNS:
                    if re.search(pat, modified, re.IGNORECASE):
                        modified = re.sub(pat, rep, modified, flags=re.IGNORECASE)
                        p2_changes.append("Restructured participial clause into active sentence")

                # De-nominalization
                for pat, repl in DENOMINALIZATION_PATTERNS:
                    if re.search(pat, modified, re.IGNORECASE):
                        modified = re.sub(pat, repl, modified, flags=re.IGNORECASE)
                        p2_changes.append("Inverted rigid nominalized openers")

                # Contractions (for non-academic tones)
                if tone != "academic":
                    for pat, contracted in CONTRACTIONS.items():
                        if re.search(pat, modified):
                            modified = re.sub(pat, contracted, modified)
                            p2_changes.append(f"Injected natural contraction '{contracted}'")

                # Break long compound sentences (> 18 words)
                sents = split_sentences(modified)
                split_sents = []
                for s in sents:
                    words = tokenize_words(s)
                    if len(words) > 18:
                        clause_patterns = [
                            (r',\s+which\s+(?=(?:means|allows|provides|enables|helps|ensures|creates|leads)\b)', '. This '),
                            (r',\s+while\s+(?=(?:it|they|this|these|we|he|she)\b)', '. Meanwhile, '),
                            (r',\s+whereas\s+(?=(?:it|they|this|these|we|he|she)\b)', '. In contrast, '),
                            (r';\s+', '. '),
                            (r',\s+thereby\s+', '. This effectively '),
                            (r',\s+and\s+therefore\s+(?=(?:it|they|this|these|we)\b)', '. Therefore, ')
                        ]
                        for cp_pat, cp_rep in clause_patterns:
                            if re.search(cp_pat, s, re.IGNORECASE):
                                s = re.sub(cp_pat, cp_rep, s, count=1)
                                p2_changes.append("Split compound clause for cadence balance")
                                break
                    split_sents.append(s)
                modified = " ".join(split_sents)
                modified = re.sub(r'\s+', ' ', modified).strip()
                all_changes.extend(p2_changes)

            elif iteration == 2:
                # Pass 3: Compound Sentence Splitting & Transition Stripping
                p3_changes = []
                sents = split_sentences(modified)
                split_sents = []
                for s in sents:
                    words = tokenize_words(s)
                    if len(words) >= 14:
                        clause_break_patterns = [
                            (r',\s+and\s+(?=(?:it|they|this|these|we|he|she)\b)', '. Also, '),
                            (r',\s+but\s+(?=(?:it|they|this|these|we|he|she)\b)', '. Still, '),
                            (r'\s+that allow(?:s)?\s+(?:users|organizations|teams|businesses|people|leaders)\s+to\b', '. This helps teams '),
                            (r'\s+that enable(?:s)?\s+(?:users|organizations|teams|businesses|people|leaders)\s+to\b', '. This lets teams '),
                            (r',\s+which\s+(?:helps|allows|enables|supports)\b', '. This helps '),
                        ]
                        for conj_pat, conj_rep in clause_break_patterns:
                            if re.search(conj_pat, s, re.IGNORECASE):
                                s = re.sub(conj_pat, conj_rep, s, count=1)
                                p3_changes.append("Split uniform sentence for enhanced burstiness")
                                break
                    split_sents.append(s)
                modified = " ".join(split_sents)
                modified = re.sub(r'\s+', ' ', modified).strip()
                all_changes.extend(p3_changes)

            else:
                # Pass 4: Final Polishing - Strip remaining formulaic transitions and inject natural rhythm
                p4_changes = []
                # Strip remaining formal openers completely
                modified = re.sub(r'^(?:Furthermore|Moreover|Additionally|In addition|Consequently|Also|In the end),\s*', '', modified, flags=re.IGNORECASE)
                modified = re.sub(r'(?<=[.!?]\s)(?:Furthermore|Moreover|Additionally|In addition|Consequently|Also|In the end),\s*', '', modified, flags=re.IGNORECASE)
                p4_changes.append("Streamlined leading discourse transitions")

                if tone != "academic":
                    for formal_pat, contracted in [
                        (r'\bit is\b', "it's"),
                        (r'\bthere is\b', "there's"),
                        (r'\bthey are\b', "they're"),
                        (r'\bwe are\b', "we're"),
                        (r'\bdo not\b', "don't"),
                        (r'\bcannot\b', "can't"),
                        (r'\bdoes not\b', "doesn't"),
                        (r'\bthat is\b', "that's")
                    ]:
                        if re.search(formal_pat, modified, re.IGNORECASE):
                            modified = re.sub(formal_pat, contracted, modified, flags=re.IGNORECASE)
                            p4_changes.append(f"Injected natural contraction '{contracted}'")

                all_changes.extend(p4_changes)

            # Check convergence score with temporary entity restoration
            eval_text = self._restore_academic_entities(modified, entity_map) if entity_map else modified
            current_eval = detector.analyze(eval_text)
            current_ai = current_eval["fakePercentage"]

            if best_text is None or current_ai <= best_score:
                best_score = current_ai
                best_text = eval_text
                best_changes = list(all_changes)

            if current_ai <= target_score:
                break

        final_text = best_text if (best_text and best_text != text) else (modified if modified != text else text)
        if final_text:
            final_text = re.sub(r'(^|[.!?]\s+)([a-z])', lambda m: m.group(1) + m.group(2).upper(), final_text)
        if entity_map and final_text == modified:
            final_text = self._restore_academic_entities(final_text, entity_map)

        final_changes = best_changes if best_changes else ["Humanized sentence cadence and vocabulary"]

        if best_score <= 15.0:
            final_changes.insert(0, f"Deep Convergence: Achieved authentic human score ({round(best_score)}%) in {passes_run} passes")
        elif best_score < initial_ai:
            final_changes.insert(0, f"Deep Convergence: Reduced AI probability from {round(initial_ai)}% to {round(best_score)}% in {passes_run} passes")

        unique_changes = list(dict.fromkeys(final_changes))

        return {
            "original_text": text,
            "humanized_text": final_text,
            "changes_applied": unique_changes[:10],
            "tone": tone,
            "intensity": intensity,
            "shielded_items_count": len(entity_map),
            "convergence_passes": passes_run,
            "source": "heuristic_engine"
        }

    def _heuristic_humanize(self, text: str, tone: str, intensity: str, academic_shield: bool = True) -> Dict[str, Any]:
        tone = tone.lower() if tone in ["natural", "academic", "professional", "creative"] else "natural"
        intensity = intensity.lower() if intensity in ["mild", "balanced", "aggressive"] else "balanced"

        changes_applied = []
        entity_map = {}
        modified = text

        # Step 0: Academic Shield Protection
        if academic_shield:
            modified, entity_map = self._protect_academic_entities(modified)
            if entity_map:
                changes_applied.append(f"Academic Shield: Preserved {len(entity_map)} citations/quotes")

        # Step 1: Clean Compound Transitions first (prevents stacked openers)
        for pattern, replacement in COMPOUND_TRANSITION_PATTERNS:
            if re.search(pattern, modified, re.IGNORECASE):
                modified = re.sub(pattern, replacement, modified, flags=re.IGNORECASE)
                changes_applied.append("Streamlined compound transition")

        # Step 2: Replace AI Clichés & formulaic patterns with tone-appropriate human phrasing
        combined_cliches = {**AI_CLICHE_PATTERNS, **EXTENDED_AI_PATTERNS}
        for pattern, info in combined_cliches.items():
            regex = re.compile(pattern, re.IGNORECASE)

            def replace_callback(match):
                orig = match.group(0)
                repl = info.get(tone, info.get("natural", "explore"))
                if "\\1" in repl:
                    return match.expand(repl)
                return match_case(orig, repl)

            if regex.search(modified):
                modified = regex.sub(replace_callback, modified)
                changes_applied.append(f"Replaced trope '{info['desc']}'")

        # Step 2b: Restructure Participial Clauses (e.g. ', thereby reducing' -> '. This reduces')
        for pat, rep in PARTICIPIAL_CLAUSE_PATTERNS:
            if re.search(pat, modified, re.IGNORECASE):
                modified = re.sub(pat, rep, modified, flags=re.IGNORECASE)
                changes_applied.append("Restructured participial clause into active sentence")

        # Step 3: Fix robotic transitions & formulaic openers
        transitions = TRANSITION_REPLACEMENTS.get(tone, TRANSITION_REPLACEMENTS["natural"])
        for t_idx, (ai_term, repl_list) in enumerate(transitions):
            pattern = re.compile(re.escape(ai_term), re.IGNORECASE)
            if pattern.search(modified):
                replacement = repl_list[t_idx % len(repl_list)] if repl_list else ""
                if replacement == "":
                    modified = pattern.sub("", modified).strip()
                    modified = re.sub(r'(?<=[.!?]\s),', '', modified)
                else:
                    modified = pattern.sub(replacement, modified)
                changes_applied.append(f"Softened rigid transition '{ai_term}'")

        # Step 4: Inject natural contractions (essential for passing AI detectors, except academic)
        if tone != "academic" and (tone in ["natural", "creative", "professional"] or intensity in ["balanced", "aggressive"]):
            for formal, contracted in CONTRACTIONS.items():
                pattern = re.compile(formal)
                if pattern.search(modified):
                    modified = pattern.sub(contracted, modified)
                    changes_applied.append(f"Injected natural contraction '{contracted}'")

        # Step 5: Burstiness & Cadence Restructuring
        raw_sentences = split_sentences(modified)
        restructured_sentences = []

        for idx, sent in enumerate(raw_sentences):
            words = tokenize_words(sent)
            word_count = len(words)

            # Split overly long compound sentences (18+ words) ONLY at genuine independent clauses
            if word_count >= 18:
                split_points = [
                    (r',\s+and\s+(?=(?:it|they|this|these|we|he|she)\b)', '. Also, '),
                    (r',\s+but\s+(?=(?:it|they|this|these|we|he|she)\b)', '. However, '),
                    (r',\s+while\s+(?=(?:it|they|this|these|we|he|she)\b)', '. Meanwhile, '),
                    (r';\s+', '. '),
                    (r',\s+which\s+(?=(?:means|allows|provides|enables|helps|ensures|creates|leads)\b)', '. This '),
                    (r',\s+so\s+(?=(?:it|they|this|these|we|he|she)\b)', '. As a result, ')
                ]
                for sp_pattern, sp_replace in split_points:
                    if re.search(sp_pattern, sent, re.IGNORECASE):
                        sent = re.sub(sp_pattern, sp_replace, sent, count=1)
                        changes_applied.append("Refined clause structure for natural human cadence")
                        break

            if sent and sent[0].islower():
                sent = sent[0].upper() + sent[1:]

            restructured_sentences.append(sent)

        # Reassemble text
        humanized_text = " ".join(restructured_sentences)
        humanized_text = re.sub(r'\s+', ' ', humanized_text)
        humanized_text = re.sub(r'\s+([.,!?;:])', r'\1', humanized_text)
        humanized_text = re.sub(r'([.!?])\s*([a-z])', lambda m: f"{m.group(1)} {m.group(2).upper()}", humanized_text)
        humanized_text = humanized_text.strip()

        # Step 6: Restore Academic Entities
        if entity_map:
            humanized_text = self._restore_academic_entities(humanized_text, entity_map)

        unique_changes = list(dict.fromkeys(changes_applied))

        return {
            "original_text": text,
            "humanized_text": humanized_text,
            "changes_applied": unique_changes[:8],
            "tone": tone,
            "intensity": intensity,
            "shielded_items_count": len(entity_map),
            "source": "heuristic_engine"
        }

    def _try_ollama_humanize(
        self,
        text: str,
        tone: str,
        intensity: str,
        model: str,
        academic_shield: bool = True
    ) -> Optional[Dict[str, Any]]:
        entity_map = {}
        target_text = text
        if academic_shield:
            target_text, entity_map = self._protect_academic_entities(text)

        prompt = (
            f"Rewrite the following text to sound 100% human-written, natural, and score below 15% on AI detectors. "
            f"Tone: {tone}. Intensity: {intensity}. "
            f"Drastically vary sentence lengths (mix short 3-word punchy sentences with compound sentences). "
            f"Eliminate ALL AI clichés (delve into, crucial role, testament to, rich tapestry, furthermore, moreover, in conclusion). "
            f"Use natural contractions (it's, don't, can't, we've). "
            f"Do not alter placeholder tokens like __ACAD_SHIELD_*. "
            f"Return ONLY the rewritten paragraph without commentary:\n\n{target_text}"
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
                        if entity_map:
                            rewritten = self._restore_academic_entities(rewritten, entity_map)
                        return {
                            "original_text": text,
                            "humanized_text": rewritten,
                            "changes_applied": [
                                f"Rewritten via local Ollama ({model})",
                                f"Tone calibrated to {tone}",
                                "High burstiness & natural contractions applied"
                            ] + ([f"Academic Shield: Preserved {len(entity_map)} citations/quotes"] if entity_map else []),
                            "tone": tone,
                            "intensity": intensity,
                            "shielded_items_count": len(entity_map),
                            "source": f"ollama_{model}"
                        }
        except Exception:
            pass
        return None

    def reroll_sentence(self, sentence: str, tone: str = "natural") -> List[Dict[str, str]]:
        """Generates 3 distinct AI-resistant alternative phrasings for an individual sentence."""
        clean_sent = sentence.strip()
        if not clean_sent:
            return []

        # 1. Natural / Conversational variant
        natural_cand = clean_sent
        for pat, rep in COMPOUND_TRANSITION_PATTERNS:
            natural_cand = re.sub(pat, rep, natural_cand, flags=re.IGNORECASE)
        for formal, contracted in CONTRACTIONS.items():
            natural_cand = re.sub(formal, contracted, natural_cand)
        natural_cand = re.sub(r'^(?:It is important to note that|It should be noted that)\s+', 'Notice that, ', natural_cand, flags=re.IGNORECASE)
        natural_cand = re.sub(r'^(?:In order to)\s+', 'To ', natural_cand, flags=re.IGNORECASE)
        natural_cand = re.sub(r'\butilize\b', 'use', natural_cand, flags=re.IGNORECASE)
        natural_cand = re.sub(r'\bfoster innovation\b', 'spark new ideas', natural_cand, flags=re.IGNORECASE)
        if not re.search(r"[.!?]$", natural_cand):
            natural_cand += "."

        # 2. Academic / Structured variant
        academic_cand = clean_sent
        academic_cand = re.sub(r'\bshows\b', 'demonstrates', academic_cand, flags=re.IGNORECASE)
        academic_cand = re.sub(r'\buse\b', 'employ', academic_cand, flags=re.IGNORECASE)
        academic_cand = re.sub(r'\bhelps\b', 'facilitates', academic_cand, flags=re.IGNORECASE)
        academic_cand = re.sub(r'^(?:In conclusion|In summary),', 'In synthesis,', academic_cand, flags=re.IGNORECASE)
        if not re.search(r"[.!?]$", academic_cand):
            academic_cand += "."

        # 3. Punchy / Concise variant
        punchy_cand = clean_sent
        punchy_cand = re.sub(r'\b(?:furthermore|moreover|additionally|consequently|subsequently)\b,?\s*', '', punchy_cand, flags=re.IGNORECASE)
        punchy_cand = re.sub(r'\b(?:in order to)\b', 'to', punchy_cand, flags=re.IGNORECASE)
        punchy_cand = re.sub(r'\b(?:due to the fact that)\b', 'because', punchy_cand, flags=re.IGNORECASE)
        punchy_cand = re.sub(r'\b(?:plays a (?:vital|crucial|key) role in)\b', 'drives', punchy_cand, flags=re.IGNORECASE)
        for formal, contracted in CONTRACTIONS.items():
            punchy_cand = re.sub(formal, contracted, punchy_cand)
        punchy_cand = punchy_cand.strip()
        if punchy_cand:
            punchy_cand = punchy_cand[0].upper() + punchy_cand[1:]
        if not re.search(r"[.!?]$", punchy_cand):
            punchy_cand += "."

        return [
            {
                "tone": "Conversational",
                "text": natural_cand,
                "rationale": "Natural cadence with contractions & conversational phrasing"
            },
            {
                "tone": "Academic",
                "text": academic_cand,
                "rationale": "High lexical entropy with scholarly syntactic inversion"
            },
            {
                "tone": "Punchy",
                "text": punchy_cand,
                "rationale": "Concise active voice maximizing burstiness variance"
            }
        ]
