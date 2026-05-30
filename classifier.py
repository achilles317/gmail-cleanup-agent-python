# classifier.py — Ollama LLM email classifier
#
# Used for emails that don't match known sender rules.
# The LLM reads From, Subject, and snippet and decides: archive or keep.

from langchain_ollama import OllamaLLM
from langchain.prompts import PromptTemplate
from config import OLLAMA_MODEL, OLLAMA_BASE_URL


CLASSIFICATION_PROMPT = PromptTemplate(
    input_variables=["sender", "subject", "snippet"],
    template="""You are an email classifier. Decide if this email should be archived or kept.

ALWAYS KEEP:
- Newsletters or content about AI, machine learning, LLMs, product management, tech, or engineering
- Any email from Lenny's Newsletter, The Pragmatic Engineer, Tina Huang, Substack, or Medium
- Job alerts, recruiter messages, hiring opportunities, interview invites
- Delivery updates (order shipped, out for delivery, delivered)
- Personal messages from real people
- Direct replies to something the user sent
- Business emails requiring action or a response

ALWAYS ARCHIVE:
- Bank transaction alerts (HDFC, ICICI, SBI, Kotak, AU Small Finance)
- Stock market / exchange notifications (NSE, BSE, Zerodha)
- OTP or verification codes
- Crypto alerts (Binance, WazirX)
- Event registrations or promotional offers (Townscript, discount offers)
- Google policy reminders or terms update emails
- Generic automated marketing emails with no educational value

When in doubt, KEEP. Only archive if you are confident it is transactional or promotional with no learning value.

Email:
From: {sender}
Subject: {subject}
Preview: {snippet}

Respond with ONLY one word — either: archive  or  keep"""
)


def build_classifier():
    """
    Returns a classify(sender, subject, snippet) -> str function.
    Connects to locally running Ollama. Make sure `ollama serve` is running.
    """
    llm = OllamaLLM(model=OLLAMA_MODEL, base_url=OLLAMA_BASE_URL)
    chain = CLASSIFICATION_PROMPT | llm

    def classify(sender: str, subject: str, snippet: str) -> str:
        result = chain.invoke({"sender": sender, "subject": subject, "snippet": snippet})
        decision = result.strip().lower()
        # Guard against verbose responses — just check if 'archive' appears
        return "archive" if "archive" in decision else "keep"

    return classify
