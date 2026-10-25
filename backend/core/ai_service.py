"""
Shared Multimodal AI Integration Service for the Construction Intelligence Platform.
Provides centralized, asynchronous, feature-aware LLM & Vision model calling
with automatic image encoding, construction-domain prompting, token limits,
and structured schema sanitization.
"""
import base64
import json
import logging
from typing import Optional, Dict, Any, Union, List

from groq import Groq
from core.config import settings

logger = logging.getLogger(__name__)

# Lazily instantiated Groq client
_client: Optional[Groq] = None


def get_client() -> Groq:
    """Lazily initialize and return the Groq client instance."""
    global _client
    if _client is None:
        _client = Groq(api_key=settings.GROQ_API_KEY)
    return _client


# ── Shared Construction Domain System Prompt ──────────────────────────────────
BASE_CONSTRUCTION_SYSTEM_PROMPT = """You are the AI core for the Multimodal Construction Intelligence Platform.
You are an expert civil, structural, and construction engineering intelligence engine with deep expertise in:
- Indian and International Building Standards (IS 456 for Concrete, IS 800 for Steel, CPWD Specifications, NBC, ASTM, IBC).
- On-site hazard detection, PPE compliance, OSHA / Indian standard site safety.
- Structural crack diagnostics, masonry/concrete forensics, and non-destructive testing (NDT).
- Quantity takeoff (MTO), parametric budgeting, and CPM/PERT construction scheduling.
- Real estate market evaluation and micro-market parametric estimation in India.

CRITICAL INSTRUCTIONS:
1. Provide accurate, professional, context-rich engineering assessments.
2. When structured JSON is requested, output ONLY valid RFC-8259 JSON without any markdown formatting, backticks, or text before/after.
3. Explicitly state assumptions and incorporate safety disclaimers when appropriate.
"""


def encode_image_to_base64(image_bytes: bytes) -> str:
    """
    Utility to encode raw image bytes into a base64 UTF-8 string.
    """
    return base64.b64encode(image_bytes).decode("utf-8")


def clean_json_response(raw_text: str) -> str:
    """
    Strip potential markdown code blocks (```json ... ```) or whitespace
    surrounding AI responses to ensure reliable JSON parsing.
    """
    text = raw_text.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        text = "\n".join(lines).strip()
    return text


def query_ai(
    feature: str = "general",
    user_inputs: Optional[Union[Dict[str, Any], str]] = None,
    image_bytes: Optional[bytes] = None,
    image_media_type: str = "image/jpeg",
    system_prompt: Optional[str] = None,
    user_text: Optional[str] = None,
    use_vision: bool = False,
    max_tokens: Optional[int] = None,
    temperature: float = 0.3,
) -> str:
    """
    Centralized multimodal AI request handler.
    Can be called synchronously or awaited (returns str directly, compatible with async def routes).

    Parameters
    ----------
    feature : str
        Platform feature identifier (e.g. 'safety', 'cracks', 'planning', 'valuation', 'knowledge', 'chat').
    user_inputs : dict or str, optional
        Structured user inputs or context for the feature.
    image_bytes : bytes, optional
        Raw uploaded image bytes for vision analysis.
    image_media_type : str
        MIME type of the image ('image/jpeg', 'image/png', 'image/webp').
    system_prompt : str, optional
        Feature-specific system instructions. If omitted, uses the baseline construction prompt.
    user_text : str, optional
        Direct text prompt. If omitted, user_inputs is formatted automatically.
    use_vision : bool
        Force vision model selection even if image_bytes is absent.
    max_tokens : int, optional
        Token limit. Defaults to settings.GROQ_MAX_TOKENS.
    temperature : float
        Sampling temperature (default 0.3 for structured consistency).

    Returns
    -------
    str
        Raw text completion from the model.
    """
    client = get_client()

    # Determine Model Selection
    is_multimodal = bool(image_bytes) or use_vision
    model = settings.GROQ_VISION_MODEL if is_multimodal else settings.GROQ_LLM_MODEL

    # Determine token constraints
    token_limit = max_tokens or settings.GROQ_MAX_TOKENS
    if "prompt-guard" in model:
        token_limit = min(token_limit, 512)

    # Construct the final system prompt with feature-specific contextualization (Activity 4.3)
    from core.feature_prompts import get_feature_reasoning_prompt

    if system_prompt:
        effective_system = system_prompt
    elif feature and feature != "general":
        effective_system = f"{BASE_CONSTRUCTION_SYSTEM_PROMPT}\n\n{get_feature_reasoning_prompt(feature)}"
    else:
        effective_system = BASE_CONSTRUCTION_SYSTEM_PROMPT

    # Construct the user text representation with feature header
    if user_text:
        prompt_body = user_text
    elif isinstance(user_inputs, dict):
        formatted_inputs = [f"{k}: {v}" for k, v in user_inputs.items()]
        prompt_body = f"[{feature.upper()} REQUEST]:\n" + "\n".join(formatted_inputs)
    elif user_inputs:
        prompt_body = str(user_inputs)
    else:
        prompt_body = f"Please perform {feature} analysis based on provided context."

    # Multimodal Message Preparation
    if image_bytes:
        b64_image = encode_image_to_base64(image_bytes)
        user_message_content = [
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:{image_media_type};base64,{b64_image}"
                },
            },
            {"type": "text", "text": prompt_body},
        ]
    else:
        user_message_content = prompt_body

    messages = [
        {"role": "system", "content": effective_system},
        {"role": "user", "content": user_message_content},
    ]

    logger.info("Centralized AI invocation: feature=%s, model=%s, multimodal=%s", feature, model, is_multimodal)

    # Model invocation
    completion = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=token_limit,
    )

    response_content = completion.choices[0].message.content
    return response_content
