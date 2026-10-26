from langchain_core.language_models.fake_chat_models import FakeListChatModel

from src.rag.generator import answer, extract_citations, format_context
from src.rag.prompt import MATH_LOSS_WARNING, SYSTEM_PROMPT
from src.rag.prompt import NOT_FOUND


def paper(i: int, score: float = 0.6) -> dict:
    return {"title": f"Paper {i}", "year": 2000 + i, "summary": f"abstract {i}", "score": score, "source_url": f"https://x/{i}"}


def fake_search(papers):
    return lambda question, k: papers[:k]


class ExplodingLLM:
    def __call__(self, *args, **kwargs):
        raise AssertionError("LLM이 호출되면 안 된다")

    invoke = __call__

    def __or__(self, other):
        raise AssertionError("LLM이 호출되면 안 된다")

    def __ror__(self, other):
        raise AssertionError("LLM이 호출되면 안 된다")


def test_format_context_numbers_papers_from_one():
    text = format_context([paper(1), paper(2)])
    assert text.startswith("[1] Paper 1 (2001)\nabstract 1")
    assert "\n\n[2] Paper 2 (2002)" in text


def test_format_context_warns_only_for_math_loss_papers():
    flagged = {**paper(2), "math_loss": ["값 누락(전치사·비교어 뒤가 비어 있음)"]}
    text = format_context([paper(1), flagged])
    first, second = text.split("\n\n")
    assert MATH_LOSS_WARNING not in first
    assert second.startswith(f"[2] Paper 2 (2002)\n{MATH_LOSS_WARNING}\nabstract 2")


def test_empty_math_loss_list_is_not_a_warning():
    assert MATH_LOSS_WARNING not in format_context([{**paper(1), "math_loss": []}])


def test_system_prompt_tells_model_not_to_invent_values_for_flagged_papers():
    assert MATH_LOSS_WARNING in SYSTEM_PROMPT and "초록에서 수치가 누락되어 확인할 수 없음" in SYSTEM_PROMPT


def test_extract_citations_splits_valid_and_invalid_numbers():
    valid, invalid = extract_citations("A이다[1]. B이다 [2, 3]. C이다[9].", n_papers=3)
    assert valid == [1, 2, 3]
    assert invalid == [9]


def test_extract_citations_ignores_non_citation_brackets():
    assert extract_citations("배열 [a] 와 [] 는 인용이 아님", n_papers=3) == ([], [])


def test_low_retrieval_score_skips_llm_and_says_not_found():
    result = answer("질문", search_fn=fake_search([paper(1, score=0.1)]), llm=ExplodingLLM())
    assert result["answer"] == NOT_FOUND
    assert result["used_llm"] is False and result["sources"] == []


def test_only_cited_papers_become_sources_and_invalid_citation_is_flagged():
    llm = FakeListChatModel(responses=["첫째 주장이다[2]. 둘째 주장이다[9]."])
    result = answer("질문", search_fn=fake_search([paper(1), paper(2), paper(3)]), llm=llm)
    assert [p["title"] for p in result["sources"]] == ["Paper 2"]
    assert result["invalid_citations"] == [9]
    assert result["uncited"] is False


def test_answer_without_any_citation_is_flagged_as_uncited():
    llm = FakeListChatModel(responses=["출처 없이 말하는 답변"])
    result = answer("질문", search_fn=fake_search([paper(1)]), llm=llm)
    assert result["uncited"] is True and result["sources"] == []


def test_llm_not_found_answer_is_not_flagged_as_uncited():
    llm = FakeListChatModel(responses=[f"{NOT_FOUND} 관련 내용이 초록에 없습니다."])
    result = answer("질문", search_fn=fake_search([paper(1)]), llm=llm)
    assert result["used_llm"] is True and result["uncited"] is False


def test_every_rag_module_compiles():
    # ask.py의 f-string 줄바꿈 버그가 테스트 없이 병합된 적이 있어서, CLI 파일까지 문법만이라도 확인한다
    import py_compile
    from pathlib import Path

    for path in Path(__file__).resolve().parents[1].joinpath("src", "rag").glob("*.py"):
        py_compile.compile(str(path), doraise=True)


def test_defaults_are_max_search_with_judge_gate(monkeypatch):
    # 2026-10-26 측정으로 정한 기본 조합. 환경변수가 없으면 이 조합으로 동작해야 한다
    monkeypatch.delenv("GATE_MODE", raising=False)
    monkeypatch.delenv("QUERY_MODE", raising=False)
    from src.rag import judge, rewrite

    assert rewrite.DEFAULT_MODE == "max" and judge.DEFAULT_GATE_MODE == "judge"
    verdict = judge.Judgement(verdict="none", relevant=[], reason="질문이 묻는 관계가 없음")
    result = answer("질문", search_fn=fake_search([paper(1, score=0.5)]), llm=ExplodingLLM(), judge_fn=lambda *a, **k: verdict)
    assert result["gate_mode"] == "judge" and result["used_llm"] is False and result["verdict"] == "none"


def test_answer_length_is_not_capped_in_the_system_prompt():
    # 2026-10-27: "8문장 이내"가 완결성을 깎는다는 측정(docs/evaluation.md) 때문에 풀었다. 되돌리려면 이 테스트와 문서를 함께 고친다
    assert "8문장" not in SYSTEM_PROMPT and "길이 제한은 없습니다" in SYSTEM_PROMPT
    assert "초록에 없는 수치·사실·조건은 만들지 않습니다" in SYSTEM_PROMPT  # 길이를 풀어도 근거 규칙은 그대로
