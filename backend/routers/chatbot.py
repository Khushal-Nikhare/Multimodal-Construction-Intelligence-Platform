"""
FR-06: Construction Chatbot Router
Endpoints:
  - POST /api/chat     (Contract 3.6 format with session_id, message, history)
  - POST /api/chatbot  (Activity 5.1 direct endpoint returning reply and action_suggestions)
"""
import logging
import time
import uuid
from typing import Optional, List, Dict, Any, Literal, Tuple

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from schemas.response import UniversalError, UniversalMeta, UniversalResponse
from schemas.contracts import ChatResponseData
from core.ai_service import query_ai
from services.output_enforcer import parse_and_validate_ai_response

logger = logging.getLogger(__name__)

router = APIRouter(tags=["FR-06: Construction Chatbot"])


# ── Request Models ────────────────────────────────────────────────────────────

class ChatMessage(BaseModel):
    role: Literal["user", "assistant"] = Field(..., description="Conversation speaker")
    content: str = Field(..., min_length=1, max_length=4_000, description="Message text content")


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=4_000, description="User question or statement")
    session_id: Optional[str] = Field(None, max_length=80, description="Persistent conversational session identifier")
    history: List[ChatMessage] = Field(default_factory=list, max_length=8, description="Recent conversation turns")


# ── Chatbot Execution Core ────────────────────────────────────────────────────

CHATBOT_SYSTEM_PROMPT = """You are the AI Construction Intelligence Chatbot — an expert on-site civil engineer, project coordinator, and building code advisor.

CORE BEHAVIORS:
1. Provide accurate, practical civil engineering advice (IS 456, IS 800, CPWD, OSHA).
2. MULTI-TURN CONTEXT: Seamlessly incorporate previous discussion into your answer.
3. AMBIGUITY DETECTION (Scenario 6.2): If the user's message is single-word or highly ambiguous (e.g. 'Concrete', 'Slab', 'Steel'), detect this immediately:
   - Set requires_clarification: true
   - In 'reply', ask a helpful clarifying question detailing possible sub-topics (e.g. mix design, curing duration, slump testing, compressive strength).
   - In 'action_suggestions', suggest focused sub-topics.
4. SAFETY GUARDRAILS: Strictly refuse unsafe demolition, unauthorized load-bearing modifications, or safety shortcuts.
5. ACTION SUGGESTIONS: Always generate 2-3 logical, actionable next steps or follow-up topics for the user.

OUTPUT FORMAT: Strict RFC-8259 JSON matching this exact structure:
{
  "session_id": "<session_id>",
  "reply": "<detailed markdown-formatted civil engineering response or clarifying question>",
  "requires_clarification": false,
  "action_suggestions": ["Action 1", "Action 2"],
  "suggested_followups": ["Followup Question 1?", "Followup Question 2?"]
}
"""


def _process_chat_query(payload: ChatRequest) -> Tuple[Dict[str, Any], bool]:
    # Validate non-empty / non-whitespace
    cleaned_msg = payload.message.strip()
    if not cleaned_msg:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "status": "error",
                "error": {
                    "code": "EMPTY_QUERY",
                    "message": "Message text cannot be empty or whitespace.",
                }
            }
        )

    session_id = payload.session_id or f"sess-{uuid.uuid4().hex[:8]}"

    # Check for single-word / brief ambiguous input (Scenario 6.2)
    words = cleaned_msg.split()
    is_single_word = len(words) == 1 and len(cleaned_msg) < 15

    # Assemble conversation context
    history_lines = []
    for h in (payload.history or []):
        history_lines.append(f"{h.role.upper()}: {h.content}")
    history_context = "\n".join(history_lines) if history_lines else "None (New Conversation)"

    user_prompt = f"""Session ID: {session_id}
Conversation History:
{history_context}

CURRENT USER MESSAGE:
"{cleaned_msg}"

{"NOTE: This query is brief or single-word. If ambiguous, set requires_clarification: true and provide sub-topic choices." if is_single_word else ""}
"""

    try:
        raw_response = query_ai(
            feature="chat",
            system_prompt=CHATBOT_SYSTEM_PROMPT,
            user_text=user_prompt,
            max_tokens=1500,
            temperature=0.3,
        )
    except Exception as exc:
        logger.exception("AI service error in chatbot request: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail={
                "status": "error",
                "error": {
                    "code": "AI_SERVICE_ERROR",
                    "message": "The construction assistant is temporarily unavailable. Please retry.",
                },
            },
        ) from exc

    safe_fallback = {
        "session_id": session_id,
        "reply": raw_response if raw_response.strip() else "I received your construction query. How can I assist further?",
        "requires_clarification": False,
        "suggested_followups": [
            "What IS codes apply to this situation?",
            "What are the standard safety precautions?",
        ],
    }

    validated, used_fallback = parse_and_validate_ai_response(
        raw_response=raw_response,
        schema_cls=ChatResponseData,
        fallback_data=safe_fallback,
    )
    data = validated.model_dump()
    # Keep either field useful for clients during a model omission, without
    # accepting unvalidated model output.
    if not data["action_suggestions"]:
        data["action_suggestions"] = data["suggested_followups"]
    if not data["suggested_followups"]:
        data["suggested_followups"] = data["action_suggestions"]
    return data, used_fallback


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.post("/api/chat", response_model=UniversalResponse)
async def chat_contract_endpoint(payload: ChatRequest):
    """
    Standard Data Contract 3.6 Endpoint.
    """
    t0 = time.time()
    req_id = f"req-chat-{uuid.uuid4().hex[:8]}"

    data, used_fallback = _process_chat_query(payload)
    latency = round((time.time() - t0) * 1000, 2)

    return UniversalResponse(
        status="partial" if used_fallback else "success",
        data=data,
        meta=UniversalMeta(request_id=req_id, latency_ms=latency, model_provider="groq")
    )


@router.post("/api/chatbot")
async def direct_chatbot_endpoint(payload: ChatRequest):
    """
    Activity 5.1 direct endpoint returning { reply, action_suggestions, session_id }
    compatible with `res.data.reply` and `res.data.action_suggestions`.
    """
    data, used_fallback = _process_chat_query(payload)
    return {
        "status": "partial" if used_fallback else "success",
        "reply": data["reply"],
        "action_suggestions": data.get("action_suggestions", []),
        "requires_clarification": data.get("requires_clarification", False),
        "session_id": data["session_id"],
        "data": data, # Also include nested data for Universal format compatibility
    }
