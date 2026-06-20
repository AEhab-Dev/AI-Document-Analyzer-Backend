from groq import Groq
from app.core.config import settings

client = Groq(api_key=settings.GROQ_API_KEY)

MODEL = "llama-3.3-70b-versatile"

SUMMARY_SYSTEM_PROMPT = """You are a document analyst. Detect the document type (CV, Contract, Policy, or Report) and extract key information.

For CV: candidate name, experience, skills, education, last job.
For Contract: parties, dates, payment terms, termination, red flags.
For Policy: topic, scope, key rules, effective date.
For Report: topic, findings, recommendations.

Start with: **Document Type:** [type]
Use **bold** headers. Be concise."""

QA_SYSTEM_PROMPT = """Answer questions based ONLY on the document provided. If the answer is not in the document, say: "This information is not present in the document." Be concise."""


def generate_summary(document_text: str) -> tuple[str, str]:
    truncated = " ".join(document_text.split()[:3000])

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": SUMMARY_SYSTEM_PROMPT},
            {"role": "user", "content": f"Analyze this document:\n\n{truncated}"},
        ],
        temperature=0.2,
        max_tokens=800,
    )

    summary = response.choices[0].message.content.strip()

    doc_type = "general"
    summary_lower = summary.lower()
    if "cv" in summary_lower or "resume" in summary_lower:
        doc_type = "cv"
    elif "contract" in summary_lower:
        doc_type = "contract"
    elif "policy" in summary_lower:
        doc_type = "policy"

    return summary, doc_type


def answer_question(document_text: str, question: str, chat_history: list[dict]) -> str:
    truncated = " ".join(document_text.split()[:3000])

    messages = [
        {
            "role": "system",
            "content": f"{QA_SYSTEM_PROMPT}\n\nDOCUMENT:\n{truncated}",
        }
    ]

    for entry in chat_history[-4:]:
        messages.append({"role": entry["role"], "content": entry["content"]})

    messages.append({"role": "user", "content": question})

    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        temperature=0.1,
        max_tokens=500,
    )

    return response.choices[0].message.content.strip()