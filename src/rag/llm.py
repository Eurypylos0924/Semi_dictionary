"""답변 생성에 쓸 LLM을 제공자(gemini / nvidia / ollama)별로 만든다.

무료 서비스는 모델이 갑자기 종료되므로 코드 수정 없이 환경변수로 갈아탈 수 있게 한다.
  LLM_PROVIDER=gemini|nvidia|ollama   CHAT_MODEL=모델 이름(생략하면 제공자 기본 모델)
"""

import os

from dotenv import load_dotenv

from src.const.config import CHAT_MAX_TOKENS, DEFAULT_CHAT_MODELS, LLM_PROVIDER


def resolve(provider: str | None = None, model: str | None = None) -> tuple[str, str]:
    """인자 > 환경변수 > 기본값 순서로 (제공자, 모델 이름)을 정한다."""
    provider = (provider or os.getenv("LLM_PROVIDER") or LLM_PROVIDER).lower()
    if provider not in DEFAULT_CHAT_MODELS:
        raise ValueError(f"알 수 없는 LLM 제공자 '{provider}'. 선택지: {', '.join(DEFAULT_CHAT_MODELS)}")
    return provider, model or os.getenv("CHAT_MODEL") or DEFAULT_CHAT_MODELS[provider]


def get_llm(provider: str | None = None, model: str | None = None):
    load_dotenv(".env")
    provider, model = resolve(provider, model)

    if provider == "gemini":
        from langchain_google_genai import ChatGoogleGenerativeAI

        return ChatGoogleGenerativeAI(
            model=model, google_api_key=os.getenv("GOOGLE_API_KEY"), temperature=0, max_output_tokens=CHAT_MAX_TOKENS
        )
    if provider == "nvidia":
        from langchain_nvidia_ai_endpoints import ChatNVIDIA

        return ChatNVIDIA(model=model, api_key=os.getenv("nvidiaapi_key"), temperature=0, max_tokens=CHAT_MAX_TOKENS)

    from langchain_ollama import ChatOllama  # ollama: 로컬 서버, 키 불필요

    # num_ctx: 기본값(2048)은 초록 5편을 넣으면 잘리므로 늘린다
    return ChatOllama(model=model, temperature=0, num_ctx=8192, num_predict=CHAT_MAX_TOKENS)
