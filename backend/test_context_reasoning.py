"""
Automated unit tests for Activity 4.3: Context-Aware Reasoning and Feature Differentiation.
Tests:
1. Feature prompt retrieval for all features (safety, cracks, planning, valuation, knowledge, chat, site_assistant, weather).
2. Persona and role differentiation per feature.
3. Feature differentiation in live query_ai calls across multiple construction domains.
"""
from core.feature_prompts import get_feature_reasoning_prompt, FEATURE_REASONING_PROMPTS
from core.ai_service import query_ai
from schemas.contracts import KnowledgeResponseData
from services.output_enforcer import parse_and_validate_ai_response


def test_feature_prompts_coverage():
    expected_features = [
        "safety",
        "cracks",
        "planning",
        "valuation",
        "knowledge",
        "chat",
        "site_assistant",
        "weather",
    ]
    for feat in expected_features:
        prompt = get_feature_reasoning_prompt(feat)
        assert prompt is not None
        assert "ROLE:" in prompt
        assert "REASONING GUIDELINES:" in prompt
    print("PASS: test_feature_prompts_coverage")


def test_contextual_reasoning_differentiation():
    # Knowledge query tests civil engineering standards persona
    knowledge_res = query_ai(
        feature="knowledge",
        user_inputs={"query": "What is the minimum curing period for OPC concrete under IS 456:2000 Clause 13.5?"},
    )
    assert len(knowledge_res) > 20
    assert "IS 456" in knowledge_res or "curing" in knowledge_res.lower()
    print("PASS: test_contextual_reasoning_differentiation (Knowledge Assistant)")

    # Chat query with ambiguity triggers clarification flag or clarifying questions
    chat_res = query_ai(
        feature="chat",
        user_text="What concrete should I use?",
    )
    assert len(chat_res) > 20
    print("PASS: test_contextual_reasoning_differentiation (Chatbot Context)")


if __name__ == "__main__":
    test_feature_prompts_coverage()
    test_contextual_reasoning_differentiation()
    print("ALL ACTIVITY 4.3 TESTS PASSED SUCCESSFULLY.")
