"""
Parser and normalizer utility for enforcing AI structured outputs and data contracts.
Handles markdown cleanup, JSON decoding, schema validation, and defensive fallback defaults.
"""
import json
import logging
from typing import Type, TypeVar, Optional, Dict, Any, Tuple
from pydantic import BaseModel, ValidationError

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)


def clean_markdown_fences(text: str) -> str:
    """
    Remove ```json ... ``` code blocks or leading/trailing whitespace,
    and extract the outermost JSON object/array if extraneous text surrounds it.
    """
    s = text.strip()
    if s.startswith("```"):
        lines = s.splitlines()
        if lines[0].strip().startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip().startswith("```"):
            lines = lines[:-1]
        s = "\n".join(lines).strip()

    # If extraneous prose precedes or follows the JSON object, extract the JSON portion
    first_brace = s.find("{")
    last_brace = s.rfind("}")
    if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
        s = s[first_brace : last_brace + 1]

    return s


def parse_and_validate_ai_response(
    raw_response: str,
    schema_cls: Type[T],
    fallback_data: Optional[Dict[str, Any]] = None,
) -> Tuple[T, bool]:
    """
    Parse an AI string output as JSON, validate against a Pydantic schema class,
    and return (validated_model, is_fallback_used).

    If parsing or validation fails, logs the error and gracefully applies
    the provided fallback_data (if available).

    Parameters
    ----------
    raw_response : str
        Raw string returned by query_ai().
    schema_cls : Type[T]
        Pydantic model class to validate against.
    fallback_data : dict, optional
        Safe semantic default dictionary if model response is malformed.

    Returns
    -------
    Tuple[T, bool]
        (instance_of_schema_cls, was_fallback_applied)
    """
    cleaned = clean_markdown_fences(raw_response)

    try:
        parsed_dict = json.loads(cleaned)
        validated = schema_cls.model_validate(parsed_dict)
        return validated, False
    except (json.JSONDecodeError, ValidationError) as err:
        logger.warning(
            "AI response schema validation failed for %s: %s. Raw preview: %.200s",
            schema_cls.__name__,
            err,
            raw_response,
        )

        if fallback_data is not None:
            try:
                # Merge any partial data extracted if possible
                fallback_model = schema_cls.model_validate(fallback_data)
                return fallback_model, True
            except ValidationError as fallback_err:
                logger.error("Fallback dictionary itself failed validation: %s", fallback_err)
                raise fallback_err

        # If no fallback is provided, raise
        raise err
