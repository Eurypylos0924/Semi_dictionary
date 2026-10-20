import json
from pathlib import Path

import pytest

from src.evaluation.retrieval_eval import QUESTIONS_PATH, load_questions, score_question, summarize

PROCESSED = Path("data/processed/papers.jsonl")


def test_score_question_uses_first_gold_rank_for_mrr_and_hits():
    q = {"gold_doc_ids": ["A", "B"]}
    result = score_question(q, ["X", "A", "Y", "B"])
    assert result["first_rank"] == 2
    assert result["mrr"] == 0.5
    assert (result["hit@1"], result["hit@3"]) == (0.0, 1.0)
    assert result["recall@3"] == 0.5  # 근거 2편 중 상위 3개 안에서 1편
    assert result["recall@5"] == 1.0


def test_score_question_when_gold_not_retrieved():
    result = score_question({"gold_doc_ids": ["A"]}, ["X", "Y"])
    assert result["first_rank"] is None
    assert result["mrr"] == 0.0 and result["hit@5"] == 0.0


def test_summarize_averages_metrics():
    rows = [score_question({"gold_doc_ids": ["A"]}, ["A"]), score_question({"gold_doc_ids": ["A"]}, ["X"])]
    assert summarize(rows)["hit@1"] == 0.5


def test_question_file_schema_and_unique_ids():
    questions = load_questions()
    ids = [q["id"] for q in questions]
    assert len(ids) == len(set(ids))
    for q in questions:
        assert q["question"].strip()
        if q["answerable"]:
            assert q["gold_doc_ids"] and q["expected_points"]
        else:
            assert q["gold_doc_ids"] == [] and q["note"]


@pytest.mark.skipif(not PROCESSED.exists(), reason="data/processed 는 git에 없으므로 로컬에 있을 때만 검사")
def test_gold_doc_ids_exist_in_corpus():
    corpus = {json.loads(line)["doc_id"] for line in PROCESSED.open(encoding="utf-8")}
    missing = [(q["id"], g) for q in load_questions() for g in q["gold_doc_ids"] if g not in corpus]
    assert not missing


FIELD_PATH = Path("src/evaluation/questions_field.jsonl")


def test_field_question_file_schema():
    questions = load_questions(FIELD_PATH)
    assert len({q["id"] for q in questions}) == len(questions)
    for q in questions:
        assert q["question"].strip()
        if q["answerable"]:
            assert q["gold_doc_ids"] and q["expected_points"]
        else:
            assert q["gold_doc_ids"] == [] and q["note"]
            assert q["unanswerable_kind"] in {"coverage_gap", "out_of_scope"}


@pytest.mark.skipif(not PROCESSED.exists(), reason="data/processed 는 git에 없으므로 로컬에 있을 때만 검사")
def test_field_gold_doc_ids_exist_in_corpus():
    corpus = {json.loads(line)["doc_id"] for line in PROCESSED.open(encoding="utf-8")}
    missing = [(q["id"], g) for q in load_questions(FIELD_PATH) for g in q["gold_doc_ids"] if g not in corpus]
    assert not missing


def test_gate_report_marks_blocked_and_passed_questions():
    from src.const.config import MIN_RETRIEVAL_SCORE
    from src.evaluation.retrieval_eval import gate_report

    rows = [
        {"id": "A", "unanswerable_kind": "out_of_scope", "top_score": MIN_RETRIEVAL_SCORE - 0.1, "question": "q1"},
        {"id": "B", "unanswerable_kind": "coverage_gap", "top_score": MIN_RETRIEVAL_SCORE + 0.1, "question": "q2"},
    ]
    table = "\n".join(gate_report(rows))
    assert "| A | out_of_scope | " in table and "차단" in table.split("| B |")[0]
    assert "통과" in table.split("| B |")[1]
