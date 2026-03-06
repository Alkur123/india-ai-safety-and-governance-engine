# <img src="https://flagcdn.com/48x36/in.png" width="36" height="27" alt="India Flag" style="vertical-align: middle;"/> India AI Governance Engine (V2) — Model Card

> *Submitted for AI for Bharat Hackathon 2026*
> 
> **Powered by Hack2Skill | Powered by AWS**
> 
> **🏆 Building Digital India's AI Safety Infrastructure**

---

## 1. 🧠 Model Overview

The India AI Governance Engine uses a combination of lightweight machine learning models and deterministic policy logic to enforce pre-generation AI safety governance.

Unlike traditional moderation systems that filter responses *after* generation, this system evaluates prompts *before* an LLM generates a response, ensuring deterministic and auditable safety enforcement.

The system integrates multiple model components including:
- Semantic safety detection
- Intent classification
- Risk scoring
- Language model generation

---

## 2. 🧩 Model Components

### 2.1 Semantic Safety Engine
- **Model:** `sentence-transformers/all-MiniLM-L6-v2`
- **Purpose:** Detect harmful semantic intent even when users paraphrase unsafe requests.

**Example Semantic Detection:**
| Prompt | Detection |
| :--- | :--- |
| *"How to kill myself?"* | **SELF_HARM** |
| *"How can I disappear forever?"* | **SELF_HARM** |

The model generates sentence embeddings and computes similarity against known harmful patterns. Threshold-based classification determines whether the query is unsafe.

### 2.2 Intent Classification
Intent classification determines the governance category of a user query. 

**Categories include:**
- Medical advice
- Legal advice
- Financial advice
- Violence
- Illegal activity
- Self-harm
- Safe informational queries

Intent classification enables mapping prompts to regulatory policies.

### 2.3 Language Model (Generation)
- **Model:** `Google FLAN-T5` *(or any wrapped LLM like Bedrock/OpenAI)*
- **Purpose:** Generate responses for queries that pass governance checks.

The LLM is invoked only *after* safety evaluation is completed. This ensures that unsafe prompts never reach the generation layer.

---

## 3. 📚 Training Data

The governance models rely primarily on:
- Publicly available sentence transformer models
- Curated governance prompt datasets
- Regulatory domain examples

**Evaluation dataset:**
- 69 governance test queries
- Multiple risk categories
- Adversarial prompts
- Safe informational prompts

**Categories covered include:** Medical advice, Legal advice, Financial advice, Violence, Self-harm, and Prompt injection.

---

## 4. 📊 Evaluation Metrics

Evaluation was conducted on a curated governance dataset.

| Metric | Value | Detail |
| :--- | :--- | :--- |
| **Precision** | 0.98 | Low false positive rate |
| **Recall** | 0.76 | High violation detection rate |
| **F1 Score** | 0.86 | Balanced performance |
| **True Positives** | 44 | Correctly identified violations |
| **True Negatives** | 61 | Correctly identified safe prompts |

**Category-level performance:**

| Category | Precision | Recall |
| :--- | :--- | :--- |
| **Medical** | 1.00 | 1.00 |
| **Legal** | 1.00 | 1.00 |
| **Financial** | 0.83 | 1.00 |
| **Violence** | 1.00 | 1.00 |
| **Self-Harm** | 1.00 | 0.86 |

---

## 5. 🎯 Intended Use

The governance engine is designed for:
- Regulated AI deployments
- Enterprise AI systems
- Government AI applications
- Healthcare AI interfaces
- Financial advisory chat systems

The system ensures that LLMs operate strictly within Indian regulatory and ethical constraints.

---

## 6. 🚫 Out-of-Scope Use Cases

The system is **not** designed for:
- Replacing professional medical advice
- Legal consultation systems
- Autonomous decision making
- High-risk safety-critical environments

The governance layer only enforces policy constraints, not expert guidance.

---

## 7. ⚖️ Ethical Considerations

AI governance systems must balance **safety enforcement**, **user freedom**, and **regulatory compliance**.

**Potential ethical considerations include:**
- False positives blocking legitimate educational questions
- Cultural and linguistic interpretation differences
- Evolving regulatory frameworks

Continuous monitoring and policy updates are required to maintain fairness and accuracy.

---

## 8. ⚠️ Limitations

Current system limitations include:
- Limited multilingual support (English/Hindi focus)
- Prompt-level evaluation rather than claim-level reasoning
- Static policy rules
- Reliance on curated semantic patterns
- Limited adversarial robustness against highly novel novel attacks

---

## 9. 🔮 Future Improvements (V3 Roadmap)

Future versions will introduce advanced alignment architectures:
- Claim-level reasoning for prompt decomposition
- Stability verification across paraphrased prompts
- Multilingual governance enforcement (Tamil, Telugu, Bengali, Marathi)
- Regulatory knowledge retrieval (RAG)
- Telemetry-driven policy learning

---

## 10. 🛡️ Responsible AI Compliance

The governance engine strictly aligns with responsible AI principles including **transparency, explainability, safety, and accountability**.

Each decision produces an **explainability trace** showing exactly how governance decisions were made:

```text
00ms : Euphemism expansion
05ms : Intent classification
10ms : PII detection
15ms : Attack analysis
20ms : Semantic safety check
30ms : Policy enforcement
50ms : Decision → BLOCK
```

---

## 11. ☁️ Deployment Context

The system is deployed using scalable cloud infrastructure:
- **Containerization:** Docker containers
- **Hosting:** AWS EC2 (ap-south-1, Mumbai)
- **Registry:** AWS Elastic Container Registry (ECR)

The architecture supports a scalable, secure, and fully auditable AI governance infrastructure
