"""검색한 논문을 근거로 한국어 답변과 출처를 만든다.

흐름: 질문 -> 검색(상위 k) -> [점수 게이트] -> 프롬프트(context 번호 [1]..[k]) -> LLM -> 인용 번호 검증

환각 방지를 두 겹으로 한다.
  1) 검색 1위 점수가 MIN_RETRIEVAL_SCORE 미만이면 LLM을 부르지 않고 "근거 없음"으로 답한다.
  2) 프롬프트로 "초록에 없으면 모른다고 답하라"고 지시하고, 답변의 인용 번호가 실제 있는 논문인지 검사한다.
"""

import re
from typing import Callable

from langchain_core.output_parsers import StrOutputParser

from src.const.config import ANSWER_TOP_K, MIN_RETRIEVAL_SCORE
from src.rag.llm import get_llm
from src.rag.prompt import ANSWER_PROMPT, NOT_FOUND
from src.rag.retriever import search


def format_context(papers: list[dict]) -> str:
    """검색 결과를 [1] 제목 (연도) + 초록 형태로 번호를 붙여 이어 붙인다."""
    return "\n\n".join(f"[{i}] {p['title']} ({p['year']})\n{p['summary']}" for i, p in enumerate(papers, start=1))


def extract_citations(answer: str, n_papers: int) -> tuple[list[int], list[int]]:
    """답변에서 [1], [2, 3] 형태의 인용 번호를 뽑아 (유효한 번호, 존재하지 않는 번호)로 나눈다."""
    numbers = {int(n) for group in re.findall(r"\[(\d+(?:\s*,\s*\d+)*)\]", answer) for n in re.split(r"\s*,\s*", group)}
    valid = sorted(n for n in numbers if 1 <= n <= n_papers)
    invalid = sorted(n for n in numbers if n < 1 or n > n_papers)
    return valid, invalid


def answer(
    question: str,
    *,
    k: int = ANSWER_TOP_K,
    min_score: float = MIN_RETRIEVAL_SCORE,
    search_fn: Callable[[str, int], list[dict]] = search,
    llm=None,
) -> dict:
    papers = search_fn(question, k)
    top_score = papers[0]["score"] if papers else 0.0

    if not papers or top_score < min_score:
        return {"answer": NOT_FOUND, "sources": [], "retrieved": papers, "top_score": top_score,
                "used_llm": False, "invalid_citations": [], "uncited": False}

    chain = ANSWER_PROMPT | (llm or get_llm()) | StrOutputParser()
    text = chain.invoke({"context": format_context(papers), "question": question}).strip()

    valid, invalid = extract_citations(text, len(papers))
    not_found = text.startswith(NOT_FOUND)
    return {
        "answer": text,
        "sources": [papers[n - 1] for n in valid],      # 답변이 실제로 인용한 논문만 출처로 보여준다
        "retrieved": papers,
        "top_score": top_score,
        "used_llm": True,
        "invalid_citations": invalid,                   # 없는 번호를 인용했다면 환각 신호
        "uncited": not valid and not not_found,         # 근거를 말하면서 인용이 하나도 없으면 신뢰하기 어려움
    }
