"""질문과 가장 가까운 논문을 찾아 보여준다.

실행: uv run python -m src.rag.retriever "HfO2 박막에서 누설전류가 커지는 원인은?" [-k 5]
"""

import argparse
import json

import faiss
import numpy as np

from src.const.config import DOCS_PATH, FAISS_PATH
from src.vectorstore.embedder import get_embeddings, normalize


def max_fuse(scores: np.ndarray, ids: np.ndarray, n_docs: int) -> np.ndarray:
    """검색어별 (점수, 문서 번호) 결과를 문서별 최댓값 점수 하나로 합친다. 점수는 코사인 유사도 그대로라 게이트에 쓸 수 있다."""
    best = np.full(n_docs, -np.inf, dtype="float32")
    for row_scores, row_ids in zip(scores, ids):
        best[row_ids] = np.maximum(best[row_ids], row_scores)
    return best


def search_queries(queries: list[str], k: int = 5) -> list[dict]:
    """검색어 여러 개로 검색해 문서별 최고 점수로 순위를 매긴다 (검색어가 하나면 search와 같은 결과)."""
    index = faiss.read_index(str(FAISS_PATH))
    with DOCS_PATH.open(encoding="utf-8") as f:
        papers = [json.loads(line) for line in f]
    embeddings = get_embeddings()
    vectors = normalize([embeddings.embed_query(q) for q in queries])
    scores, ids = index.search(vectors, index.ntotal)
    best = max_fuse(scores, ids, index.ntotal)
    top = np.argsort(-best)[:k]
    return [{**papers[i], "score": float(best[i])} for i in top]


def search(query: str, k: int = 5) -> list[dict]:
    index = faiss.read_index(str(FAISS_PATH))
    with DOCS_PATH.open(encoding="utf-8") as f:
        papers = [json.loads(line) for line in f]
    query_vec = normalize([get_embeddings().embed_query(query)])
    scores, ids = index.search(query_vec, k)
    return [{**papers[i], "score": float(s)} for s, i in zip(scores[0], ids[0])]


def main() -> None:
    parser = argparse.ArgumentParser(description="논문 검색")
    parser.add_argument("query")
    parser.add_argument("-k", type=int, default=5)
    args = parser.parse_args()

    for rank, p in enumerate(search(args.query, args.k), start=1):
        print(f"{rank}. [{p['score']:.3f}] {p['year']} {p['title']}")
        print(f"   주제: {', '.join(p['topics'])} | {p['source_url']}")
        print(f"   {p['summary'][:160]}...\n")


if __name__ == "__main__":
    main()
