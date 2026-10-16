import pytest

from src.const.config import DEFAULT_CHAT_MODELS, LLM_PROVIDER
from src.rag.llm import resolve


@pytest.fixture(autouse=True)
def clean_env(monkeypatch):
    monkeypatch.delenv("LLM_PROVIDER", raising=False)
    monkeypatch.delenv("CHAT_MODEL", raising=False)


def test_defaults_to_configured_provider_and_its_default_model():
    assert resolve() == (LLM_PROVIDER, DEFAULT_CHAT_MODELS[LLM_PROVIDER])


def test_environment_variables_override_defaults(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "Ollama")  # 대소문자 무관
    monkeypatch.setenv("CHAT_MODEL", "qwen2.5:7b")
    assert resolve() == ("ollama", "qwen2.5:7b")


def test_arguments_override_environment(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "nvidia")
    assert resolve("gemini", "gemini-x") == ("gemini", "gemini-x")


def test_each_provider_falls_back_to_its_own_default_model():
    for provider, model in DEFAULT_CHAT_MODELS.items():
        assert resolve(provider) == (provider, model)


def test_unknown_provider_raises_with_choices():
    with pytest.raises(ValueError, match="gemini"):
        resolve("openai")
