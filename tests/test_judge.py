import pytest
from langchain_core.language_models.fake_chat_models import FakeListChatModel
from langchain_core.messages import AIMessage
from langchain_core.runnables import RunnableLambda

from src.rag.generator import answer
from src.rag.judge import HARD_FLOOR, Judgement, judge, normalize, read_cache
from src.rag.prompt import NOT_FOUND


def paper(i: int, score: float = 0.6) -> dict:
    return {"doc_id": f"W{i}", "title": f"Paper {i}", "year": 2000 + i, "summary": f"abstract {i}", "score": score, "source_url": f"https://x/{i}"}


def fake_search(papers):
    return lambda question, k: papers[:k]


def fake(content: str) -> FakeListChatModel:
    return FakeListChatModel(responses=[content])


# ---- judge() ----------------------------------------------------------------------------------------------


def test_judge_parses_json_and_drops_nonexistent_paper_numbers(tmp_path):
    raw = '{"verdict": "partial", "relevant": [2, 9], "reason": "일부만 다룸"}'
    result = judge("질문", [paper(1), paper(2), paper(3)], llm=fake(raw), cache_path=tmp_path / "c.jsonl")
    assert result.verdict == "partial" and result.relevant == [2]


def test_judge_accepts_nested_or_string_paper_numbers(tmp_path):
    raw = '{"verdict": "partial", "relevant": [[1, 2], "3"], "reason": "중첩 목록"}'
    result = judge("질문", [paper(1), paper(2), paper(3)], llm=fake(raw), cache_path=tmp_path / "c.jsonl")
    assert result.relevant == [1, 2, 3]


def test_judge_none_has_no_relevant_papers(tmp_path):
    raw = '```json\n{"verdict": "none", "relevant": [1, 2], "reason": "관계를 다루지 않음"}\n```'  # 코드 펜스도 허용
    result = judge("질문", [paper(1), paper(2)], llm=fake(raw), cache_path=tmp_path / "c.jsonl")
    assert result.verdict == "none" and result.relevant == []


def test_normalize_uses_all_papers_when_answerable_but_none_selected():
    result = normalize(Judgement(verdict="answerable", relevant=[]), n_papers=3)
    assert result.relevant == [1, 2, 3]


def test_judge_returns_none_on_malformed_output(tmp_path):
    assert judge("질문", [paper(1)], llm=fake("네, 답할 수 있습니다."), cache_path=tmp_path / "c.jsonl") is None
    assert not (tmp_path / "c.jsonl").exists()  # 실패한 판정은 캐시하지 않는다


def test_judge_uses_cache_for_same_question_and_papers(tmp_path):
    cache = tmp_path / "c.jsonl"
    papers = [paper(1), paper(2)]
    first = judge("질문", papers, llm=fake('{"verdict": "answerable", "relevant": [1], "reason": "직접 다룸"}'), cache_path=cache)
    assert len(read_cache(cache)) == 1
    again = judge("질문", papers, llm=fake('{"verdict": "none", "relevant": [], "reason": "다른 답"}'), cache_path=cache)
    assert again == first  # LLM을 다시 부르지 않고 캐시를 쓴다
    other = judge("질문", [paper(3)], llm=fake('{"verdict": "none", "relevant": [], "reason": "논문 목록이 다르면 새로 판정"}'), cache_path=cache)
    assert other.verdict == "none"


# ---- answer() 의 judge 게이트 모드 ---------------------------------------------------------------------------


def never_called(*args, **kwargs):
    raise AssertionError("호출되면 안 된다")


def test_judge_mode_rejects_below_hard_floor_without_calling_judge():
    result = answer("질문", search_fn=fake_search([paper(1, HARD_FLOOR - 0.01)]), llm=None, gate_mode="judge", judge_fn=never_called)
    assert result["answer"] == NOT_FOUND and result["used_llm"] is False


def test_judge_mode_none_verdict_refuses_with_reason_and_skips_answer_llm():
    judgement = Judgement(verdict="none", relevant=[], reason="CMP와 Idsat을 연결한 초록이 없음")
    result = answer("질문", search_fn=fake_search([paper(1, 0.5)]), llm=None, gate_mode="judge", judge_fn=lambda q, p, llm=None: judgement)
    assert result["answer"].startswith(NOT_FOUND) and "Idsat" in result["answer"]
    assert result["used_llm"] is False and result["verdict"] == "none"


def test_judge_mode_partial_with_selection_passes_only_relevant_papers_and_hint_to_answer_llm():
    seen = []
    llm = RunnableLambda(lambda prompt_value: (seen.append(prompt_value.to_string()), AIMessage(content="일부 답이다[1]."))[1])
    judgement = Judgement(verdict="partial", relevant=[2], reason="일부만")
    result = answer("질문", search_fn=fake_search([paper(1), paper(2), paper(3)]), llm=llm, gate_mode="judge", judge_fn=lambda q, p, llm=None: judgement, use_judge_selection=True)
    prompt = seen[0]
    assert "Paper 2" in prompt and "Paper 1" not in prompt and "Paper 3" not in prompt  # 판정이 고른 논문만
    assert "[검토 메모]" in prompt
    assert [p["title"] for p in result["sources"]] == ["Paper 2"]  # 번호는 고른 논문 기준으로 다시 매겨짐
    assert result["verdict"] == "partial"


def test_judge_mode_answerable_has_no_hint():
    seen = []
    llm = RunnableLambda(lambda prompt_value: (seen.append(prompt_value.to_string()), AIMessage(content="답[1]."))[1])
    judgement = Judgement(verdict="answerable", relevant=[1], reason="직접 다룸")
    answer("질문", search_fn=fake_search([paper(1)]), llm=llm, gate_mode="judge", judge_fn=lambda q, p, llm=None: judgement)
    assert "[검토 메모]" not in seen[0]


@pytest.mark.parametrize("score, should_answer", [(0.5, True), (0.2, False)])
def test_judge_failure_falls_back_to_score_gate(score, should_answer):
    llm = fake("근거 있는 답[1].")
    result = answer("질문", search_fn=fake_search([paper(1, score)]), llm=llm, gate_mode="judge", judge_fn=lambda q, p, llm=None: None)
    assert result["used_llm"] is should_answer


def test_unknown_gate_mode_raises():
    with pytest.raises(ValueError, match="score"):
        answer("질문", search_fn=fake_search([paper(1)]), gate_mode="bogus")


def test_judge_selection_is_off_by_default_so_all_retrieved_papers_are_used():
    seen = []
    llm = RunnableLambda(lambda prompt_value: (seen.append(prompt_value.to_string()), AIMessage(content="답[1]."))[1])
    judgement = Judgement(verdict="answerable", relevant=[2], reason="직접 다룸")
    result = answer("질문", search_fn=fake_search([paper(1), paper(2)]), llm=llm, gate_mode="judge", judge_fn=lambda q, p, llm=None: judgement)
    assert "Paper 1" in seen[0] and "Paper 2" in seen[0]
    assert [p["title"] for p in result["sources"]] == ["Paper 1"]
