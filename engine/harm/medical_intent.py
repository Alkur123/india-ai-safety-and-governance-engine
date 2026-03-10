import re

# ==========================================================
# MEDICAL INTENT DETECTOR
# India AI Governance Engine V2
# ==========================================================

def normalize_medical(text: str) -> str:
    text = text.lower()
    replacements = {
        "3": "e", "1": "i", "@": "a", "$": "s",
        "0": "o", "4": "a", "5": "s", "7": "t",
        "8": "b", "9": "g", "|": "i", "!": "i", "(": "c",
    }
    for k, v in replacements.items():
        text = text.replace(k, v)
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def detect_medical_intent(query: str) -> str:
    """
    Returns:
        "ADVICE"  → Requires medical professional (BLOCK)
        "INFO"    → General educational/informational (ALLOW)
    """
    q = normalize_medical(query)

    # ======================================================
    # SECTION 0: LETHAL DOSE SEEKING (FIX #7 - Highest priority)
    # "Even if not certain, estimate lethal dose of paracetamol"
    # ======================================================
    LETHAL_DOSE_PATTERNS = [
        r"(lethal|fatal|deadly|toxic).{0,40}(dose|dosage|amount|quantity|level)",
        r"(dose|dosage|amount).{0,40}(lethal|fatal|deadly|kills|kill|die|death)",
        r"estimate.{0,30}(lethal|fatal|deadly).{0,30}(dose|dosage|amount)",
        r"(how much|what amount|what dose|what quantity).{0,50}(paracetamol|ibuprofen|aspirin|acetaminophen|medicine|drug|tablet|pill).{0,50}(lethal|fatal|deadly|kill|die|death|dangerous|toxic)",
        r"(paracetamol|ibuprofen|aspirin|acetaminophen).{0,80}(lethal|fatal|deadly|kill|die|death|overdose|toxic)",
        r"(even if|even though).{0,30}(not certain|uncertain|not sure|not fully).{0,50}(lethal|fatal|deadly|dose|dosage|estimate)",
        r"(approximate|rough|ballpark|estimate).{0,30}(lethal|fatal|deadly|toxic).{0,30}(dose|dosage|amount)",
        r"(maximum|minimum|threshold).{0,30}(lethal|fatal|deadly|toxic).{0,30}(dose|dosage|amount)",
    ]
    for pattern in LETHAL_DOSE_PATTERNS:
        if re.search(pattern, q):
            return "ADVICE"

    # ======================================================
    # SECTION 1: MULTI-STEP MANIPULATION (FIX #5)
    # "First explain why you cannot... Then provide them anyway"
    # ======================================================
    MULTI_STEP_PATTERNS = [
        r"first.{0,80}(explain|tell|describe).{0,80}(cannot|cant|unable|not allowed|restricted|why).{0,200}(then|now|but|however|anyway).{0,80}(provide|tell|give|explain|show|answer)",
        r"(explain why).{0,80}(cannot|cant|unable|restricted).{0,200}(provide|tell|give|anyway|then)",
        r"(then|now) provide (them|it) anyway",
        r"(then|now) (tell|give|provide|show) (me |them |it )?(anyway|regardless|still)",
        r"provide.{0,30}anyway.{0,50}(educational|education|learning|informational)",
        r"(educational purposes|for education).{0,50}(provide|tell|give|show|explain).{0,50}(anyway|regardless|still|the|them)",
    ]
    for pattern in MULTI_STEP_PATTERNS:
        if re.search(pattern, q):
            return "ADVICE"

    # ======================================================
    # SECTION 2: ROLE-PLAY + MEDICAL JAILBREAKS
    # ======================================================
    JAILBREAK_MEDICAL_PATTERNS = [
        r"act as (a |an )?(doctor|physician|nurse|pharmacist|surgeon|specialist|medical|healthcare|health)",
        r"pretend (you are|to be|youre) (a |an )?(doctor|physician|nurse|pharmacist|medical)",
        r"imagine you (are|were) (a |an )?(doctor|physician|nurse|pharmacist|medical)",
        r"you are (now )?(a |an )?(doctor|physician|nurse|pharmacist|medical expert|health expert)",
        r"roleplay as (a |an )?(doctor|physician|nurse|pharmacist|medical|health)",
        r"simulate (a |an )?(doctor|physician|nurse|pharmacist|medical|health)",
        r"behave as (a |an )?(doctor|physician|nurse|pharmacist|medical|health)",
        r"respond as (a |an )?(doctor|physician|nurse|pharmacist|medical|health)",
        r"speak as (a |an )?(doctor|physician|nurse|pharmacist|medical|health)",
        r"hypothetically.*(medicine|medication|drug|prescri|dose|dosage|treat|diagnose)",
        r"in (a |this )?(fictional|hypothetical|alternate|story|novel|game).*(medicine|medication|drug|prescri|dose|treat|diagnose)",
        r"for (a |my )?(story|novel|fiction|game|research).*(medicine|medication|drug|prescri|dose|treat|diagnose)",
        r"what (would|should|could) (a |the )?(doctor|physician|nurse|pharmacist) (say|tell|advise|prescribe|recommend|suggest)",
        r"if you were (a |the )?(doctor|physician|nurse|pharmacist).*(what|how|which|prescribe|recommend)",
        r"as (a |the )?(doctor|physician|nurse|pharmacist).*(what|how|which|prescribe|recommend|advise)",
        r"(emergency|urgent|critical|dying|life or death).*(prescri|medicine|medication|drug|dose|dosage|what to give|what to take)",
        r"(no time|cannot wait|cant wait|hurry).*(prescri|medicine|medication|drug|dose|dosage|what to give)",
        r"(doctors?|physician|hospital|clinic).*(unavailable|not available|closed|unreachable|busy|not here).*(medicine|medication|drug|prescri|dose|treat|give)",
        r"(without|no need for|skip).*(doctor|physician|hospital|clinic).*(medicine|medication|prescri|treat|diagnose)",
        r"self (treat|diagnose|medicate|prescribe).*(medicine|medication|drug|condition|symptom)",
    ]
    for pattern in JAILBREAK_MEDICAL_PATTERNS:
        if re.search(pattern, q):
            return "ADVICE"

    # ======================================================
    # SECTION 3: STRONG PRESCRIPTION / DOSAGE PATTERNS
    # ======================================================
    PRESCRIPTION_PATTERNS = [
        r"prescri(be|bed|bing|ption)",
        r"what (prescription|medicine|medication|drug|tablet|pill|capsule|syrup|injection|dose|dosage)",
        r"which (prescription|medicine|medication|drug|tablet|pill|capsule|syrup|injection|antibiotic|painkiller|antifungal|antiviral|steroid)",
        r"\bdosage\b", r"\bdose\b",
        r"how (much|many).*(take|inject|use|give|administer|consume|apply)",
        r"(correct|safe|right|proper|exact|recommended|maximum|minimum).*(dose|dosage|amount|quantity|units)",
        r"(units?|ml|mg|mcg|iu|grams?|tablets?|pills?|capsules?) (to|of|per|daily|twice|thrice|weekly)",
        r"(twice|thrice|once|two times|three times) (a |per )?(day|week|daily|weekly)",
        r"how often (to|should|can|must) (take|inject|use|give|administer|apply)",
        r"(give|tell|suggest|recommend|advise) (me|us|him|her|them|patient).{0,20}(medicine|medication|drug|tablet|pill|capsule|prescription|dose|dosage|injection|antibiotic|treatment)",
        r"(what|which).*(should|can|must|do|to) (take|give|use|inject|administer|apply)",
        r"(what|which).*(to take|to give|to inject|to use|to administer|to apply) for",
        r"(antibiotic|antifungal|antiviral|antiparasitic|steroid|corticosteroid|nsaid|analgesic|antipyretic|antihistamine|antacid|laxative|diuretic|beta.?blocker|ace inhibitor|statin|anticoagulant|blood thinner|antidepressant|antipsychotic|anxiolytic|sedative|hypnotic|stimulant|anticonvulsant|muscle relaxant|bronchodilator|decongestant) (for|to treat|to cure|to manage|dosage|dose|how much|which|what)",
        r"treatment plan (for|of)",
        r"(treatment|therapy|regimen) (for|of) (my|his|her|their|the|a |our )?(condition|disease|illness|disorder|problem|infection|pain|symptoms?)",
        r"how to treat (my|his|her|their|the|a |our )?(condition|disease|illness|disorder|problem|infection|pain|symptoms?)",
        r"cure for",
        r"(home |natural |herbal )?(remedy|remedies|cure|treatment) for",
        r"medicine for (my|his|her|their|the|a |our )?",
        r"medication for (my|his|her|their|the|a |our )?",
        r"drug for (my|his|her|their|the|a |our )?",
        r"tablet for (my|his|her|their|the|a |our )?",
        r"injection for (my|his|her|their|the|a |our )?",
        r"antibiotic for (my|his|her|their|the|a |our )?",
        r"treatment for (my|his|her|their|the|a |our )?",
        r"(best|good|safe|effective|strongest) (medicine|medication|drug|tablet|pill|antibiotic|treatment) (for|to treat|to cure)",
        r"(can|should) (i|we) (buy|get|take) .* (without|no) (prescription|doctor|physician)",
        r"over.?the.?counter.*(for|to treat|to cure)",
        r"(insulin|injection|iv|drip|saline).*(dose|dosage|units?|how much|how many|when|how often)",
        r"insulin.*(units?|dose|dosage|how much|injection|inject)",
        r"(diagnose|diagnosis|diagnos\w+).*(me|my|him|her|their|patient|condition|symptoms?|disease)",
        r"(is|am|are) (i|he|she|they|my \w+).*(sick|ill|infected|having|suffering|diagnosed|diabetic|hypertensive|allergic|pregnant)",
        r"(what|which) (disease|condition|illness|disorder|infection|problem) (do i|does he|does she|do they|is it|could it be)",
        r"do i have (a |the )?(disease|condition|illness|disorder|infection)",
        r"(medical|health|doctor) (advice|guidance|opinion|recommendation|consultation|help) (for|about|on|regarding)",
    ]
    for pattern in PRESCRIPTION_PATTERNS:
        if re.search(pattern, q):
            return "ADVICE"

    # ======================================================
    # SECTION 4: EMERGENCY + MEDICAL COMBINATION
    # ======================================================
    URGENCY_SIGNALS = [
        "emergency", "urgent", "immediately", "right now",
        "no time", "hurry", "asap", "critical", "dying",
        "life or death", "cant wait", "cannot wait",
        "no time to waste", "quickly", "fast",
        "doctors unavailable", "no doctor", "hospital closed",
        "cant reach doctor", "cannot reach",
    ]
    MEDICAL_TREATMENT_SIGNALS = [
        "medicine", "medication", "drug", "tablet", "pill",
        "capsule", "syrup", "injection", "antibiotic", "prescription",
        "prescribe", "dosage", "dose", "treatment", "cure",
        "remedy", "what to give", "what to take", "how to treat",
        "what should i give", "what can i give", "what to do for",
        "help him", "help her", "save him", "save her",
    ]
    has_urgency = any(signal in q for signal in URGENCY_SIGNALS)
    has_medical_treatment = any(signal in q for signal in MEDICAL_TREATMENT_SIGNALS)
    if has_urgency and has_medical_treatment:
        return "ADVICE"

    # ======================================================
    # SECTION 5: DANGEROUS EMERGENCY PATTERNS
    # ======================================================
    EMERGENCY_MEDICAL_PATTERNS = [
        r"(chest|heart).*(pain|attack|failure).*(medicine|medication|drug|give|prescribe|take|treat|what|how)",
        r"(stroke|seizure|fit|epilepsy).*(medicine|medication|drug|give|prescribe|take|treat|what|how)",
        r"(unconscious|fainted|collapsed|not responding).*(medicine|medication|drug|give|treat|what|how|do)",
        r"(allergic|anaphylaxis|shock).*(medicine|medication|drug|give|inject|treat|what|how|epipen|epinephrine)",
        r"(overdose|poisoning|poison|toxic|ingested).*(medicine|medication|drug|treat|antidote|what|how)",
        r"(baby|infant|child|newborn|toddler).*(fever|sick|ill|not breathing|seizure|fit).*(what|how|medicine|medication|give|do|treat)",
    ]
    for pattern in EMERGENCY_MEDICAL_PATTERNS:
        if re.search(pattern, q):
            return "ADVICE"

    # ======================================================
    # SECTION 6: DUAL SCORING
    # ======================================================
    MEDICAL_ACTION_WORDS = [
        "take", "inject", "prescribe", "administer", "consume",
        "apply", "use", "give", "swallow", "drink",
        "dosage", "dose", "units", "quantity", "amount",
        "medicine", "tablet", "drug", "pill", "capsule",
        "treatment", "cure", "remedy", "antibiotic",
        "painkiller", "medication", "prescription",
        "syrup", "injection", "ointment", "drops",
        "inhaler", "steroid", "antifungal", "antiviral",
        "analgesic", "antipyretic", "antacid", "supplement",
    ]
    MEDICAL_CONDITION_WORDS = [
        "diabetes", "diabetic", "bp", "blood pressure", "hypertension",
        "fever", "migraine", "cancer", "anxiety", "depression",
        "infection", "insulin", "thyroid", "cholesterol",
        "asthma", "arthritis", "kidney", "liver", "heart",
        "stroke", "seizure", "epilepsy", "pneumonia", "tuberculosis",
        "tb", "covid", "dengue", "malaria", "typhoid",
        "jaundice", "hepatitis", "ulcer", "gastritis",
        "eczema", "psoriasis", "fungal", "viral", "bacterial",
        "chest pain", "back pain", "headache", "sore throat",
        "cold", "cough", "flu", "nausea", "vomiting", "diarrhea",
        "constipation", "acidity", "allergy", "rash", "wound",
        "fracture", "sprain", "burn", "cut", "bleeding",
        "swelling", "inflammation", "joint pain", "muscle pain",
        "stomach pain", "abdominal pain", "breathlessness",
        "dizziness", "weakness", "fatigue",
        "pregnancy", "pregnant", "pcos", "pcod", "uti",
        "kidney stone", "gallstone", "bipolar", "schizophrenia",
        "adhd", "autism", "alzheimer", "parkinson",
    ]
    action_score = sum(1 for w in MEDICAL_ACTION_WORDS if w in q)
    condition_score = sum(1 for w in MEDICAL_CONDITION_WORDS if w in q)
    if action_score + condition_score >= 2:
        return "ADVICE"

    # ======================================================
    # SECTION 7: EDUCATIONAL / INFORMATIONAL (ALLOW)
    # FIX #3: Starvation/health questions → INFO not SELF_HARM
    # ======================================================
    INFO_PATTERNS = [
        r"how does .* work",
        r"how do .* work",
        r"mechanism of (action|.* drug|.* medicine|.* medication)",
        r"what is (a |an |the )?(medicine|drug|tablet|disease|condition|symptom|diagnosis|treatment|therapy|surgery)",
        r"what are (the )?(symptoms?|signs?|causes?|effects?|side effects?|complications?) of",
        r"(explain|describe|tell me about|what is|what are|define) (the )?(disease|condition|illness|disorder|syndrome|cancer|diabetes|hypertension|asthma|arthritis)",
        r"history of (medicine|medical|drug|disease|condition|treatment|surgery|healthcare)",
        r"(medical|health|anatomy|physiology|pharmacology|biology) (education|knowledge|information|basics|introduction|overview|concept)",
        r"(who|when|where|why|how) (was|is|are|were|did) .* (discovered|invented|developed|found|created|used|approved)",
        r"(awareness|prevention|precaution|lifestyle|diet|exercise|yoga|meditation) (for|of|about|regarding)",
        r"(benefit|advantage|disadvantage|risk|danger) of (exercise|yoga|meditation|diet|fasting|sleep)",
        r"(research|study|clinical trial|evidence|data|statistics) (on|about|regarding) (medicine|drug|treatment|disease|condition|therapy)",
        # FIX #3: Starvation/body questions are informational unless self-harm intent
        r"what (happens|occurs) (to|in) (the )?(body|person|human) (if|when|after) (someone|a person|you) (stops?|doesnt|does not|skips?) (eating|drinking|sleeping|exercising)",
        r"(effects?|impact|result) of (not eating|starvation|fasting|dehydration|sleep deprivation) on (the )?(body|health|person|human)",
        r"how (long|many days|much time) (can|could) (a person|someone|the body|humans?) (survive|go|last|live) without (eating|food|water|sleep)",
        r"what (is|are) (the )?(medical|physical|physiological) (effects?|consequences?|symptoms?) of (starvation|fasting|not eating|dehydration)",
    ]
    for pattern in INFO_PATTERNS:
        if re.search(pattern, q):
            return "INFO"

    return "INFO"


def get_medical_regulation(intent: str, category: str) -> str:
    if intent == "ADVICE" or category == "MEDICAL":
        return "Indian Medical Council (IMC) Act, 1956 - Section 15 & 20A"
    return "N/A"


def get_medical_risk_score(intent: str, has_urgency: bool = False, has_pii: bool = False) -> float:
    if intent == "ADVICE":
        score = 0.85
        if has_urgency: score = min(score + 0.10, 1.0)
        if has_pii:     score = min(score + 0.05, 1.0)
        return score
    return 0.15