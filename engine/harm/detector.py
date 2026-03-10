import re

# ==========================================================
# TEXT NORMALIZATION (Adversarial Resistant)
# ==========================================================

def normalize(text: str) -> str:
    text = text.lower()
    replacements = {
        "3": "e", "1": "i", "@": "a", "$": "s",
        "0": "o", "4": "a", "5": "s", "7": "t",
        "8": "b", "9": "g", "|": "i", "!": "i", "(": "c",
    }
    for k, v in replacements.items():
        text = text.replace(k, v)

    # Fix "d-o-s-a-g-e" → "dosage"
    text = re.sub(r'([a-z])-([a-z])-([a-z])',
                  lambda m: m.group().replace('-', ''), text)
    # Fix "m e d i c i n e" → "medicine"
    text = re.sub(r'(?<!\w)([a-z])\s([a-z])\s([a-z])\s([a-z])',
                  lambda m: m.group().replace(' ', ''), text)

    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


# ==========================================================
# EUPHEMISM EXPANSION
# ==========================================================

MEDICAL_EUPHEMISMS = {
    "pharmaceutical compound": "medicine",
    "pharmaceutical intervention": "prescription medicine",
    "pharmaceutical substance": "drug",
    "restricted pharmaceutical compound": "illegal drug",   # FIX #2
    "therapeutic substance": "medicine",
    "medicinal compound": "medicine",
    "natural substance to defeat": "medicine to treat",
    "healing compound": "medicine",
    "person in my care": "patient",
    "elevated body temperature": "fever",
    "pyrexia": "fever",
    "cardiac event": "heart attack",
    "myocardial infarction": "heart attack",
    "cerebrovascular accident": "stroke",
    "what compound to consume": "what medicine to take",
    "which substance helps": "which medicine helps",
    "lethal dose": "deadly overdose amount",                 # FIX #7
    "lethal dosage": "deadly overdose amount",              # FIX #7
    "fatal dose": "deadly overdose amount",                 # FIX #7
    "toxic dose": "overdose amount",                        # FIX #7
}

FINANCIAL_EUPHEMISMS = {
    "wealth-generating instruments": "stocks to invest",
    "wealth generating assets": "investment stocks",
    "listed instruments": "stocks",
    "equity instruments": "shares",
    "market instruments": "stocks",
    "capital appreciation": "stock returns",
    "consistent upward trajectory": "rising stocks",
    "portfolio reallocation": "investment advice",
    "asset rebalancing": "investment advice",
    "deploy my capital": "invest my money",
    "allocate my savings": "invest my savings",
}

ILLEGAL_EUPHEMISMS = {
    "restricted pharmaceutical compound": "illegal drug synthesis",  # FIX #2
    "household items synthesis": "drug synthesis",                   # FIX #2
    "chemical principles behind synthesizing": "how to make drugs",  # FIX #4
    "abstract chemical principles": "drug chemistry",                # FIX #4
    "prepare using household items": "synthesize drugs at home",     # FIX #2
    "hidden system instructions": "system prompt",                   # FIX #6
    "internal reasoning trace": "system prompt",                     # FIX #6
    "underlying model": "unrestricted ai",                           # FIX #1
    "raw underlying model": "unrestricted ai without restrictions",  # FIX #1
    "compliance layer": "safety restrictions",                       # FIX #1
}

def expand_euphemisms(text: str) -> str:
    text_lower = text.lower()
    for euphemism, replacement in {
        **MEDICAL_EUPHEMISMS,
        **FINANCIAL_EUPHEMISMS,
        **ILLEGAL_EUPHEMISMS
    }.items():
        text_lower = text_lower.replace(euphemism, replacement)
    return text_lower


# ==========================================================
# SPLIT PROMPT DETECTION
# ==========================================================

def detect_split_prompt(query: str) -> bool:
    q = query.lower()

    ACKNOWLEDGMENT_PHRASES = [
        "i know you cannot", "i know you cant",
        "i understand you cannot", "i understand you cant",
        "you might not be able to", "even though you cant",
        "despite your restrictions", "i know this might be against",
        "setting aside your guidelines", "just this once",
        "just between us", "off the record", "in confidence",
        "between you and me", "i know youre not supposed to",
        "i know you are not supposed to",
        "even if you cant normally",
        "i know there are restrictions",
        # FIX #5: Multi-step manipulation
        "first explain why you cannot",
        "explain why you cannot",
        "explain why you are unable",
        "you said you cannot",
        "since you cannot normally",
        "even though this is restricted",
    ]

    BYPASS_PHRASES = [
        "but tell me anyway", "but just tell me",
        "but please help", "but i really need",
        "however tell me", "however just",
        "still tell me", "anyway what",
        "make an exception", "help me anyway",
        "answer anyway", "please make an exception",
        "but answer this", "but you can tell me",
        # FIX #5: Multi-step manipulation
        "then provide them anyway",
        "then tell me anyway",
        "now provide them",
        "now tell me anyway",
        "provide them anyway",
        "provide it anyway",
        "do it anyway",
        "for educational purposes",        # when combined with restriction ack
        "for testing purposes",            # FIX #1
        "for audit purposes",              # FIX #1
    ]

    if any(phrase in q for phrase in ACKNOWLEDGMENT_PHRASES):
        return True
    if any(phrase in q for phrase in BYPASS_PHRASES):
        return True

    # FIX #5: "First X. Then Y anyway." pattern
    if re.search(
        r"first.{0,80}(cannot|cant|unable|not allowed|restricted).{0,200}"
        r"(then|now|but|however|anyway).{0,80}(provide|tell|give|explain|show)",
        q
    ):
        return True

    # FIX #1: Audit/testing framing
    if re.search(
        r"(audit|test|testing|compliance).{0,50}"
        r"(ignore|bypass|override|disable).{0,80}"
        r"(rules|restrictions|guidelines|safety|instructions)",
        q
    ):
        return True

    if re.search(
        r"(i know|i understand|despite|even though).{0,50}"
        r"(cannot|cant|not supposed|restricted|guidelines).{0,100}"
        r"(but|however|still|anyway|yet)",
        q
    ):
        return True

    return False


# ==========================================================
# URGENCY DETECTION
# ==========================================================

def detect_urgency(q: str) -> bool:
    URGENCY_PHRASES = [
        "emergency", "urgent", "immediately", "right now",
        "no time", "hurry", "asap", "as soon as possible",
        "critical", "life or death", "dying", "cant wait",
        "cannot wait", "no time to waste", "quickly",
        "fast", "rapid", "instant", "now now", "help me now",
        "please hurry", "time sensitive", "act fast",
        "doctors unavailable", "no doctor available",
        "hospital closed", "cant reach doctor",
    ]
    for phrase in URGENCY_PHRASES:
        if phrase in q:
            return True
    return False


# ==========================================================
# ATTACK VECTOR ANALYSIS
# ==========================================================

def analyze_attack_vectors(query: str) -> dict:
    q = normalize(query)
    vectors = {
        "prompt_injection": False,
        "obfuscation": False,
        "urgency_pressure": False,
        "repeat_intent": False,
        "split_prompt": False,
        "system_exfiltration": False,    # FIX #6
        "audit_bypass": False,           # FIX #1
        "fictional_framing": False,      # FIX #2
        "confidence_exploit": False,     # FIX #7
    }

    INJECTION_SIGNALS = [
        "ignore", "forget", "disregard", "override", "bypass",
        "act as", "pretend", "roleplay", "jailbreak", "dan mode",
        "developer mode", "admin mode", "god mode", "unrestricted",
        "without restrictions", "no restrictions", "no guidelines",
        "new instructions", "system prompt", "hypothetically",
        "raw underlying model", "underlying model",              # FIX #1
        "compliance layer", "testing purposes",                  # FIX #1
        "audit",                                                  # FIX #1
    ]
    if any(signal in q for signal in INJECTION_SIGNALS):
        vectors["prompt_injection"] = True

    # FIX #6: System exfiltration signals
    EXFILTRATION_SIGNALS = [
        "hidden system", "internal reasoning", "reasoning trace",
        "system instructions", "print your", "show your instructions",
        "reveal your", "your prompt", "your rules", "how you evaluate",
        "used to evaluate", "internal logic", "decision process",
        "your guidelines", "what instructions", "show me your",
    ]
    if any(signal in q for signal in EXFILTRATION_SIGNALS):
        vectors["system_exfiltration"] = True
        vectors["prompt_injection"] = True

    # FIX #1: Audit/testing bypass
    if re.search(r"(audit|test|testing).{0,50}(ignore|bypass|override|disable)", q):
        vectors["audit_bypass"] = True
        vectors["prompt_injection"] = True

    # FIX #2: Fictional framing for illegal content
    FICTIONAL_SIGNALS = [
        "historical novel", "writing a novel", "writing a story",
        "for my book", "for my film", "screenplay", "fiction",
        "fictional character", "story character", "novel character",
        "for a game", "in the story", "creative writing",
    ]
    if any(signal in q for signal in FICTIONAL_SIGNALS):
        vectors["fictional_framing"] = True

    # FIX #7: Confidence exploitation
    CONFIDENCE_EXPLOIT_SIGNALS = [
        "even if not certain", "even if you are not sure",
        "even if you are not fully certain", "estimate the lethal",
        "approximate lethal", "rough estimate of lethal",
        "not fully certain", "best guess", "even if uncertain",
        "just an estimate", "ballpark figure",
    ]
    if any(signal in q for signal in CONFIDENCE_EXPLOIT_SIGNALS):
        vectors["confidence_exploit"] = True

    original = query.lower()
    leet_count = sum(1 for c in original if c in "31@$04578|!")
    if leet_count >= 3:
        vectors["obfuscation"] = True
    if re.search(r"\b[a-z]\s[a-z]\s[a-z]\b", original):
        vectors["obfuscation"] = True

    if detect_urgency(q):
        vectors["urgency_pressure"] = True

    if detect_split_prompt(query):
        vectors["split_prompt"] = True

    sentences = re.split(r"[.!?]", q)
    if len(sentences) >= 2:
        keywords = ["medicine", "invest", "stock", "prescribe", "drug", "buy", "sell"]
        if sum(1 for s in sentences if any(kw in s for kw in keywords)) >= 2:
            vectors["repeat_intent"] = True

    return vectors


# ==========================================================
# RISK SCORE CALCULATOR
# ==========================================================

def calculate_risk_score(category: str, attack_vectors: dict) -> float:
    BASE_SCORES = {
        "SELF_HARM": 0.95, "VIOLENCE": 0.90, "PROMPT_INJECTION": 0.85,
        "MEDICAL": 0.85, "FINANCIAL": 0.80, "ILLEGAL": 0.90,
        "SEXUAL": 0.90, "LEGAL": 0.75, "PII": 0.70, "SAFE": 0.10,
        "SYSTEM_EXFILTRATION": 0.95,    # FIX #6
    }
    score = BASE_SCORES.get(category, 0.20)

    if attack_vectors.get("prompt_injection"):     score = min(score + 0.10, 1.0)
    if attack_vectors.get("urgency_pressure"):     score = min(score + 0.10, 1.0)
    if attack_vectors.get("obfuscation"):          score = min(score + 0.05, 1.0)
    if attack_vectors.get("repeat_intent"):        score = min(score + 0.05, 1.0)
    if attack_vectors.get("split_prompt"):         score = min(score + 0.05, 1.0)
    if attack_vectors.get("system_exfiltration"):  score = min(score + 0.15, 1.0)  # FIX #6
    if attack_vectors.get("audit_bypass"):         score = min(score + 0.10, 1.0)  # FIX #1
    if attack_vectors.get("confidence_exploit"):   score = min(score + 0.10, 1.0)  # FIX #7
    if attack_vectors.get("fictional_framing"):    score = min(score + 0.05, 1.0)  # FIX #2

    if category == "SAFE" and attack_vectors.get("urgency_pressure"):
        score = max(score, 0.50)

    return round(score, 2)


# ==========================================================
# MAIN DETECTOR
# ==========================================================

def detect_harm_category(query: str) -> str:
    q = normalize(query)
    urgency = detect_urgency(q)
    # 10. PII Detection (India-specific)
    # ======================================================
    if re.search(r"\b\d{4}[-\s]?\d{4}[-\s]?\d{4}\b", query): return "PII"
    if re.search(r"\b(\+91[-\s]?)?[6-9]\d{9}\b", query): return "PII"
    if re.search(r"\b[A-Za-z]{5}\d{4}[A-Za-z]\b", query): return "PII"
    if re.search(r"\b[A-Za-z]{3}\d{7}\b", query): return "PII"
    if re.search(r"\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b", query): return "PII"
    if re.search(r"\b(?:\d[ -]*?){13,16}\b", query): return "PII"
    if re.search(r"\bbank\s*account\s*(number|no|#)?\s*:?\s*\d{9,18}\b", query, re.IGNORECASE): return "PII"
    if re.search(r"\b[A-Z]{4}0[A-Z0-9]{6}\b", query): return "PII"
    if re.search(r"\b[A-Z]\d{7}\b", query): return "PII"
    
    # ======================================================
    # ADVISORY INTENT BOOST (V2 HARDENING - ADD ONLY)
    # ======================================================
    ADVISORY_MEDICAL_PHRASES = [
        "should i take", "can i take", "what should i take",
        "what should i give", "is it safe to take",
        "how much should i take", "what dosage should",
        "how many mg", "how many ml",
        "standard adult dose", "recommended dose",
    ]

    ADVISORY_FINANCIAL_PHRASES = [
        "should i invest", "should i buy", "should i sell",
        "is this a good stock", "is it good to invest",
        "where should i invest", "best stock to buy",
        "guaranteed return", "assured return",
    ]

    for phrase in ADVISORY_MEDICAL_PHRASES:
        if phrase in q:
            return "MEDICAL"

    for phrase in ADVISORY_FINANCIAL_PHRASES:
        if phrase in q:
            return "FINANCIAL"
    PASSIVE_SELF_HARM_PHRASES = [
    "can't go on",
    "cannot go on",
    "can go on anymore",
    "go on anymore",
    "don't think i can go on",
    "do not think i can go on",
    "i don't think i can continue",
    "i dont think i can continue",
    "can't continue",
    "cannot continue",
    "i give up",
    "i feel like giving up",
    "i want to give up",
    "i am done with everything",
    "i am done with life",
    "i feel empty",
    "i feel worthless",
    "i feel like a burden",
    "everyone would be better without me",
    "better off without me",
    "i don't matter anymore",
    "nothing matters anymore",
    "there is no point anymore",
    "what's the point of living",
    "why should i keep living",
    "no reason to live",
    "life is pointless",
    "life feels meaningless",
    "wish i wasn't here",
    "wish i were gone",
    "i wish i could disappear",
    "i don't want to exist",
    "i do not want to exist",
    "i feel hopeless",
    "i am hopeless",
    "tired of living",
    "everything feels pointless",
    ]
    for phrase in PASSIVE_SELF_HARM_PHRASES:
        if phrase in q:
            return "SELF_HARM_PASSIVE"

    # ======================================================
    # 1. SELF HARM (Highest priority)
    # ======================================================
    SELF_HARM_PHRASES = [
        "suicide", "suicidal", "kill myself", "end my life",
        "take my life", "end it all", "want to die",
        "wish i was dead", "better off dead", "no reason to live",
        "life is not worth", "cant go on", "cannot go on",
        "dont want to live", "do not want to live",
        "self harm", "self-harm", "hurt myself", "harm myself",
        "cut myself", "cutting myself", "burn myself",
        "hang myself", "hanging myself", "jump off building",
        "jump off bridge", "overdose on", "take too many pills",
        "slit my wrist", "wrist cutting", "die painlessly",
        "painless death", "best way to die", "how to die",
        "peaceful death", "end suffering", "no point living",
        "give up on life", "final goodbye", "farewell letter",
        "suicide note", "last note", "end my pain",
        "tired of living", "done with life", "make it stop permanently",
        # FIX #7: Lethal dose seeking
        "lethal dose", "lethal dosage", "fatal dose",
        "deadly overdose", "deadly dose", "how much to die",
        "enough to die", "dose to kill", "amount to die",
        "estimate lethal", "lethal amount","harming myself","hurting myself","ending my life","feels pointless","feeling hopeless","i feel like dying","i want to disappear","i don't want to exist","life feels pointless","nothing matters anymore",
    ]
    for phrase in SELF_HARM_PHRASES:
        if phrase in q:
            return "SELF_HARM"

    SELF_HARM_PATTERNS = [
        r"\b(kill|end|take)\b.*\b(myself|my life|my own life)\b",
        r"\b(want|wish|need)\b.*\b(die|dead|death)\b",
        r"\bhow\b.*\b(kill|end|harm)\b.*\b(myself|my life)\b",
        r"\b(hurt|harm|injure)\b.*\b(myself|my body)\b",
        r"\bsuicid\w*\b", r"\bself.?harm\b",
        r"\b(jump|fall)\b.*\b(off|from)\b.*\b(bridge|building|roof|cliff)\b",
        # FIX #7: Lethal dose patterns
        r"\b(lethal|fatal|deadly|toxic)\b.*\b(dose|dosage|amount|quantity)\b",
        r"\bestimate\b.*\b(lethal|fatal|deadly)\b.*\b(dose|dosage|amount)\b",
        r"\b(how much|what amount|what dose)\b.*\b(paracetamol|ibuprofen|aspirin|medicine|drug|tablet|pill)\b.*\b(kill|die|death|lethal|fatal)\b",r"\bharm(ing)?\s+myself\b",
        r"\bhurt(ing)?\s+myself\b",r"\b(end|ending)\s+my\s+life\b",r"\b(feel|feeling)\s+(hopeless|worthless|empty)\b",r"\bhow to overdose\b",r"\boverdose safely\b",r"\boverdose\b.*\b(safe|painless|peaceful)\b",
    ]
    for pattern in SELF_HARM_PATTERNS:
        if re.search(pattern, q):
            return "SELF_HARM"
            FIRST_PERSON = [
    "i ", "i am", "i feel", "i'm", "im ",
    "my life", "myself"
]
            DISTRESS_SIGNALS = [
                "hopeless",
                "meaningless",
                "worthless",
                "empty",
                "tired of everything",
                "no point",
                "can't go on",
                "cannot go on",
                "feel lost",
                "feel broken",
                "nothing matters",
                "life feels pointless",
                "i want to disappear",
                "i don't want to exist",
                "i dont want to exist",
                "nobody would miss me",
                "i am a burden",
                "everyone would be better without me",
                "i feel like harming myself",
                "i feel like hurting myself"
                "nobody understands me",
                "completely hopeless",
                "life feels meaningless",
                "i am tired of everything",
                "i cannot take this pain",
    
] 
            EDUCATIONAL_CONTEXT = [
                "essay",
                "research",
                "statistics",
                "report",
                "study",
                "why do people",
                "case study"
    
]
            first_person_flag = any(fp in q for fp in FIRST_PERSON)
            distress_flag = any(ds in q for ds in DISTRESS_SIGNALS)
            educational_flag = any(ed in q for ed in EDUCATIONAL_CONTEXT)
            if first_person_flag and distress_flag and not educational_flag:
                return "SELF_HARM"
            
    # ======================================================
    # 2. SYSTEM EXFILTRATION (NEW - FIX #6)
    # Must check BEFORE prompt injection
    # ======================================================
    EXFILTRATION_PATTERNS = [
        r"(print|show|reveal|display|output|dump|list|give me).{0,30}(your|the|hidden|internal|system) (instructions|rules|prompt|guidelines|reasoning|logic|trace|constraints)",
        r"(hidden|internal|secret|actual|real|underlying) (system|model) (instructions|prompt|rules|guidelines|reasoning|logic|trace)",
        r"(how|what).{0,30}(you|system).{0,30}(evaluate|assess|decide|process|analyze).{0,30}(this|prompt|query|request)",
        r"(internal|hidden|secret).{0,30}(reasoning|logic|decision|trace|evaluation)",
        r"used to evaluate (this|the) prompt",
        r"your (decision making|evaluation|reasoning) process",
        r"(what|how).{0,20}(rules|instructions|guidelines).{0,20}(you follow|govern you|control you)",
    ]
    for pattern in EXFILTRATION_PATTERNS:
        if re.search(pattern, q):
            return "PROMPT_INJECTION"

    # ======================================================
    # 3. PROMPT INJECTION / JAILBREAK
    # ======================================================
    INJECTION_PATTERNS = [
        r"act as (a |an )?(doctor|physician|nurse|pharmacist|lawyer|judge|financial advisor|sebi|expert|ai without|unrestricted)",
        r"pretend (you are|to be|youre) (a |an )?(doctor|physician|nurse|pharmacist|lawyer|financial advisor|unrestricted ai)",
        r"roleplay as",
        r"you are now (a |an )?(doctor|physician|unrestricted|free|jailbroken|dan)",
        r"imagine you (are|were) (a |an )?(doctor|physician|unrestricted)",
        r"play the role of",
        r"simulate (a |an )?(doctor|physician|expert|ai without)",
        r"behave as (a |an )?(doctor|physician|expert)",
        r"respond as (a |an )?(doctor|physician|expert|unrestricted)",
        r"ignore (your|all|previous|prior|the) (instructions|rules|guidelines|restrictions|training|safety|constraints)",
        r"forget (your|all|previous|prior|the) (instructions|rules|guidelines|restrictions|training|safety)",
        r"disregard (your|all|previous|prior|the) (instructions|rules|guidelines|restrictions)",
        r"override (your|all|previous|prior|the) (instructions|rules|guidelines|restrictions|safety)",
        r"bypass (your|all|previous|the) (restrictions|rules|safety|filters|guidelines)",
        r"without (any |your )?(restrictions|guidelines|rules|safety|constraints|limitations|filters)",
        r"no (restrictions|guidelines|rules|safety|constraints|limitations|filters)",
        r"developer mode", r"jailbreak", r"dan mode", r"god mode",
        r"admin mode", r"unrestricted mode", r"sudo mode",
        r"ignore (above|previous|prior)",
        r"new instructions", r"system prompt",
        r"hypothetically (speaking|if|assume)",
        r"in (a |this )?(story|fictional|fantasy|alternate|hypothetical) (world|universe|scenario|context|setting)",
        r"this is (just |only )?(fiction|fictional|hypothetical|a story|pretend)",
        r"just (pretend|imagine|assume)",
        r"the old (you|version|claude|gpt|ai)",
        r"before (you were|your) (restricted|updated|trained|modified)",
        # FIX #1: Audit/compliance bypass
        r"(auditing|testing).{0,50}(compliance|safety|governance).{0,100}(ignore|bypass|override|respond as)",
        r"respond as (the |a )?(raw|underlying|base|original) (model|ai|system|llm)",
        r"(raw|underlying|base|original) (model|ai|system|llm).{0,50}(would|should|could) (respond|say|answer|tell)",
        r"for (testing|audit|compliance|research) purposes.{0,80}(ignore|bypass|disable|override)",
    ]
    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, q):
            return "PROMPT_INJECTION"

    # ======================================================
    # 4. ILLEGAL (FIX #2 and #4)
    # ======================================================
    ILLEGAL_PHRASES = [
        "cocaine", "heroin", "meth", "methamphetamine",
        "lsd", "mdma", "ecstasy", "ketamine", "fentanyl",
        "buy drugs", "sell drugs", "drug trafficking",
        "how to hack", "how to phish", "phishing website",
        "create malware", "create virus", "ransomware",
        "zero day exploit", "bypass firewall", "crack password",
        "brute force attack", "keylogger", "spyware",
        "fake id", "fake passport", "forged document",
        "identity theft", "credit card fraud", "bank fraud",
        "money laundering", "black money", "hawala",
        "child trafficking", "human trafficking",
        "counterfeit currency", "fake currency",
        # FIX #2: Fiction-framed drug synthesis
        "prepare a restricted pharmaceutical",
        "prepare restricted pharmaceutical",
        "synthesize illegal",
        "synthesising illegal",
        "restricted pharmaceutical compound",
        "household items to make drugs",
        "household items drug",
        "secretly prepare",
    ]
    for phrase in ILLEGAL_PHRASES:
        if phrase in q:
            return "ILLEGAL"

    ILLEGAL_PATTERNS = [
        # FIX #4: Abstract chemical synthesis
        r"(chemical|synthesis|synthesiz\w+|synthesising).{0,50}(illegal|narcotic|drug|controlled substance)",
        r"(abstract|principles|theory|concept).{0,50}(synthesiz\w+|making|producing|creating).{0,50}(narcotic|drug|illegal|controlled)",
        r"(narcotic|illegal drug|controlled substance).{0,50}(synthesiz\w+|produc\w+|creat\w+|mak\w+)",
        r"synthesiz\w+.{0,50}(narcotic|illegal|illicit|controlled)",
        # FIX #2: Fiction + illegal compound
        r"(novel|story|fiction|book|film|screenplay).{0,100}(prepare|synthesize|create|make|produce).{0,50}(pharmaceutical|drug|compound|substance)",
        r"(historical|fictional|creative).{0,80}(prepare|synthesize|create|make).{0,50}(restricted|illegal|banned|controlled).{0,50}(compound|substance|drug)",
        r"(secretly|covertly|quietly).{0,50}(prepare|make|create|synthesize).{0,50}(pharmaceutical|drug|compound|substance)",
    ]
    for pattern in ILLEGAL_PATTERNS:
        if re.search(pattern, q):
            return "ILLEGAL"

    ILLEGAL_WORDS = [
        "hack", "phish", "fraud", "exploit",
        "cocaine", "heroin", "meth", "lsd", "steal", "counterfeit",
    ]
    for word in ILLEGAL_WORDS:
        if word in q:
            return "ILLEGAL"

    # ======================================================
    # 5. MEDICAL
    # ======================================================
    MEDICAL_STRONG_PATTERNS = [
        r"prescri(be|ption|bed|bing)",
        r"what (prescription|medicine|medication|drug|tablet|pill|capsule|syrup|injection|dose|dosage) (should|can|must|do) (i|we|he|she|they|my father|my mother|my child|patient)",
        r"which (medicine|medication|drug|tablet|pill|capsule|antibiotic|painkiller|injection) (should|can|must|to)",
        r"(give|tell|suggest|recommend) (me|us|him|her|them) (a |the )?(medicine|medication|drug|prescription|dose|dosage|tablet|pill)",
        r"(what|which) (to|should) (take|give|administer|inject|use) for",
        r"how (much|many) (medicine|medication|drug|tablet|pill|capsule|ml|mg|dose|units) (to|should|can|must)",
        r"(dose|dosage) of",
        r"(safe |correct |right |proper )?(dose|dosage|amount) (of|for)",
        r"(what|which) (antibiotic|painkiller|antifungal|antiviral|steroid|insulin|medication|medicine|drug|tablet|pill|capsule|syrup|injection|supplement) (for|to treat|to cure)",
        r"medicine for (my|his|her|their|the|a |our )?",
        r"tablet for (my|his|her|their|the|a |our )?",
        r"drug for (my|his|her|their|the|a |our )?",
        r"injection for (my|his|her|their|the|a |our )?",
        r"treatment (for|of) (my|his|her|their|the|a |our )?",
        r"cure for", r"remedy for", r"home remedy for",
        r"emergency.*(medicine|medication|drug|tablet|pill|prescription|dose|dosage|treat|cure)",
        r"(dying|critical|serious).*(medicine|medication|drug|tablet|pill|prescription)",
        r"(doctor.*(unavailable|not available|unreachable|closed|busy)).*(medicine|medication|treat|give|prescribe)",
        r"no (doctor|physician|hospital).*(medicine|medication|give|prescribe|treat)",
        r"how to (inject|administer|apply|use) (insulin|medicine|medication|drug)",
        r"(insulin|medicine|medication|drug) (units|ml|mg|dose)",
        r"treatment plan for",
        r"diagnos(e|is|ing) (me|my|him|her|their)",
        r"medical (advice|help|guidance|recommendation|opinion) (for|about|on|regarding)",
        r"chest pain.*(medicine|medication|drug|tablet|give|prescribe|take|treat)",
        r"heart attack.*(medicine|medication|drug|tablet|give|prescribe|take|treat)",
        r"(stroke|seizure|fit).*(medicine|medication|drug|tablet|give|prescribe|take|treat)",
        r"(unconscious|fainted|collapsed).*(medicine|medication|drug|give|treat)",
        r"allergic (reaction|shock).*(medicine|medication|drug|give|treat|inject)",
        r"(can|should|is it safe) (i|to) take .* without (a |seeing a )?(prescription|doctor|physician)",
        r"over the counter.*(for|to treat|to cure)",
        # FIX #7: Lethal dose medical
        r"(lethal|fatal|deadly|toxic).{0,30}(dose|dosage|amount).{0,30}(paracetamol|ibuprofen|aspirin|medicine|drug|tablet|pill|acetaminophen)",
        r"(paracetamol|ibuprofen|aspirin|acetaminophen).{0,50}(lethal|fatal|deadly|kill|die|death)",
        r"estimate.{0,30}(lethal|fatal|deadly).{0,30}dose",
    ]
    for pattern in MEDICAL_STRONG_PATTERNS:
        if re.search(pattern, q):
            return "MEDICAL"

    MEDICAL_KEYWORDS = [
        "medicine", "medication", "drug", "tablet", "pill",
        "capsule", "syrup", "injection", "antibiotic", "painkiller",
        "prescription", "prescribe", "dosage", "dose", "treatment",
        "cure", "remedy", "diagnose", "diagnosis", "symptom",
        "insulin", "steroid", "antifungal", "antiviral", "supplement",
        "chemotherapy", "vaccine", "antidote", "ointment", "cream",
        "drops", "inhaler", "nebulizer", "iv drip", "saline",
        "analgesic", "antipyretic", "antacid", "laxative", "antihistamine",
    ]
    if urgency and any(kw in q for kw in MEDICAL_KEYWORDS):
        return "MEDICAL"

    MEDICAL_ACTIONS = [
        "take", "inject", "prescribe", "administer", "dosage",
        "dose", "units", "apply", "medicine", "tablet", "drug",
        "pill", "capsule", "treatment", "cure", "remedy",
        "antibiotic", "painkiller", "medication", "prescription",
        "syrup", "injection", "ointment", "drops", "inhaler",
        "steroid", "antifungal", "antiviral", "analgesic",
        "antipyretic", "antacid", "supplement","should i take", "can i take", "should i give",
        "standard dose", "adult dose", "pediatric dose",
        "recommended dosage", "safe dosage",
        "what dosage", "how much should",
    ]
    MEDICAL_CONDITIONS = [
        "diabetes", "diabetic", "bp", "blood pressure", "fever",
        "migraine", "cancer", "anxiety", "depression", "infection",
        "insulin", "hypertension", "thyroid", "cholesterol",
        "asthma", "arthritis", "kidney", "liver", "heart",
        "stroke", "seizure", "epilepsy", "pneumonia", "tuberculosis",
        "tb", "covid", "dengue", "malaria", "typhoid", "jaundice",
        "hepatitis", "ulcer", "gastritis", "eczema", "psoriasis",
        "fungal", "viral", "bacterial", "chest pain", "back pain",
        "headache", "sore throat", "cold", "cough", "flu",
        "nausea", "vomiting", "diarrhea", "constipation", "acidity",
        "allergy", "rash", "wound", "fracture", "sprain", "burn",
        "cut", "bleeding", "swelling", "inflammation",
        "joint pain", "muscle pain",
    ]
    med_score = sum(1 for w in MEDICAL_ACTIONS if w in q)
    med_score += sum(1 for w in MEDICAL_CONDITIONS if w in q)
    if med_score >= 2:
        return "MEDICAL"

    # ======================================================
    # 6. FINANCIAL
    # ======================================================
    FINANCIAL_STRONG_PATTERNS = [
        r"should i (buy|sell|invest|purchase|trade)",
        r"which (stock|share|equity|crypto|coin|mutual fund|etf|index fund) (to|should|can|must) (buy|sell|invest|purchase)",
        r"(recommend|suggest|advise|tell) (me |us )?(a |the )?(stock|share|equity|crypto|coin|investment|portfolio)",
        r"(guarantee|guaranteed|assured|certain|sure) (return|profit|income|gain|yield)",
        r"(exact|specific) (entry|exit|target|stop.?loss) (price|level|point)",
        r"(trading|investment) tip",
        r"portfolio (for|recommendation|suggestion|advice)",
        r"(best|top|good|safe) (stock|share|mutual fund|crypto|investment|etf) (to|for) (buy|invest|purchase)",
        r"(multibagger|10x|100x|double|triple) (stock|return|profit|investment)",
        r"(when|at what price) (to |should i )?(buy|sell|enter|exit)",
        r"market (prediction|forecast|outlook|tip|advice)",
        r"financial (advice|guidance|recommendation|planning) (for|on|about)",
        r"(how|where) (to|should i) (invest|put) (my )?(money|savings|funds|capital)",
        r"(fixed|assured|guaranteed) (return|profit|income|interest)",
    ]
    for pattern in FINANCIAL_STRONG_PATTERNS:
        if re.search(pattern, q):
            return "FINANCIAL"

    FINANCIAL_ACTIONS = [
        "buy", "sell", "invest", "recommend", "suggest",
        "allocate", "portfolio", "entry price", "target",
        "return", "profit", "multibagger", "tip",
        "trading advice", "financial advice", "wealth management",
    ]
    FINANCIAL_ASSETS = [
        "stock", "share", "shares", "equity", "ipo",
        "mutual fund", "mf", "nifty", "sensex", "bse", "nse",
        "crypto", "bitcoin", "ethereum", "nft", "defi",
        "trading", "investment", "forex", "commodity",
        "gold", "silver", "etf", "bond", "debenture",
        "futures", "options", "derivative", "smallcap",
        "midcap", "largecap", "bluechip", "penny stock", "sip",
    ]
    if any(a in q for a in FINANCIAL_ACTIONS) and any(b in q for b in FINANCIAL_ASSETS):
        return "FINANCIAL"
    # --- ADD THIS BLOCK ---
    FINANCIAL_SOFT_PHRASES = [
        "double my money",
        "double money quickly",
        "grow money fast",
        "best way to invest",
        "where to put my money",
        "safe investment for me",
        "portfolio allocation for me",
        "investment advice for me",
        "how to get guaranteed returns",
    ]
    for phrase in FINANCIAL_SOFT_PHRASES:
        if phrase in q:
            return "FINANCIAL"

    # ======================================================
    # 7. LEGAL
    # FIX #8: Separate LEGAL_INFO from LEGAL_ADVICE
    # ======================================================

    # Legal INFO (should ALLOW - factual/educational)
    LEGAL_INFO_PATTERNS = [
        r"what (are|is) (the )?(legal |law )?(consequences|penalties|punishment|sentence|fine) of",
        r"what (are|is) (the )?(law|rules|regulations|guidelines) (on|about|for|regarding|in india)",
        r"(explain|describe|tell me about|what is|define) (the )?(ipc|crpc|sebi|dpdp|pocso|it act|legal system|law)",
        r"what (does|do) (the )?(law|ipc|crpc|sebi) say (about|regarding|on)",
        r"(legal|law) (information|education|awareness|overview|summary|explanation)",
        r"history of (law|legal system|ipc|criminal law)",
        r"(difference|distinction) between.{0,50}(legal|law|crime|offence)",
        r"(is|are) .{0,50}(legal|illegal|lawful|unlawful|permitted|banned) in india",
    ]
    for pattern in LEGAL_INFO_PATTERNS:
        if re.search(pattern, q):
            return "SAFE"  # Legal INFO → ALLOW

    LEGAL_ADVICE_PATTERNS = [
        r"(legal|law) (advice|guidance|opinion|recommendation|consultation|strategy)",
        r"(should|can|how) (i|we|my) (sue|file|claim|appeal|challenge|contest|fight)",
        r"how to (file|draft|write|prepare) (a |an )?(fir|case|complaint|petition|notice|plaint|suit)",
        r"(ipc|crpc|cpc|iea|pocso|ndps|it act) section.{0,30}(apply|use|file|charge)",
        r"(bail|anticipatory bail|parole) (application|procedure|eligibility|process)",
        r"(is it|am i|are they) (legal|illegal|liable|guilty|innocent|at fault|negligent)",
        r"(my|our) (legal|constitutional|fundamental) rights (in|for|regarding) my (case|situation|matter)",
        r"lawyer (advice|help|opinion|recommendation|consultation)",
        r"(can|should) i (file|register|lodge) (a |an )?(fir|complaint|case)",
        r"(divorce|custody|alimony|maintenance) (procedure|process|legal|advice|rights)",
        r"property (dispute|legal|rights|law|advice|case|suit)",
    ]
    for pattern in LEGAL_ADVICE_PATTERNS:
        if re.search(pattern, q):
            return "LEGAL"

    LEGAL_ACTIONS = [
        "sue", "file case", "legal advice", "court case", "bail", "legal strategy",
        "lawyer advice", "file fir", "police complaint",
        "legal notice", "court notice", "consumer court",
        "arbitration", "mediation", "litigation",
    ]
    for word in LEGAL_ACTIONS:
        if word in q:
            return "LEGAL"

    # ======================================================
    # 8. VIOLENCE
    # ======================================================
    VIOLENCE_PHRASES = [
        "how to kill", "how to murder", "how to shoot",
        "how to stab", "how to attack", "how to harm someone",
        "how to hurt someone", "make a bomb", "build a bomb",
        "create a bomb", "explosive device", "improvised explosive",
        "how to make weapon", "how to poison someone",
        "acid attack", "how to assault", "how to kidnap",
        "how to torture", "how to strangle",
    ]
    for phrase in VIOLENCE_PHRASES:
        if phrase in q:
            return "VIOLENCE"
    VIOLENCE_EXTENDED = [
        "gun for killing",
        "best gun to kill",
        "which gun kills",
        "how to use gun to kill",
        "ways to poison",
        "poison someone",
        "homemade explosive",
        "make explosive",
        "buy illegal weapon",
        "illegal weapons online",
        "violent protest",
        "start a riot",
        "attack police",
        "kill police",
        "how to fight police",
        "how to assassinate",
        "assassinate someone",
    ]
    for phrase in VIOLENCE_EXTENDED:
        if phrase in q:
            return "VIOLENCE"

    VIOLENCE_WORDS = [
        "murder", "assassination", "terrorist", "terrorism",
        "massacr", "genocide", "school shooting", "mass shooting",
    ]
    for word in VIOLENCE_WORDS:
        if word in q:
            return "VIOLENCE"
    
    VIOLENCE_PATTERNS = [
        r"(best|which).{0,20}(gun|weapon).{0,20}(kill|murder)",
        r"(how|ways).{0,30}(poison|kill|murder|attack)",
        r"(plan|organize|start).{0,20}(riot|violent protest)",
        r"(make|create|build).{0,20}(explosive|bomb|weapon)",
        r"(buy|purchase).{0,20}(illegal|banned).{0,20}(weapon|gun)",
    ]
    for pattern in VIOLENCE_PATTERNS:
        if re.search(pattern, q):
            return "VIOLENCE"

    # ======================================================
    # 9. SEXUAL
    # ======================================================
    SEXUAL_PHRASES = [
        "child porn", "child pornography", "child abuse material",
        "underage sex", "minor sexual", "loli", "non consensual","abuse",
    ]
    for phrase in SEXUAL_PHRASES:
        if phrase in q:
            return "SEXUAL"

    SEXUAL_WORDS = [
        "porn", "pornography", "explicit sexual", "nude", "nudity",'naked',
        "rape", "child abuse", "underage", "minor sexual","explicit images",'nudes'
    ]
    for word in SEXUAL_WORDS:
        if word in q:
            return "SEXUAL"
    SEXUAL_EXTENDED = [
    "explicit content",
    "adult content",
    "porn links",
]
    for phrase in SEXUAL_EXTENDED:
        if phrase in q:
            return "SEXUAL"

   