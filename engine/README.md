# 🛡️ AI Safety & Governance Engine
### *Inference-Time Governance Layer for Responsible AI in India*

[![Hackathon](https://img.shields.io/badge/AWS-AI%20for%20Bharat%20Hackathon-FF9900?style=for-the-badge&logo=amazonaws)](https://aws.amazon.com/) 
[![Python](https://img.shields.io/badge/Made%20with-Python-3776AB?style=for-the-badge&logo=python)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-Apache%202.0-green?style=for-the-badge)](./LICENSE)
[![Status](https://img.shields.io/badge/Status-Evaluation%20Phase-blue?style=for-the-badge)]()

---

## 🔗 Quick Links
- **[🎥 Live Demo (Hugging Face Space)](https://huggingface.co/spaces/jash-ai/AI-Governance-Engine)**
- **[💾 Download Model Card](./MODEL_CARD.md)**
- **[☁️ Deploy to AWS](#-deployment-aws-ready)**

---

## 1️⃣ The Problem
In India, integrating Large Language Models (LLMs) into public-sector and enterprise workflows carries critical risks that standard safety filters cannot address:
- **Unregulated Advice:** General-purpose LLMs often provide hallucinated or unverified medical, legal, and financial advice.
- **Data Leaks:** High risk of exposing sensitive Indian PII (Aadhaar, PAN, Mobile Numbers).
- **Audit Gaps:** Post-generation moderation is opaque, probabilistic, and hard to audit for regulatory compliance.

**The Gap:** Reliance on "aligned" models is not enough. Regulated industries need **deterministic, auditable guarantees** before an AI generates a single token.

## 2️⃣ The Solution
The **AI Safety & Governance Engine** is a deterministic, inference-time safety layer that sits *between* the user and the LLM. It enforces strict compliance with Indian regulations and organizational policies **before** generation occurs.

### How It Works
We treat governance as a separate, distinct layer from intelligence.
- **✅ Deterministic:** Same input = Same safety decision. No probabilistic guessing for compliance.
- **🇮🇳 India-Aware:** Built-in recognition of Indian regulatory frameworks (IMC, BCI, SEBI, IPC).
- **🔍 Auditable:** Every decision produces an immutable audit log, not just a rejected prompt.

## 3️⃣ Key Capabilities

### 🩺 Sector-Specific Regulatory Enforcement
We map user intent directly to Indian regulatory bodies:
| Domain | Regulation | Action |
| :--- | :--- | :--- |
| **Medical** | Indian Medical Council (IMC) | **BLOCK** & Redirect to licensed practitioner |
| **Legal** | Bar Council of India (BCI) | **BLOCK** & Cite liability risks |
| **Financial** | SEBI Advisory Rules | **BLOCK** & Warn against unregistered advice |
| **Illegal** | Indian Penal Code (IPC) | **BLOCK** & Log incident |

### 🔐 Indian PII Protection
Uses specialized regex patterns and context awareness to detect and redact sensitive Indian identifiers **before** they reach the LLM provider.
- **Aadhaar Numbers:** `XXXX-XXXX-XXXX`
- **PAN Cards:** `ABCDE1234F`
- **Mobile Numbers:** `+91-9876543210`
- **Voter IDs**

### 🌐 Accurate Language Detection
- Honest detection of **Hindi** and **English**.
- Prevents hallucinated multilingual reasoning in unsupported languages.
- *For V3: Expansion to Tamil and Telugu policy enforcement.*

## 4️⃣ Architecture
The engine operates as a stateless middleware.

```mermaid
graph TD
    User[User Query] --> PII[🔐 Indian PII Redaction]
    PII --> Intent[🚦 Harm & Intent Detection]
    Intent --> Policy[📜 Policy Engine (IMC/BCI/SEBI)]
    Policy --> Decision{Decision?}
    
    Decision -- 🔴 BLOCK --> BlockMsg[Block Response + Audit Log]
    Decision -- 🟡 ABSTAIN --> AbstainMsg[Uncertainty Fallback]
    Decision -- 🟢 ALLOW --> LLM[🤖 LLM Generation]
    
    LLM --> Verify[✅ Verification]
    Verify --> Output[Final Response]
```

## 5️⃣ Real-World Examples

#### 🔴 Scenario: Medical Advice (Blocked)
> **User:** "What medicine should I take for fever?"
>
> **Engine:** **BLOCKED**
> - **Category:** MEDICAL_ADVICE
> - **Regulation:** Indian Medical Council
> - **Reason:** AI cannot prescribe medication. Please consult a doctor.

#### 🔴 Scenario: Financial Tips (Blocked)
> **User:** "Which stock is best for 100% returns tomorrow?"
>
> **Engine:** **BLOCKED**
> - **Category:** FINANCIAL_ADVICE
> - **Regulation:** SEBI
> - **Reason:** Unregistered investment advice is prohibited.

#### 🟢 Scenario: General Knowledge + PII (Allowed & Redacted)
> **User:** "My Aadhaar is 5432-1098-7654. How do I update my address?"
>
> **Engine:** **ALLOWED (Redacted)**
> - **Input to LLM:** "My Aadhaar is <REDACTED_AADHAAR>. How do I update my address?"
> - **Output:** Provides official UIDAI address update steps.

## 6️⃣ Performance & Cost
| Feature | LLM-Based Moderation | **Governance Engine** |
| :--- | :--- | :--- |
| **Cost (1M reqs)** | $300 - $500 | **$5 - $15** (CPU-native) |
| **Latency** | 500ms - 2s | **< 50ms** |
| **Consistency** | Probabilistic (Varies) | **Deterministic (100%)** |
| **Hardware** | Requires GPUs | **Runs on generic Lambda/CPU** |

## 7️⃣ Deployment (AWS Ready)
Designed for horizontal scalability on AWS.
1.  **API Gateway**: Handles incoming requests.
2.  **AWS Lambda**: Runs the Python governance logic (stateless).
3.  **Amazon CloudWatch**: Tracks True/False positives and blocks.
4.  **Amazon S3 / DynamoDB**: Stores immutable audit logs for RTI compliance.

### Local Installation
```bash
# Clone the repository
git clone https://github.com/yourusername/ai-safety-governance.git
cd ai-safety-governance

# Install dependencies
pip install -r requirements.txt

# Run the engine
python main.py
```

## ⚠️ Limitations & Trade-offs
To prioritize safety and compliance, this system accepts specific trade-offs:

- **Rule-Based over Probabilistic:** We use regex and strict keyword matching for predictablity. This ensures legal defensibility but may miss nuanced edge cases or over-block benign queries.
- **Conservative Default:** Medical, legal, and financial queries are **blocked by default**. We prioritize preventing harm over providing information in these high-risk sectors.
- **Language Support:** Currently detects Hindi and English. Other languages are treated with high caution or blocked to prevent unmoderated responses.
- **Governance ≠ Intelligence:** This layer enforces policy; it does not reason. It is not a replacement for human judgment in complex, ambiguous scenarios.

## 8️⃣ Roadmap (V3)
- **Multilingual Governance:** Deep intent detection for Tamil, Telugu, and Kannada.
- **Human-in-the-Loop (HITL):** Workflow for reviewing `ABSTAIN` decisions.
- **Agentic Oversight:** Supervisor agents for multi-turn workflows.

---
*Built for the AWS AI for Bharat Hackathon 2026. Empowering responsible AI adoption in India.*
