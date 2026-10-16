from pathlib import Path

RAW_DIR = Path("data/raw")
PROCESSED_PATH = Path("data/processed/papers.jsonl")
REMOVED_PATH = Path("data/processed/removed.jsonl")
INDEX_DIR = Path("data/index")
FAISS_PATH = INDEX_DIR / "papers.faiss"
DOCS_PATH = INDEX_DIR / "papers_meta.jsonl"

EMBEDDING_MODEL = "nvidia/nemotron-3-embed-1b"
EMBED_BATCH_SIZE = 32

# 답변 생성
# LLM 제공자: "gemini" | "nvidia" | "ollama". 환경변수 LLM_PROVIDER, CHAT_MODEL 로 바꿀 수 있다.
# 무료 서비스는 모델이 예고 없이 종료(EOL)되므로 제공자를 쉽게 갈아탈 수 있게 해 둔다 (2026-10-16 실제 호출로 확인).
LLM_PROVIDER = "gemini"
DEFAULT_CHAT_MODELS = {
    "gemini": "gemini-3.1-flash-lite",             # Google AI Studio 무료 등급(한도는 AI Studio에서 확인). 3.5-flash와 품질이 비슷하고 약 4배 빠름
    "nvidia": "nvidia/nemotron-3-super-120b-a12b",  # NVIDIA 무료 API, 당시 응답한 유일한 채팅 모델, 추론 모델이라 느림
    "ollama": "gemma3:4b",                         # 로컬(CPU) 비상용. 느리고 규칙 준수가 불안정
}
CHAT_MAX_TOKENS = 2048   # 추론(thinking) 모델은 생각에도 토큰을 쓰므로 넉넉히 둔다
ANSWER_TOP_K = 5         # 답변 근거로 LLM에 넘길 논문 수
# 검색 1위 점수(코사인 유사도)가 이 값보다 낮으면 LLM을 부르지 않고 "근거 없음"으로 답한다.
# 평가 질문 기준 범위 밖 질문은 약 0.21, 답 있는 질문은 0.39 이상이었다 (잠정값, 어려운 질문으로 재점검 필요)
MIN_RETRIEVAL_SCORE = 0.30
