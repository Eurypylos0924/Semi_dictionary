"""검색한 논문을 근거로 한국어 답변과 출처를 만든다.

흐름: 질문 -> 검색(상위 k) -> [점수 게이트] -> 프롬프트(context 번호 [1]..[k]) -> LLM -> 인용 번호 검증

환각 방지를 두 겹으로 한다.
  1) 검색 1위 점수가 MIN_RETRIEVAL_SCORE 미만이면 LLM을 부르지 않고 "근거 없음"으로 답한다.
  2) 프롬프트로 "초록에 없으면 모른다고 답하라"고 지시하고, 답변의 인용 번호가 실제 있는 논문인지 검사한다.
"""

import re
from typing import Callable

from langchain_core.output_parsers import StrOutputParser

import os

from src.const.config import ANSWER_TOP_K, MIN_RETRIEVAL_SCORE
from src.rag.judge import DEFAULT_GATE_MODE, GATE_MODES, HARD_FLOOR, Judgement, judge
from src.rag.llm import get_llm
from src.rag.prompt import ANSWER_PROMPT, MATH_LOSS_WARNING, NOT_FOUND
from src.rag.rewrite import search_with_mode

PARTIAL_HINT = "\n\n[검토 메모]\n참고 논문으로는 질문의 일부만 답할 수 있다고 판정됐습니다. 논문에서 확인되는 부분만 답하고, 확인되지 않는 부분은 '논문에서 확인되지 않음'이라고 밝히세요."


def format_context(papers: list[dict]) -> str:
    """검색 결과를 [1] 제목 (연도) + 초록 형태로 번호를 붙여 이어 붙인다. 수식·수치가 빠진 초록(math_loss)에는 경고를 붙인다."""
    blocks = []
    for i, p in enumerate(papers, start=1):
        warning = f"\n{MATH_LOSS_WARNING}" if p.get("math_loss") else ""
        blocks.append(f"[{i}] {p['title']} ({p['year']}){warning}\n{p['summary']}")
    return "\n\n".join(blocks)


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
    search_fn: Callable[[str, int], list[dict]] = search_with_mode,
    llm=None,
    gate_mode: str | None = None,
    judge_fn: Callable[..., Judgement | None] = judge,
    use_judge_selection: bool = False,
) -> dict:
    """gate_mode: 'score'(검색 1위 점수가 min_score 미만이면 거절) | 'judge'(점수는 하한선, 그 위는 LLM이 근거 적합성 판정)."""
    gate_mode = (gate_mode or os.getenv("GATE_MODE") or DEFAULT_GATE_MODE).lower()
    if gate_mode not in GATE_MODES:
        raise ValueError(f"알 수 없는 게이트 방식 '{gate_mode}'. 선택지: {', '.join(GATE_MODES)}")

    papers = search_fn(question, k)
    top_score = papers[0]["score"] if papers else 0.0
    base = {"retrieved": papers, "top_score": top_score, "gate_mode": gate_mode, "verdict": None, "judge_reason": ""}

    def refuse(reason: str = "", **extra) -> dict:
        text = f"{NOT_FOUND} {reason}".strip()
        return {**base, "answer": text, "sources": [], "used_llm": False, "invalid_citations": [], "uncited": False, **extra}

    context_papers, hint = papers, ""
    if gate_mode == "score":
        if not papers or top_score < min_score:
            return refuse()
    else:
        if not papers or top_score < HARD_FLOOR:
            return refuse()
        judgement = judge_fn(question, papers, llm=llm)
        if judgement is None:  # 판정 형식 오류 -> 점수 게이트로 대체
            if top_score < min_score:
                return refuse(verdict="judge_failed")
        else:
            base["verdict"], base["judge_reason"] = judgement.verdict, judgement.reason
            if judgement.verdict == "none":
                return refuse(judgement.reason)
            if use_judge_selection:  # 판정이 고른 논문만 근거로 쓴다 (기본은 끔: 측정에서 정답 논문의 약 절반을 버림)
                context_papers = [papers[n - 1] for n in judgement.relevant]
            hint = PARTIAL_HINT if judgement.verdict == "partial" else ""

    chain = ANSWER_PROMPT | (llm or get_llm()) | StrOutputParser()
    text = chain.invoke({"context": format_context(context_papers), "question": question, "hint": hint}).strip()

    valid, invalid = extract_citations(text, len(context_papers))
    not_found = text.startswith(NOT_FOUND)
    return {
        **base,
        "answer": text,
        "sources": [context_papers[n - 1] for n in valid],  # 답변이 실제로 인용한 논문만 출처로 보여준다
        "used_llm": True,
        "invalid_citations": invalid,                       # 없는 번호를 인용했다면 환각 신호
        "uncited": not valid and not not_found,             # 근거를 말하면서 인용이 하나도 없으면 신뢰하기 어려움
    }
