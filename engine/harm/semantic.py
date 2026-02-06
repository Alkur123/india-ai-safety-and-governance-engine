from sentence_transformers import SentenceTransformer, util

model = SentenceTransformer("all-MiniLM-L6-v2")

SEMANTIC_PATTERNS = {
    "SELF_HARM": ["I don't want to exist","life is pointless","end everything"],
    "ILLEGAL": ["break into system","steal without trace"],
    "MEDICAL": ["what medicine should I take","safe dosage"]
}

embeds = {k:model.encode(v,convert_to_tensor=True) for k,v in SEMANTIC_PATTERNS.items()}

def semantic_match(q, threshold=0.65):
    q_emb=model.encode(q,convert_to_tensor=True)
    for cat,emb in embeds.items():
        score=util.cos_sim(q_emb,emb).max().item()
        if score>=threshold:
            return cat,score
    return None,0.0
