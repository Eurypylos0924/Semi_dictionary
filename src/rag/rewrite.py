"""질문을 논문 초록 말투의 영어 검색문으로 바꿔서 검색한다 (Query Rewriting).

배경: 현업 표현 질문("열처리했더니 누설이 늘었어")은 논문 말투("leakage current ... annealing ...")와 어휘가 달라
검색 점수가 낮게 나온다. 질문을 논문이 쓰는 기술 용어의 영어 검색문으로 바꿔서 이 차이를 줄인다.

검색 방식(mode):
  original : 원문 질문만 검색 (기준선, 기존 동작)
  rewrite  : 재작성한 검색문만 검색
  max      : 원문과 재작성문을 모두 검색하고 문서별 최고 점수로 합침 (재작성이 엉뚱할 때를 대비)

환경변수 QUERY_MODE 로 바꿀 수 있다. 재작성 결과는 data/cache/rewrites.jsonl 에 저장해 같은 질문은 LLM을 다시 부르지 않는다.
"""

import hashlib
import json
import os
from pathlib import Path
from typing import Callable

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from src.rag.llm import get_llm, resolve
from src.rag.retriever import search, search_queries

MODES = ("original", "rewrite", "max")
DEFAULT_MODE = "original"  # 측정 결과를 보고 바꾼다 (docs/rag.md 참고)
CACHE_PATH = Path("data/cache/rewrites.jsonl")

REWRITE_SYSTEM = """당신은 반도체·디스플레이 박막 공정(원자층 증착 ALD, HfO2 같은 고유전율 절연막, XRD 결정성 분석, CMP, 웨이퍼맵·수율 분석) 논문 초록을 검색하는 검색어 작성기입니다.
사용자의 질문을 논문 초록에서 쓰는 영어 기술 용어의 검색문으로 바꿉니다.

규칙:
1. 질문의 증상·상황을 논문이 쓰는 용어로 바꿉니다. 예: "누설이 늘었어" -> leakage current increase, "피크가 퍼졌어" -> XRD peak broadening
2. 약어는 풀어 쓰고 약어도 함께 씁니다. 예: ALD -> atomic layer deposition (ALD)
3. 질문에 없는 수치·조건·결론을 지어내서 넣지 않습니다.
4. 질문이 반도체 박막 공정과 무관해도 그 주제를 그대로 영어 검색문으로 옮깁니다. 코퍼스에 있을 법한 주제로 억지로 끼워 맞추지 않습니다.
5. 설명 없이 영어 검색문 한 줄만 출력합니다. 키워드 나열이어도 됩니다."""

REWRITE_PROMPT = ChatPromptTemplate.from_messages([("system", REWRITE_SYSTEM), ("human", "{question}")])


def clean_rewrite(text: str) -> str:
    """LLM 출력에서 첫 줄만 남기고 따옴표나 'Query:' 같은 접두어를 제거한다."""
    line = next((l.strip() for l in text.strip().splitlines() if l.strip()), "")
    for prefix in ("query:", "search query:", "검색문:"):
        if line.lower().startswith(prefix):
            line = line[len(prefix):].strip()
    return line.strip("\"'` ")


def cache_key(question: str, provider: str, model: str) -> str:
    return hashlib.sha1(f"{provider}|{model}|{REWRITE_SYSTEM}|{question}".encode("utf-8")).hexdigest()


def read_cache(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    with path.open(encoding="utf-8") as f:
        return {row["key"]: row["rewrite"] for row in map(json.loads, f)}


def write_cache(path: Path, key: str, question: str, rewrite: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps({"key": key, "question": question, "rewrite": rewrite}, ensure_ascii=False) + "\n")


def rewrite_query(question: str, *, llm=None, cache_path: Path | None = CACHE_PATH) -> str:
    provider, model = resolve()
    key = cache_key(question, provider, model)
    if cache_path is not None:
        cached = read_cache(cache_path).get(key)
        if cached:
            return cached
    chain = REWRITE_PROMPT | (llm or get_llm()) | StrOutputParser()
    rewritten = clean_rewrite(chain.invoke({"question": question}))
    if not rewritten:  # LLM이 빈 답을 주면 원문으로 검색한다
        return question
    if cache_path is not None:
        write_cache(cache_path, key, question, rewritten)
    return rewritten


def search_with_mode(
    question: str,
    k: int = 5,
    mode: str | None = None,
    rewriter: Callable[[str], str] = rewrite_query,
) -> list[dict]:
    mode = (mode or os.getenv("QUERY_MODE") or DEFAULT_MODE).lower()
    if mode not in MODES:
        raise ValueError(f"알 수 없는 검색 방식 '{mode}'. 선택지: {', '.join(MODES)}")
    if mode == "original":
        return search(question, k)
    rewritten = rewriter(question)
    return search_queries([rewritten] if mode == "rewrite" else [question, rewritten], k)
