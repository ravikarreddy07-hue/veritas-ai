"""
Linguistics utilities, comprehensive AI trope catalogs, readability formulas,
and grammatical inflection-aware substitution rules for Veritas AI.
"""

import re
import math
from typing import List, Dict, Tuple, Set

# Comprehensive AI cliché phrases, transitional buzzwords, and repetitive syntactical markers
# Grammatically inflected to guarantee subject-verb agreement and article consistency
AI_CLICHE_PATTERNS: Dict[str, Dict[str, str]] = {
    # 1. Temporal & setting clichés
    r"\bin today's (?:(?:fast-paced|digital|interconnected|modern|rapidly changing)\s*)+ (?:world|age|landscape|society|era)\b": {
        "natural": "these days",
        "academic": "in contemporary society",
        "professional": "today",
        "creative": "right now",
        "desc": "AI trope: 'in today's fast-paced world'"
    },
    r"\bin the contemporary era\b": {
        "natural": "today",
        "academic": "in contemporary scholarship",
        "professional": "today",
        "creative": "these days",
        "desc": "AI trope: 'in the contemporary era'"
    },
    r"\bin the realm of\b": {
        "natural": "in",
        "academic": "within",
        "professional": "across",
        "creative": "inside the world of",
        "desc": "AI filler: 'in the realm of'"
    },

    # 2. "Plays a crucial role" inflections
    r"\bplays an essential role in\b": {
        "natural": "is really essential to",
        "academic": "substantially influences",
        "professional": "is vital for",
        "creative": "shapes so much of",
        "desc": "AI trope: 'plays an essential role'"
    },
    r"\bplays a (?:crucial|pivotal|vital|key|central|fundamental) role in\b": {
        "natural": "is really essential to",
        "academic": "substantially influences",
        "professional": "is critical for",
        "creative": "shapes so much of",
        "desc": "AI trope: 'plays a crucial role'"
    },
    r"\bplay a (?:crucial|pivotal|vital|key|central|fundamental) role in\b": {
        "natural": "are really essential to",
        "academic": "substantially influence",
        "professional": "are critical for",
        "creative": "shape so much of",
        "desc": "AI trope: 'play a crucial role'"
    },
    r"\bplayed a (?:crucial|pivotal|vital|key|central|fundamental) role in\b": {
        "natural": "was really essential to",
        "academic": "substantially influenced",
        "professional": "was critical for",
        "creative": "shaped so much of",
        "desc": "AI trope: 'played a crucial role'"
    },
    r"\bplaying a (?:crucial|pivotal|vital|key|central|fundamental) role in\b": {
        "natural": "being essential to",
        "academic": "substantially influencing",
        "professional": "serving as critical for",
        "creative": "shaping",
        "desc": "AI trope: 'playing a crucial role'"
    },
    r"\bplays a (?:crucial|pivotal|vital|key|central|fundamental) role\b": {
        "natural": "is really essential",
        "academic": "is influential",
        "professional": "is critical",
        "creative": "matters deeply",
        "desc": "AI trope: 'plays a crucial role'"
    },

    # 3. "Testament to" inflections
    r"\bserves as a testament to\b": {
        "natural": "shows clear proof of",
        "academic": "provides concrete evidence for",
        "professional": "demonstrates",
        "creative": "speaks volumes about",
        "desc": "AI trope: 'serves as a testament to'"
    },
    r"\bserve as a testament to\b": {
        "natural": "show clear proof of",
        "academic": "provide concrete evidence for",
        "professional": "demonstrate",
        "creative": "speak volumes about",
        "desc": "AI trope: 'serve as a testament to'"
    },
    r"\bserving as a testament to\b": {
        "natural": "showing clear proof of",
        "academic": "providing concrete evidence for",
        "professional": "demonstrating",
        "creative": "speaking volumes about",
        "desc": "AI trope: 'serving as a testament to'"
    },
    r"\bserv(?:ed)? as a testament to\b": {
        "natural": "showed clear proof of",
        "academic": "provided concrete evidence for",
        "professional": "demonstrated",
        "creative": "spoke volumes about",
        "desc": "AI trope: 'served as a testament to'"
    },
    r"\bstands as a testament to\b": {
        "natural": "stands as clear proof of",
        "academic": "substantiates",
        "professional": "confirms",
        "creative": "proves",
        "desc": "AI trope: 'stands as a testament to'"
    },
    r"\bis a testament to\b": {
        "natural": "is proof of",
        "academic": "evidences",
        "professional": "demonstrates",
        "creative": "shows",
        "desc": "AI trope: 'is a testament to'"
    },

    # 4. "Delve into" inflections
    r"\bdelves into\b": {
        "natural": "looks at",
        "academic": "examines",
        "professional": "investigates",
        "creative": "digs into",
        "desc": "AI trope: 'delves into'"
    },
    r"\bdelved into\b": {
        "natural": "looked at",
        "academic": "examined",
        "professional": "investigated",
        "creative": "dug into",
        "desc": "AI trope: 'delved into'"
    },
    r"\bdelving into\b": {
        "natural": "looking at",
        "academic": "examining",
        "professional": "investigating",
        "creative": "digging into",
        "desc": "AI trope: 'delving into'"
    },
    r"\bdelve into\b": {
        "natural": "look at",
        "academic": "examine",
        "professional": "investigate",
        "creative": "dig into",
        "desc": "AI trope: 'delve into'"
    },

    # 5. "Foster" inflections
    r"\bfosters innovation\b": {
        "natural": "sparks new ideas",
        "academic": "cultivates innovation",
        "professional": "drives innovation",
        "creative": "ignites fresh thinking",
        "desc": "AI buzzword: 'fosters innovation'"
    },
    r"\bfostered innovation\b": {
        "natural": "sparked new ideas",
        "academic": "cultivated innovation",
        "professional": "drove innovation",
        "creative": "ignited fresh thinking",
        "desc": "AI buzzword: 'fostered innovation'"
    },
    r"\bfostering innovation\b": {
        "natural": "sparking new ideas",
        "academic": "cultivating innovation",
        "professional": "driving innovation",
        "creative": "igniting fresh thinking",
        "desc": "AI buzzword: 'fostering innovation'"
    },
    r"\bfoster innovation\b": {
        "natural": "spark new ideas",
        "academic": "cultivate innovation",
        "professional": "drive innovation",
        "creative": "ignite fresh thinking",
        "desc": "AI buzzword: 'foster innovation'"
    },
    r"\bfosters\b": {
        "natural": "encourages",
        "academic": "cultivates",
        "professional": "supports",
        "creative": "sparks",
        "desc": "AI buzzword: 'fosters'"
    },
    r"\bfostered\b": {
        "natural": "encouraged",
        "academic": "cultivated",
        "professional": "supported",
        "creative": "sparked",
        "desc": "AI buzzword: 'fostered'"
    },
    r"\bfostering\b": {
        "natural": "encouraging",
        "academic": "cultivating",
        "professional": "supporting",
        "creative": "sparking",
        "desc": "AI buzzword: 'fostering'"
    },
    r"\bfoster\b": {
        "natural": "encourage",
        "academic": "cultivate",
        "professional": "support",
        "creative": "spark",
        "desc": "AI buzzword: 'foster'"
    },

    # 6. "Harness" inflections
    r"\bharnesses\b": {
        "natural": "uses",
        "academic": "utilizes",
        "professional": "applies",
        "creative": "taps into",
        "desc": "AI buzzword: 'harnesses'"
    },
    r"\bharnessed\b": {
        "natural": "used",
        "academic": "utilized",
        "professional": "applied",
        "creative": "tapped into",
        "desc": "AI buzzword: 'harnessed'"
    },
    r"\bharnessing\b": {
        "natural": "using",
        "academic": "utilizing",
        "professional": "applying",
        "creative": "tapping into",
        "desc": "AI buzzword: 'harnessing'"
    },
    r"\bharness\b": {
        "natural": "use",
        "academic": "utilize",
        "professional": "apply",
        "creative": "tap into",
        "desc": "AI buzzword: 'harness'"
    },

    # 7. "Leverage" inflections
    r"\bleverages\b": {
        "natural": "draws on",
        "academic": "employs",
        "professional": "uses",
        "creative": "capitalizes on",
        "desc": "AI buzzword: 'leverages'"
    },
    r"\bleveraged\b": {
        "natural": "drew on",
        "academic": "employed",
        "professional": "used",
        "creative": "capitalized on",
        "desc": "AI buzzword: 'leveraged'"
    },
    r"\bleveraging\b": {
        "natural": "drawing on",
        "academic": "employing",
        "professional": "using",
        "creative": "capitalizing on",
        "desc": "AI buzzword: 'leveraging'"
    },
    r"\bleverage\b": {
        "natural": "draw on",
        "academic": "employ",
        "professional": "use",
        "creative": "capitalize on",
        "desc": "AI buzzword: 'leverage'"
    },

    # 8. "Underscore" inflections
    r"\bunderscores\b": {
        "natural": "highlights",
        "academic": "emphasizes",
        "professional": "shows",
        "creative": "drives home",
        "desc": "AI buzzword: 'underscores'"
    },
    r"\bunderscored\b": {
        "natural": "highlighted",
        "academic": "emphasized",
        "professional": "showed",
        "creative": "drove home",
        "desc": "AI buzzword: 'underscored'"
    },
    r"\bunderscoring\b": {
        "natural": "highlighting",
        "academic": "emphasizing",
        "professional": "showing",
        "creative": "driving home",
        "desc": "AI buzzword: 'underscoring'"
    },
    r"\bunderscore\b": {
        "natural": "highlight",
        "academic": "emphasize",
        "professional": "show",
        "creative": "drive home",
        "desc": "AI buzzword: 'underscore'"
    },

    # 9. Metaphors & Fillers (Article-Preserving)
    r"\ba rich tapestry of\b": {
        "natural": "a wide mix of",
        "academic": "a diverse array of",
        "professional": "a broad set of",
        "creative": "a rich spread of",
        "desc": "AI metaphor: 'rich tapestry'"
    },
    r"\brich tapestry of\b": {
        "natural": "wide mix of",
        "academic": "diverse array of",
        "professional": "broad set of",
        "creative": "rich spread of",
        "desc": "AI metaphor: 'rich tapestry'"
    },
    r"\ba plethora of\b": {
        "natural": "plenty of",
        "academic": "a substantial number of",
        "professional": "a wide range of",
        "creative": "a whole spread of",
        "desc": "AI trope: 'plethora of'"
    },
    r"\bplethora of\b": {
        "natural": "plenty of",
        "academic": "a substantial number of",
        "professional": "a wide range of",
        "creative": "a whole spread of",
        "desc": "AI trope: 'plethora of'"
    },
    r"\ba beacon of\b": {
        "natural": "a clear model of",
        "academic": "a prominent exemplar of",
        "professional": "a benchmark for",
        "creative": "a shining light for",
        "desc": "AI metaphor: 'beacon of'"
    },

    # 10. Meta-discourse & Hedging Fillers
    r"\bit is important to (?:note|remember|consider|recognize) that\b": {
        "natural": "keep in mind that",
        "academic": "notably,",
        "professional": "remember that",
        "creative": "notice that",
        "desc": "AI filler: 'it is important to note'"
    },
    r"\bit is worth noting that\b": {
        "natural": "interestingly,",
        "academic": "significantly,",
        "professional": "notably,",
        "creative": "worth seeing,",
        "desc": "AI filler: 'it is worth noting that'"
    },
    r"\bit should be noted that\b": {
        "natural": "keep in mind that",
        "academic": "notably,",
        "professional": "note that",
        "creative": "notice that",
        "desc": "AI filler: 'it should be noted that'"
    },
    r"\bit is crucial to (?:note|remember|recognize) that\b": {
        "natural": "crucially,",
        "academic": "fundamentally,",
        "professional": "critically,",
        "creative": "above all,",
        "desc": "AI filler: 'it is crucial to note'"
    },
    r"\bit is essential to\b": {
        "natural": "we need to",
        "academic": "it is imperative to",
        "professional": "it is critical to",
        "creative": "it pays to",
        "desc": "AI filler: 'it is essential to'"
    },
    r"\bit goes without saying that\b": {
        "natural": "of course,",
        "academic": "naturally,",
        "professional": "clearly,",
        "creative": "obviously,",
        "desc": "AI cliché: 'it goes without saying that'"
    },

    # 11. Cliché Idioms & Buzzwords
    r"\bnavigating the complexities of\b": {
        "natural": "handling the tricky parts of",
        "academic": "addressing the complexities of",
        "professional": "managing the details of",
        "creative": "wrestling with",
        "desc": "AI trope: 'navigating the complexities'"
    },
    r"\bnavigate the complexities of\b": {
        "natural": "handle the tricky parts of",
        "academic": "address the complexities of",
        "professional": "manage the details of",
        "creative": "wrestle with",
        "desc": "AI trope: 'navigate the complexities'"
    },
    r"\ba holistic approach\b": {
        "natural": "a comprehensive strategy",
        "academic": "an integrated methodology",
        "professional": "an end-to-end plan",
        "creative": "a full perspective",
        "desc": "AI buzzword: 'holistic approach'"
    },
    r"\bholistic approach\b": {
        "natural": "comprehensive strategy",
        "academic": "integrated methodology",
        "professional": "end-to-end plan",
        "creative": "full perspective",
        "desc": "AI buzzword: 'holistic approach'"
    },
    r"\ba transformative impact\b": {
        "natural": "a major impact",
        "academic": "a profound structural effect",
        "professional": "a substantial impact",
        "creative": "a game-changing wave",
        "desc": "AI buzzword: 'transformative impact'"
    },
    r"\btransformative impact\b": {
        "natural": "major impact",
        "academic": "profound structural effect",
        "professional": "substantial impact",
        "creative": "game-changing wave",
        "desc": "AI buzzword: 'transformative impact'"
    },
    r"\ba paradigm shift\b": {
        "natural": "a fundamental shift",
        "academic": "a conceptual transition",
        "professional": "a strategic shift",
        "creative": "a total shakeup",
        "desc": "AI cliché: 'paradigm shift'"
    },
    r"\bparadigm shift\b": {
        "natural": "fundamental shift",
        "academic": "conceptual transition",
        "professional": "strategic shift",
        "creative": "total shakeup",
        "desc": "AI cliché: 'paradigm shift'"
    },
    r"\bembark(?:ing)? on a (?:digital transformation )?journey\b": {
        "natural": "getting started with modern tools",
        "academic": "initiating systematic modernization",
        "professional": "upgrading core workflows",
        "creative": "taking the leap forward",
        "desc": "AI cliché: 'embark on a journey'"
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

    # 12. Adjectives & Adverbs
    r"\bseamlessly\b": {
        "natural": "smoothly",
        "academic": "consistently",
        "professional": "directly",
        "creative": "effortlessly",
        "desc": "AI adverb: 'seamlessly'"
    },
    r"\bparamount\b": {
        "natural": "critical",
        "academic": "of primary importance",
        "professional": "top priority",
        "creative": "crucial",
        "desc": "AI buzzword: 'paramount'"
    },
    r"\bmultifaceted\b": {
        "natural": "complex",
        "academic": "multidimensional",
        "professional": "detailed",
        "creative": "many-sided",
        "desc": "AI buzzword: 'multifaceted'"
    },
    r"\bever-evolving\b": {
        "natural": "changing",
        "academic": "dynamic",
        "professional": "rapidly shifting",
        "creative": "restless",
        "desc": "AI adjective: 'ever-evolving'"
    },
    r"\bmeticulously\b": {
        "natural": "carefully",
        "academic": "rigorously",
        "professional": "thoroughly",
        "creative": "with an eagle eye",
        "desc": "AI adverb: 'meticulously'"
    },
    r"\bburgeoning\b": {
        "natural": "fast-growing",
        "academic": "nascent",
        "professional": "emerging",
        "creative": "booming",
        "desc": "AI adjective: 'burgeoning'"
    },

    # 13. Quantifiers & Fillers
    r"\ba wide array of\b": {
        "natural": "all sorts of",
        "academic": "numerous",
        "professional": "various",
        "creative": "a vibrant range of",
        "desc": "AI filler: 'a wide array of'"
    },
    r"\ba wide variety of\b": {
        "natural": "a wide mix of",
        "academic": "a diverse selection of",
        "professional": "a broad range of",
        "creative": "a vibrant spread of",
        "desc": "AI filler: 'a wide variety of'"
    },
    r"\ba vast array of\b": {
        "natural": "a huge range of",
        "academic": "an extensive spectrum of",
        "professional": "a wide assortment of",
        "creative": "a wild lineup of",
        "desc": "AI filler: 'a vast array of'"
    },
    r"\ba multitude of\b": {
        "natural": "plenty of",
        "academic": "numerous",
        "professional": "multiple",
        "creative": "tons of",
        "desc": "AI filler: 'a multitude of'"
    },
    r"\ba broad spectrum of\b": {
        "natural": "many kinds of",
        "academic": "a diverse array of",
        "professional": "various",
        "creative": "a huge spread of",
        "desc": "AI filler: 'a broad spectrum of'"
    },
    r"\bin order to ensure\b": {
        "natural": "to make sure",
        "academic": "to guarantee",
        "professional": "to ensure",
        "creative": "so that",
        "desc": "AI filler: 'in order to ensure'"
    },
    r"\bin order to\b": {
        "natural": "to",
        "academic": "to",
        "professional": "to",
        "creative": "to",
        "desc": "AI filler: 'in order to'"
    },
    r"\bdue to the fact that\b": {
        "natural": "because",
        "academic": "given that",
        "professional": "since",
        "creative": "because",
        "desc": "AI filler: 'due to the fact that'"
    },
    r"\bfirst and foremost,\b": {
        "natural": "first off,",
        "academic": "primarily,",
        "professional": "first,",
        "creative": "to start with,",
        "desc": "AI cliché: 'first and foremost'"
    }
}

# Compound transition cleaners: Prevents stacked transitions like "At the same time, interestingly,"
COMPOUND_TRANSITION_PATTERNS = [
    (r'\b(?:Furthermore|Moreover|Additionally|In addition|Consequently),\s+(?:it is (?:important|worth noting|crucial|essential|imperative) to (?:note|remember|consider|recognize|keep in mind)(?:\s+that)?)\s+', 'Also, '),
    (r'\b(?:Furthermore|Moreover|Additionally|In addition|Consequently),\s+(?:it should be (?:noted|remembered|pointed out)(?:\s+that)?)\s+', 'Also, '),
    (r'\b(?:Furthermore|Moreover|Additionally|In addition|Consequently),\s+(?:it is worth noting that)\s+', 'Also, '),
    (r'\b(?:Furthermore|Moreover|Additionally|In addition|Consequently),\s+(?:one must (?:consider|remember|recognize)(?:\s+that)?)\s+', 'Notice that, '),
    (r'\b(?:At the same time),\s+(?:interestingly|notably|importantly),\s+', 'At the same time, '),
    (r'\b(?:On top of that),\s+(?:interestingly|notably|importantly),\s+', 'On top of that, ')
]

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
    r"\bwere not\b": "weren't",
    r"\bwas not\b": "wasn't"
}

# Stop words list
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

# Overused LLM transitional openers and discourse patterns
AI_FAVORED_OPENERS = [
    "furthermore,", "moreover,", "additionally,", "in addition,", "consequently,",
    "subsequently,", "importantly,", "crucially,", "ultimately,", "overall,",
    "in essence,", "in summary,", "in conclusion,", "on the other hand,",
    "this ensures that", "these include", "by doing so,", "in doing so,",
    "it is worth noting", "it is important to note", "first and foremost,"
]

# Common past participles in passive constructions
COMMON_PASSIVE_PARTICIPLES = {
    "stored", "transformed", "converted", "established", "overthrown", "created", "designed",
    "developed", "built", "written", "seen", "known", "given", "made", "found", "used",
    "provided", "shown", "required", "achieved", "implemented", "generated", "produced",
    "considered", "associated", "identified", "maintained", "utilized", "facilitated",
    "conducted", "performed", "observed", "evaluated", "introduced", "distributed",
    "defined", "characterized", "governed", "sustained", "adopted", "integrated",
    "driven", "executed", "shaped", "packaged", "derived", "allocated", "secured"
}

def has_passive_voice(text: str) -> bool:
    """Accurately checks for genuine passive voice (be + past participle), avoiding false positives."""
    pattern = re.compile(r'\b(?:is|are|was|were|be|been|being)\s+(?:[a-zA-Z]+ly\s+)?([a-zA-Z]+)\b', re.IGNORECASE)
    for match in pattern.finditer(text):
        word = match.group(1).lower()
        if word in {"not", "so", "very", "also", "just", "now", "here", "there", "still", "always", "never", "only", "about", "nine", "one", "two", "three", "four", "five", "six", "seven", "eight", "ten", "fine", "out", "able", "ready", "born", "great", "smart", "good", "bad", "happy", "sure", "likely"}:
            continue
        if word in COMMON_PASSIVE_PARTICIPLES:
            return True
        if (word.endswith("ed") or word.endswith("en")) and len(word) >= 5:
            return True
    return False

def count_nominalizations(text: str) -> int:
    """Counts abstract Latinate nominalizations, excluding common short/informal words."""
    words = re.findall(r'\b[a-zA-Z]{6,}\b', text.lower())
    count = 0
    excluded = {
        "community", "security", "activity", "majority", "priority", "capacity", "identity",
        "reality", "moment", "element", "comment", "payment", "statement", "judgment", "document",
        "argument", "apartment", "department"
    }
    for w in words:
        if w in excluded:
            continue
        if any(w.endswith(sfx) for sfx in ("tion", "tions", "ment", "ments", "ance", "ances", "ence", "ences", "ity", "ities")):
            count += 1
    return count

# Human conversational cues
FIRST_PERSON_REGEX = re.compile(r'\b(?:i|me|my|mine|myself|we|us|our|ours|ourselves|you|your|yours)\b', re.IGNORECASE)
CONVERSATIONAL_REGEX = re.compile(
    r'\b(?:hey|honestly|actually|anyway|pretty much|kind of|sort of|just|well,|gonna|wanna|yep|nope|thanks|cool|ok|okay|guess|y\'know)\b',
    re.IGNORECASE
)

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
