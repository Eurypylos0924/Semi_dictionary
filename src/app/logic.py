"""화면이 쓰는 로직. streamlit을 쓰지 않는 순수 함수라 pytest로 직접 검증한다.

답변 파이프라인(src/rag)은 호출만 하고 고치지 않는다. 여기서는 (1) 화면 설정을 파이프라인 인자로 바꾸고
(2) 파이프라인 결과를 "무엇을 보여줄지"(상태 배지, 경고, 번호 붙은 출처)로 가공한다.
"""

from src.const.config import ANSWER_TOP_K
from src.rag.generator import answer
from src.rag.prompt import NOT_FOUND
from src.rag.rewrite import search_with_mode

QUERY_MODES = ("max", "original")
GATE_MODES = ("judge", "score")

# 처음 보는 사람이 어떤 질문이 되고 안 되는지 알 수 있도록 되는 질문 3개와 거절되는 질문 1개를 섞는다 (평가 질문과 겹치지 않게 새로 썼고, 실제로 돌려 보고 골랐다.
# 처음에 넣은 배터리 양극 소재 질문은 코퍼스에 XRD 결정립 분석 논문이 있어 범위 안이었다)
EXAMPLES = (
    "CMP를 하고 나면 웨이퍼에 긁힌 자국이 생겨. 어떻게 줄여?",
    "HfO2 박막을 어닐링하면 결정화되면서 누설전류가 늘어나?",
    "XRD 피크가 넓어졌는데 결정립이 작아진 건지 변형 때문인지 어떻게 구분해?",
    "웨이퍼 불량 패턴을 딥러닝으로 분류할 때 GPU는 어떤 사양이 필요해?",  # 주제(웨이퍼 불량 분류)는 논문에 있지만 GPU 사양은 없다: 검색 점수는 0.5로 높아도 근거 판정이 거절한다
)

# 근거 판정(verdict)과 점수 게이트 결과를 사용자가 읽는 말로 바꾼다 (label, Streamlit 색)
VERDICT_BADGES = {
    "answerable": ("근거 충분", "green"),
    "partial": ("일부만 근거 있음", "orange"),
    "none": ("근거 없음", "red"),
    "judge_failed": ("판정 실패, 점수로 판단", "gray"),
}


def run_question(question: str, *, query_mode: str, gate_mode: str, k: int = ANSWER_TOP_K, llm=None) -> dict:
    """질문 하나를 파이프라인에 넣는다. query_mode/gate_mode는 화면에서 고른 값이다."""
    if query_mode not in QUERY_MODES:
        raise ValueError(f"검색 방식은 {', '.join(QUERY_MODES)} 중 하나여야 한다: {query_mode}")
    if gate_mode not in GATE_MODES:
        raise ValueError(f"게이트 방식은 {', '.join(GATE_MODES)} 중 하나여야 한다: {gate_mode}")
    return answer(
        question,
        k=k,
        llm=llm,
        search_fn=lambda q, n: search_with_mode(q, n, mode=query_mode),
        gate_mode=gate_mode,
    )


def is_refusal(result: dict) -> bool:
    """근거를 찾지 못해 거절한 답변인가 (게이트가 막았거나 LLM이 스스로 거절)."""
    return result["answer"].startswith(NOT_FOUND)


def status_badge(result: dict) -> tuple[str, str]:
    """답변 위에 붙일 상태 배지 (label, 색)."""
    if is_refusal(result):
        return "근거를 찾지 못함", "red"
    verdict = result.get("verdict")
    if verdict in VERDICT_BADGES:
        return VERDICT_BADGES[verdict]
    return "점수 게이트 통과", "blue"  # 게이트가 score일 때는 판정이 없다


def warnings_for(result: dict) -> list[str]:
    """답변을 그대로 믿으면 안 되는 신호. 비어 있으면 표시할 경고가 없다."""
    notes = []
    if result.get("invalid_citations"):
        nums = ", ".join(f"[{n}]" for n in result["invalid_citations"])
        notes.append(f"존재하지 않는 논문 번호를 인용했습니다 ({nums}). 이 답변은 믿기 어렵습니다.")
    if result.get("uncited"):
        notes.append("답변에 인용 번호가 없습니다. 근거를 직접 확인하세요.")
    return notes


def numbered_papers(result: dict) -> list[dict]:
    """검색된 논문에 답변 속 [n]과 같은 번호를 붙인다(번호 = 검색 순위). 답변이 인용했는지(cited)와 초록 일부도 담는다."""
    cited = {p["doc_id"] for p in result.get("sources", [])}
    rows = []
    for number, paper in enumerate(result["retrieved"], start=1):
        summary = paper["summary"]
        rows.append(
            {
                "number": number,
                "title": paper["title"],
                "year": paper["year"],
                "url": paper.get("source_url"),
                "score": paper["score"],
                "cited": paper["doc_id"] in cited,
                "math_loss": bool(paper.get("math_loss")),
                "abstract": summary if len(summary) <= 500 else summary[:500].rstrip() + "…",
            }
        )
    return rows


def safe_md(text: str) -> str:
    """논문 제목·초록·LLM 답변을 st.markdown에 넣을 때 '$' 한 쌍이 수식으로 렌더링되어 글이 깨지는 것을 막는다."""
    return text.replace("$", r"\$")


def reason_to_show(result: dict) -> str:
    """근거 판정 이유. 거절 답변은 이미 본문에 같은 이유를 담고 있으므로 중복해서 보여주지 않는다."""
    reason = result.get("judge_reason") or ""
    return "" if reason in result["answer"] else reason
