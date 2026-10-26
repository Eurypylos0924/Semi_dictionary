from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from src.app import logic
from src.rag.prompt import NOT_FOUND

MAIN = str(Path(__file__).resolve().parents[1] / "src" / "app" / "main.py")


def paper(i: int, **extra) -> dict:
    return {"doc_id": f"W{i}", "title": f"Paper {i}", "year": 2000 + i, "summary": f"abstract {i}", "score": 0.5, "source_url": f"https://x/{i}", **extra}


def result(**over) -> dict:
    retrieved = [paper(1), paper(2), paper(3)]
    base = {
        "answer": "펄스를 포화시켜야 한다[2].",
        "retrieved": retrieved,
        "sources": [retrieved[1]],
        "verdict": "answerable",
        "judge_reason": "근거가 있음",
        "invalid_citations": [],
        "uncited": False,
        "used_llm": True,
    }
    return {**base, **over}


# ---- 로직 (streamlit 없이) -----------------------------------------------------------------------------------


def test_status_badge_covers_every_gate_outcome():
    assert logic.status_badge(result(verdict="answerable")) == ("근거 충분", "green")
    assert logic.status_badge(result(verdict="partial")) == ("일부만 근거 있음", "orange")
    assert logic.status_badge(result(verdict=None))[0] == "점수 게이트 통과"  # 게이트가 score일 때는 판정이 없다
    assert logic.status_badge(result(verdict="judge_failed"))[0].startswith("판정 실패")


@pytest.mark.parametrize("verdict", ["none", None, "partial"])
def test_refusal_text_is_shown_as_not_found_whatever_the_verdict(verdict):
    refused = result(answer=f"{NOT_FOUND} 이유", verdict=verdict, sources=[], used_llm=False)
    assert logic.is_refusal(refused) and logic.status_badge(refused) == ("근거를 찾지 못함", "red")


def test_warnings_report_invalid_and_missing_citations_only_when_present():
    assert logic.warnings_for(result()) == []
    notes = logic.warnings_for(result(invalid_citations=[7, 9], uncited=True))
    assert len(notes) == 2 and "[7], [9]" in notes[0] and "인용 번호가 없습니다" in notes[1]


def test_numbered_papers_use_retrieval_rank_as_citation_number_and_mark_cited():
    rows = logic.numbered_papers(result())
    assert [r["number"] for r in rows] == [1, 2, 3]
    assert [r["cited"] for r in rows] == [False, True, False]  # 답변이 [2]를 인용했다


def test_numbered_papers_flag_math_loss_and_truncate_long_abstracts():
    rows = logic.numbered_papers(result(retrieved=[paper(1, math_loss=["값 누락"]), paper(2, summary="가" * 900)], sources=[]))
    assert rows[0]["math_loss"] is True and rows[1]["math_loss"] is False
    assert len(rows[1]["abstract"]) == 501 and rows[1]["abstract"].endswith("…")


def test_judge_reason_is_hidden_when_the_refusal_already_contains_it():
    assert logic.reason_to_show(result()) == "근거가 있음"
    refused = result(answer=f"{NOT_FOUND} 논문에 GPU 사양이 없음", judge_reason="논문에 GPU 사양이 없음", sources=[])
    assert logic.reason_to_show(refused) == ""
    assert logic.reason_to_show(result(judge_reason="")) == ""


def test_safe_md_escapes_dollar_so_text_is_not_rendered_as_math():
    assert logic.safe_md("비용 $5 와 $10") == r"비용 \$5 와 \$10"


def test_run_question_passes_screen_choices_to_the_pipeline(monkeypatch):
    seen = {}

    def fake_answer(question, *, k, llm, search_fn, gate_mode):
        seen.update(question=question, k=k, gate_mode=gate_mode, mode_used=search_fn)
        return result()

    monkeypatch.setattr(logic, "answer", fake_answer)
    monkeypatch.setattr(logic, "search_with_mode", lambda q, n, mode: [mode, n])
    logic.run_question("질문", query_mode="original", gate_mode="score", k=4)
    assert seen["gate_mode"] == "score" and seen["k"] == 4
    assert seen["mode_used"]("q", 4) == ["original", 4]  # 화면에서 고른 검색 방식이 그대로 검색에 쓰인다


def test_run_question_rejects_unknown_modes():
    with pytest.raises(ValueError, match="검색 방식"):
        logic.run_question("q", query_mode="rewrite", gate_mode="judge")
    with pytest.raises(ValueError, match="게이트"):
        logic.run_question("q", query_mode="max", gate_mode="bogus")


def test_examples_include_an_out_of_scope_question_and_do_not_reuse_eval_questions():
    eval_text = (Path(MAIN).parents[1] / "evaluation" / "questions_field.jsonl").read_text(encoding="utf-8")
    assert len(logic.EXAMPLES) >= 3
    assert not [q for q in logic.EXAMPLES if q in eval_text]  # 예시가 평가 질문과 겹치면 데모가 평가에 맞춘 것처럼 보인다


# ---- 화면 (AppTest, 파이프라인은 가짜로 대체) ----------------------------------------------------------------------


@pytest.fixture
def app(monkeypatch):
    calls = []

    def fake_run(question, *, query_mode, gate_mode, **_):
        calls.append((question, query_mode, gate_mode))
        return result()

    monkeypatch.setattr(logic, "run_question", fake_run)
    at = AppTest.from_file(MAIN, default_timeout=15).run()
    at.calls = calls
    return at


def test_app_starts_without_error_and_offers_example_questions(app):
    assert not app.exception
    assert app.title[0].value == "반도체 박막 논문 QA"
    assert len(app.chat_input) == 1


def test_asking_a_question_shows_answer_badge_and_cited_source(app):
    app.chat_input[0].set_value("ALD 펄스는?").run()
    assert not app.exception
    assert app.calls == [("ALD 펄스는?", "max", "judge")]  # 기본 설정은 max + judge
    assert [m.name for m in app.chat_message] == ["user", "assistant"]
    text = " ".join(m.value for m in app.markdown)
    assert "펄스를 포화시켜야 한다[2]." in text and "[2] [Paper 2](https://x/2) (2002)" in text


def test_a_pipeline_failure_is_shown_without_leaking_the_error_message(monkeypatch):
    def boom(*a, **k):
        raise RuntimeError("secret-api-key-123")

    monkeypatch.setattr(logic, "run_question", boom)
    at = AppTest.from_file(MAIN, default_timeout=15).run()
    at.chat_input[0].set_value("질문").run()
    assert not at.exception  # 오류를 삼켜 화면에 알려 주고 앱은 죽지 않는다
    shown = " ".join(e.value for e in at.error)
    assert "RuntimeError" in shown and "secret-api-key-123" not in shown


def test_clearing_the_chat_empties_history(app):
    app.chat_input[0].set_value("질문").run()
    assert len(app.chat_message) == 2
    app.button[0].click().run()
    assert len(app.chat_message) == 0


def _ask_with_example_then_clear(main_path, monkeypatch):
    calls = []

    def fake_run(question, **_):
        calls.append(question)
        return result()

    monkeypatch.setattr(logic, "run_question", fake_run)
    at = AppTest.from_file(main_path, default_timeout=15).run()
    at.pills[0].set_value(logic.EXAMPLES[0]).run()
    assert calls == [logic.EXAMPLES[0]] and len(at.chat_message) == 2
    at.button[0].click().run()
    return at, calls


def test_clearing_the_chat_does_not_ask_the_selected_example_again(monkeypatch):
    # 실제 화면에서 겪은 버그: 고른 예시가 남아 있어 대화를 지우면 같은 질문이 다시 실행됐다
    at, calls = _ask_with_example_then_clear(MAIN, monkeypatch)
    assert not at.exception
    assert calls == [logic.EXAMPLES[0]]  # 질문은 한 번뿐이다
    assert len(at.chat_message) == 0 and at.pills[0].value is None


def test_the_clear_chat_regression_test_detects_the_old_behavior(monkeypatch):
    # 위 테스트가 실제로 버그를 잡는지 확인한다: 예시 버튼의 key를 고정해 옛 동작을 흉내 내면 같은 질문이 다시 실행되어야 한다
    old = Path(MAIN).read_text(encoding="utf-8").replace('key=f"examples_{st.session_state.chat_epoch}"', 'key="examples"')
    assert old != Path(MAIN).read_text(encoding="utf-8")
    copy = Path(MAIN).with_name("_old_main.py")
    copy.write_text(old, encoding="utf-8")
    try:
        _, calls = _ask_with_example_then_clear(str(copy), monkeypatch)
    finally:
        copy.unlink()
    assert len(calls) == 2
