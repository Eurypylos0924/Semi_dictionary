import pytest

from src.evaluation.faithfulness import (
    Claim,
    Coverage,
    PointCoverage,
    aggregate,
    is_limitation,
    coverage_score,
    problem_claims,
    read_cache,
    spot_check,
    write_cache,
)


def claim(verdict: str, cited=None, supported_by=None, text="주장") -> Claim:
    return Claim(claim=text, cited=cited or [], verdict=verdict, supported_by=supported_by or [], note="메모")


def rec(claims, answered=True, coverage=None) -> dict:
    return {"answered": answered, "claims": claims, "coverage": coverage}


def test_claim_accepts_nested_and_string_numbers():
    c = Claim(claim="x", cited=[[1, 2], "3"], verdict="supported", supported_by=["2"])
    assert c.cited == [1, 2, 3] and c.supported_by == [2]


def test_aggregate_counts_each_verdict_and_derived_rates():
    records = [
        rec([claim("supported", [1]), claim("supported", [2]), claim("misattributed", [3], [1]), claim("unsupported")]),
        rec([claim("contradicted", [1])]),
    ]
    a = aggregate(records)
    assert a["claims"] == 5
    assert a["faithfulness"] == pytest.approx(2 / 5)
    assert a["misattribution_rate"] == pytest.approx(1 / 5)
    assert a["hallucination_rate"] == pytest.approx(2 / 5)  # unsupported 1 + contradicted 1
    assert a["citation_correct"] == pytest.approx(2 / 3)  # 근거가 있는 주장(supported 2 + misattributed 1) 중 번호까지 맞은 것
    assert a["faithfulness_macro"] == pytest.approx((2 / 4 + 0) / 2)


def test_aggregate_separates_refused_questions_and_averages_completeness_both_ways():
    records = [rec([claim("supported")], coverage=1.0), rec(None, answered=False, coverage=None), rec([claim("supported")], coverage=0.5)]
    a = aggregate(records)
    assert (a["questions"], a["answered"], a["refused"]) == (3, 2, 1)
    assert a["completeness"] == pytest.approx(0.75)  # 답변한 질문 기준
    assert a["completeness_all"] == pytest.approx(1.5 / 3)  # 거절한 질문은 0점으로 계산


def test_aggregate_ignores_answers_whose_grading_failed():
    a = aggregate([rec(None, answered=True), rec([claim("supported")])])
    assert a["graded_answers"] == 1 and a["claims"] == 1 and a["faithfulness"] == 1.0


def test_aggregate_with_no_claims_returns_none_rates():
    a = aggregate([rec([], answered=True)])
    assert a["claims"] == 0 and a["faithfulness"] is None and a["citation_correct"] is None


def test_coverage_score_treats_missing_points_as_not_covered():
    cov = Coverage(points=[PointCoverage(index=1, covered="yes"), PointCoverage(index=2, covered="partial")])
    assert coverage_score(cov, 3) == pytest.approx((1 + 0.5 + 0) / 3)  # 3번 항목은 채점에 없어 no로 간주
    assert coverage_score(None, 3) is None


def test_problem_claims_lists_only_non_supported():
    details = [{"config": "c", "id": "F01", "claims": [claim("supported"), claim("unsupported", text="부풀린 주장")]}, {"config": "c", "id": "F02", "claims": None}]
    lines = problem_claims(details)
    assert len(lines) == 1 and "부풀린 주장" in lines[0] and "F01" in lines[0]


def test_spot_check_shows_cited_abstract_and_verdict_and_is_reproducible():
    record = {"retrieved": [{"title": "T1", "summary": "초록 하나", "doc_id": "W1"}, {"title": "T2", "summary": "초록 둘", "doc_id": "W2"}]}
    details = [{"config": "c", "id": "F01", "question": "질문", "record": record, "claims": [claim("supported", [2], [2], "주장 하나")]}]
    text = spot_check(details, n=5)
    assert "주장 하나" in text and "초록 둘" in text and "supported" in text
    assert spot_check(details, n=5) == text


def test_cache_roundtrip(tmp_path):
    path = tmp_path / "x" / "c.jsonl"
    write_cache(path, "k", {"a": 1})
    assert read_cache(path) == {"k": {"a": 1}}


def test_is_limitation_detects_honest_absence_statements_only():
    assert is_limitation(claim("unsupported", text="구체적인 수치는 논문에서 확인되지 않음"))
    assert is_limitation(claim("unsupported", text="Other factors are not confirmed in the provided papers."))
    assert not is_limitation(claim("supported", text="HfO2는 약 700도에서 결정화된다"))


def test_aggregate_can_drop_limitation_statements_from_the_claim_count():
    records = [rec([claim("supported", text="사실 주장"), claim("unsupported", text="수율 영향은 논문에서 확인되지 않음")])]
    raw, filtered = aggregate(records), aggregate(records, drop_limitations=True)
    assert raw["claims"] == 2 and raw["hallucination_rate"] == pytest.approx(0.5)
    assert filtered["claims"] == 1 and filtered["hallucination_rate"] == 0.0
