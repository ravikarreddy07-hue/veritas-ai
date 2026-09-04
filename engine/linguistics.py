"""
Linguistics utilities, comprehensive AI trope catalogs, readability formulas, and vocabulary distributions.
"""

import re
import math
from typing import List, Dict, Tuple, Set

# Comprehensive AI cliché phrases, transitional buzzwords, and repetitive syntactical markers
AI_CLICHE_PATTERNS: Dict[str, Dict[str, str]] = {
    r"\bin today's (?:fast-paced|digital|interconnected|modern) (?:world|age|landscape|society|era)\b": {
        "natural": "these days",
        "academic": "in contemporary society",
        "professional": "today",
        "creative": "right now",
        "desc": "AI trope: 'in today's fast-paced world'"
    },
    r"\bplays? a (?:crucial|pivotal|vital|key|central|fundamental) role(?:\s+in)?\b": {
        "natural": "is really essential to",
        "academic": "substantially influences",
        "professional": "is critical for",
        "creative": "shapes so much of",
        "desc": "AI trope: 'plays a crucial role'"
    },
    r"\bdelve(?:s|d)? into\b": {
        "natural": "look at",
        "academic": "examine",
        "professional": "investigate",
        "creative": "dig into",
        "desc": "AI trope: 'delve into'"
    },
    r"\b(?:serves as|stands as|is) a testament to\b": {
        "natural": "shows clear proof of",
        "academic": "provides concrete evidence for",
        "professional": "demonstrates",
        "creative": "speaks volumes about",
        "desc": "AI trope: 'a testament to'"
    },
    r"\bit is (?:important|crucial|essential|worth noting) to (?:note|remember|consider|recognize)(?:\s+that)?\b": {
        "natural": "keep in mind that",
        "academic": "notably,",
        "professional": "remember that",
        "creative": "notice that",
        "desc": "AI filler: 'it is important to note'"
    },
    r"\bit is worth noting that\b": {
        "natural": "interestingly,",
        "academic": "significantly,",
        "professional": "specifically,",
        "creative": "worth seeing,",
        "desc": "AI filler: 'it is worth noting that'"
    },
    r"\b(?:a )?rich tapestry of\b": {
        "natural": "wide mix of",
        "academic": "diverse array of",
        "professional": "broad set of",
        "creative": "colorful spectrum of",
        "desc": "AI metaphor: 'rich tapestry'"
    },
    r"\bbeacon of\b": {
        "natural": "great example of",
        "academic": "prominent model of",
        "professional": "benchmark for",
        "creative": "shining sign of",
        "desc": "AI metaphor: 'beacon of'"
    },
    r"\bfoster(?:s|ed|ing)? (?:innovation|growth|collaboration)\b": {
        "natural": "spark new ideas",
        "academic": "cultivate progress",
        "professional": "drive development",
        "creative": "ignite fresh ideas",
        "desc": "AI buzzword: 'foster innovation'"
    },
    r"\bfoster(?:s|ed|ing)?\b": {
        "natural": "build",
        "academic": "cultivate",
        "professional": "support",
        "creative": "nurture",
        "desc": "AI buzzword: 'foster'"
    },
    r"\bharness(?:es|ed|ing)?\b": {
        "natural": "use",
        "academic": "utilize",
        "professional": "apply",
        "creative": "tap into",
        "desc": "AI buzzword: 'harness'"
    },
    r"\bleverage(?:s|d|ing)?\b": {
        "natural": "make good use of",
        "academic": "employ",
        "professional": "use",
        "creative": "capitalize on",
        "desc": "AI buzzword: 'leverage'"
    },
    r"\bever-evolving\b": {
        "natural": "changing",
        "academic": "dynamic",
        "professional": "rapidly shifting",
        "creative": "restless",
        "desc": "AI adjective: 'ever-evolving'"
    },
    r"\bmultifaceted\b": {
        "natural": "complex",
        "academic": "multidimensional",
        "professional": "detailed",
        "creative": "many-sided",
        "desc": "AI buzzword: 'multifaceted'"
    },
    r"\bseamlessly\b": {
        "natural": "smoothly",
        "academic": "coherently",
        "professional": "directly",
        "creative": "effortlessly",
        "desc": "AI adverb: 'seamlessly'"
    },
    r"\bholistic approach(?: to succeed)?\b": {
        "natural": "complete picture",
        "academic": "integrated methodology",
        "professional": "end-to-end plan",
        "creative": "full perspective",
        "desc": "AI buzzword: 'holistic approach'"
    },
    r"\bplethora of\b": {
        "natural": "plenty of",
        "academic": "substantial number of",
        "professional": "wide range of",
        "creative": "sea of",
        "desc": "AI trope: 'plethora of'"
    },
    r"\bembark(?:ing)? on a (?:digital transformation )?journey\b": {
        "natural": "getting started with modern tools",
        "academic": "initiating systematic modernization",
        "professional": "upgrading core workflows",
        "creative": "taking the leap forward",
        "desc": "AI cliché: 'embark on a journey'"
    },
    r"\bin conclusion,\b": {
        "natural": "at the end of the day,",
        "academic": "ultimately,",
        "professional": "in summary,",
        "creative": "the takeaway is clear:",
        "desc": "Mechanical conclusion: 'in conclusion,'"
    },
    r"\bfurthermore,\b": {
        "natural": "also,",
        "academic": "additionally,",
        "professional": "on top of that,",
        "creative": "what's more,",
        "desc": "Stiff transitional: 'furthermore,'"
    },
    r"\bmoreover,\b": {
        "natural": "plus,",
        "academic": "in addition,",
        "professional": "alongside that,",
        "creative": "even better,",
        "desc": "Stiff transitional: 'moreover,'"
    },
    r"\bunderscores?\b": {
        "natural": "highlights",
        "academic": "emphasizes",
        "professional": "shows",
        "creative": "drives home",
        "desc": "AI buzzword: 'underscore'"
    },
    r"\bparamount\b": {
        "natural": "critical",
        "academic": "of primary importance",
        "professional": "top priority",
        "creative": "crucial",
        "desc": "AI buzzword: 'paramount'"
    },
    r"\bnavigating the complexities of\b": {
        "natural": "dealing with the tricky parts of",
        "academic": "addressing the intricate factors in",
        "professional": "managing the details of",
        "creative": "wrestling with",
        "desc": "AI trope: 'navigating the complexities'"
    },
    r"\bin the realm of\b": {
        "natural": "in",
        "academic": "within",
        "professional": "across",
        "creative": "inside the world of",
        "desc": "AI filler: 'in the realm of'"
    },
    r"\ba wide array of\b": {
        "natural": "all sorts of",
        "academic": "numerous",
        "professional": "various",
        "creative": "a vibrant range of",
        "desc": "AI filler: 'a wide array of'"
    },
    r"\bunlock(?:ing)? unprecedented opportunities\b": {
        "natural": "open up massive new possibilities",
        "academic": "enable novel opportunities",
        "professional": "unlock strong business value",
        "creative": "spark entirely new horizons",
        "desc": "AI cliché: 'unlock unprecedented opportunities'"
    },
    r"\badopting this strategic paradigm\b": {
        "natural": "making this move",
        "academic": "implementing this framework",
        "professional": "executing this strategy",
        "creative": "leaning into this change",
        "desc": "AI buzzword: 'strategic paradigm'"
    },
    r"\bseamlessly align (?:their )?core competencies\b": {
        "natural": "work together without friction",
        "academic": "integrate complementary operational capabilities",
        "professional": "collaborate effectively across functions",
        "creative": "lock into sync",
        "desc": "AI buzzword: 'align core competencies'"
    },
    r"\bwill foster synergy\b": {
        "natural": "builds genuine teamwork",
        "academic": "enhances institutional cohesion",
        "professional": "improves cross-team productivity",
        "creative": "brings everyone together",
        "desc": "AI trope: 'foster synergy'"
    }
}

# Common English contractions for natural human voice injection
CONTRACTIONS = {
    r"\bit is\b": "it's",
    r"\bIt is\b": "It's",
    r"\bdo not\b": "don't",
    r"\bDo not\b": "Don't",
    r"\bdoes not\b": "doesn't",
    r"\bDoes not\b": "Doesn't",
    r"\bcannot\b": "can't",
    r"\bCannot\b": "Can't",
    r"\bwill not\b": "won't",
    r"\bWill not\b": "Won't",
    r"\bthey are\b": "they're",
    r"\bThey are\b": "They're",
    r"\bwe are\b": "we're",
    r"\bWe are\b": "We're",
    r"\byou are\b": "you're",
    r"\bYou are\b": "You're",
    r"\bthere is\b": "there's",
    r"\bThere is\b": "There's",
    r"\bthat is\b": "that's",
    r"\bThat is\b": "That's",
    r"\bhave not\b": "haven't",
    r"\bhas not\b": "hasn't",
    r"\bwould not\b": "wouldn't",
    r"\bcould not\b": "couldn't",
    r"\bshould not\b": "shouldn't",
}

# English stop words list
STOPWORDS: Set[str] = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are", 
    "aren't", "as", "at", "be", "because", "been", "before", "being", "below", "between", "both", 
    "but", "by", "can't", "cannot", "could", "couldn't", "did", "didn't", "do", "does", "doesn't", 
    "doing", "don't", "down", "during", "each", "few", "for", "from", "further", "had", "hadn't", 
    "has", "hasn't", "have", "haven't", "having", "he", "he'd", "he'll", "he's", "her", "here", 
    "here's", "hers", "herself", "him", "himself", "his", "how", "how's", "i", "i'd", "i'll", 
    "i'm", "i've", "if", "in", "into", "is", "isn't", "it", "it's", "its", "itself", "let's", 
    "me", "more", "most", "mustn't", "my", "myself", "no", "nor", "not", "of", "off", "on", 
    "once", "only", "or", "other", "ought", "our", "ours", "ourselves", "out", "over", "own", 
    "same", "shan't", "she", "she'd", "she'll", "she's", "should", "shouldn't", "so", "some", 
    "such", "than", "that", "that's", "the", "their", "theirs", "them", "themselves", "then", 
    "there", "there's", "these", "they", "they'd", "they'll", "they're", "they've", "this", 
    "those", "through", "to", "too", "under", "until", "up", "very", "was", "wasn't", "we", 
    "we'd", "we'll", "we're", "we've", "were", "weren't", "what", "what's", "when", "when's", 
    "where", "where's", "which", "while", "who", "who's", "whom", "why", "why's", "with", 
    "won't", "would", "wouldn't", "you", "you'd", "you'll", "you're", "you've", "your", 
    "yours", "yourself", "yourselves"
}

# Overused LLM transitional openers
AI_FAVORED_OPENERS = [
    "furthermore,", "moreover,", "additionally,", "in addition,", "consequently,",
    "subsequently,", "importantly,", "crucially,", "ultimately,", "overall,",
    "in essence,", "in summary,", "in conclusion,", "on the other hand,"
]

def split_sentences(text: str) -> List[str]:
    """Splits paragraph text cleanly into individual sentences, preserving punctuation."""
    if not text or not text.strip():
        return []
    cleaned = re.sub(r'[ \t]+', ' ', text.strip())
    raw_sentences = re.split(r'(?<=[.!?])\s+(?=[A-Z0-9"\'“‘])', cleaned)
    return [s.strip() for s in raw_sentences if s.strip()]

def tokenize_words(text: str) -> List[str]:
    """Extracts lowercase alphabetic words from text."""
    return re.findall(r'\b[a-zA-Z\'-]+\b', text.lower())

def count_syllables(word: str) -> int:
    """Estimates the syllable count of an English word."""
    word = word.lower().strip()
    if len(word) <= 3:
        return 1
    word = re.sub(r'(?:[^laeiouy]|ed|es|e)$', '', word)
    word = re.sub(r'^y', '', word)
    syllables = len(re.findall(r'[aeiouy]{1,2}', word))
    return max(1, syllables)

def calculate_readability(text: str) -> Dict[str, float]:
    """Computes standard readability scores (Flesch-Kincaid Grade & Reading Ease)."""
    sentences = split_sentences(text)
    words = tokenize_words(text)
    if not sentences or not words:
        return {
            "flesch_reading_ease": 60.0,
            "flesch_kincaid_grade": 8.0,
            "avg_sentence_length": 0.0,
            "avg_word_syllables": 1.5
        }

    total_sentences = len(sentences)
    total_words = len(words)
    total_syllables = sum(count_syllables(w) for w in words)

    avg_sentence_len = total_words / total_sentences
    avg_syllables_per_word = total_syllables / total_words

    fre = 206.835 - (1.015 * avg_sentence_len) - (84.6 * avg_syllables_per_word)
    fre = max(0.0, min(100.0, fre))

    fkgl = (0.39 * avg_sentence_len) + (11.8 * avg_syllables_per_word) - 15.59
    fkgl = max(1.0, fkgl)

    return {
        "flesch_reading_ease": round(fre, 1),
        "flesch_kincaid_grade": round(fkgl, 1),
        "avg_sentence_length": round(avg_sentence_len, 1),
        "avg_word_syllables": round(avg_syllables_per_word, 2)
    }
