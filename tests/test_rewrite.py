import numpy as np
import pytest
from langchain_core.language_models.fake_chat_models import FakeListChatModel

from src.rag import rewrite
from src.rag.retriever import max_fuse
from src.rag.rewrite import clean_rewrite, read_cache, rewrite_query, search_with_mode, write_cache


def test_max_fuse_takes_best_score_per_document_across_queries():
    scores = np.array([[0.9, 0.5, 0.1], [0.3, 0.8, 0.2]], dtype="float32")
    ids = np.array([[0, 1, 2], [1, 0, 2]])  # 두 번째 검색어는 문서 번호 순서가 다름
    best = max_fuse(scores, ids, 3)
    # 문서0: 첫 검색어 0.9, 둘째 검색어 0.8(둘째 행의 ids가 [1,0,2]이므로 0번 문서 점수는 0.8) -> 0.9
    assert best[0] == pytest.approx(0.9)
    # 문서1: 첫 검색어 0.5, 둘째 검색어 0.3 -> 0.5
    assert best[1] == pytest.approx(0.5)
    # 문서2: 첫 검색어 0.1, 둘째 검색어 0.2 -> 0.2
    assert best[2] == pytest.approx(0.2)


@pytest.mark.parametrize(
    "raw, expected",
    [
        ("  leakage current in HfO2 after annealing \n", "leakage current in HfO2 after annealing"),
        ('"XRD peak broadening"', "XRD peak broadening"),
        ("Query: atomic layer deposition (ALD)\n설명입니다", "atomic layer deposition (ALD)"),
        ("\n\nsearch query: CMP dishing erosion\n", "CMP dishing erosion"),
        ("", ""),
    ],
)
def test_clean_rewrite_keeps_only_the_query_line(raw, expected):
    assert clean_rewrite(raw) == expected


def test_rewrite_query_uses_llm_then_cache(tmp_path):
    cache = tmp_path / "rewrites.jsonl"
    first = rewrite_query("질문", llm=FakeListChatModel(responses=['"HfO2 crystallization leakage"']), cache_path=cache)
    assert first == "HfO2 crystallization leakage"
    assert len(read_cache(cache)) == 1
    # 같은 질문은 LLM을 부르지 않고 캐시를 쓴다 (응답 목록이 비어 있어도 실패하지 않음)
    again = rewrite_query("질문", llm=FakeListChatModel(responses=["다른 답"]), cache_path=cache)
    assert again == "HfO2 crystallization leakage"


def test_rewrite_query_falls_back_to_original_when_llm_returns_nothing(tmp_path):
    result = rewrite_query("원문 질문", llm=FakeListChatModel(responses=["   "]), cache_path=tmp_path / "c.jsonl")
    assert result == "원문 질문"
    assert not (tmp_path / "c.jsonl").exists()  # 실패한 재작성은 캐시하지 않는다


def test_cache_roundtrip(tmp_path):
    path = tmp_path / "sub" / "c.jsonl"
    write_cache(path, "k1", "q", "r")
    assert read_cache(path) == {"k1": "r"}


def test_search_with_mode_dispatch(monkeypatch):
    calls = {}
    monkeypatch.setattr(rewrite, "search", lambda q, k: calls.setdefault("original", (q, k)) and [])
    monkeypatch.setattr(rewrite, "search_queries", lambda qs, k: calls.setdefault("queries", (list(qs), k)) and [])

    search_with_mode("원문", 3, "original", rewriter=lambda q: "EN")
    assert calls["original"] == ("원문", 3)

    search_with_mode("원문", 3, "rewrite", rewriter=lambda q: "EN")
    assert calls["queries"] == (["EN"], 3)

    calls.pop("queries")
    search_with_mode("원문", 3, "max", rewriter=lambda q: "EN")
    assert calls["queries"] == (["원문", "EN"], 3)


def test_search_with_mode_rejects_unknown_mode_and_reads_env(monkeypatch):
    with pytest.raises(ValueError, match="original"):
        search_with_mode("q", 1, "bogus")
    monkeypatch.setenv("QUERY_MODE", "bogus")
    with pytest.raises(ValueError):
        search_with_mode("q", 1)
