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
# NVIDIA 무료 API. 모델 목록에 있어도 서비스 종료(EOL)된 모델이 많아 실제 호출로 확인했다(2026-10-16 기준 응답하는 채팅 모델은 이것뿐).
# 추론 모델이라 생각에 토큰을 쓰므로 max_tokens를 넉넉히 둔다. 환경변수 CHAT_MODEL 로 바꿀 수 있다.
CHAT_MODEL = "nvidia/nemotron-3-super-120b-a12b"
CHAT_MAX_TOKENS = 2048
ANSWER_TOP_K = 5                            # 답변 근거로 LLM에 넘길 논문 수
# 검색 1위 점수(코사인 유사도)가 이 값보다 낮으면 LLM을 부르지 않고 "근거 없음"으로 답한다.
# 평가 질문 기준 범위 밖 질문은 약 0.21, 답 있는 질문은 0.39 이상이었다 (잠정값, 어려운 질문으로 재점검 필요)
MIN_RETRIEVAL_SCORE = 0.30
