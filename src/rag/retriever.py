"""질문과 가장 가까운 논문을 찾아 보여준다.

실행: uv run python -m src.rag.retriever "HfO2 박막에서 누설전류가 커지는 원인은?" [-k 5]
"""

import argparse
import json

import faiss

from src.const.config import DOCS_PATH, FAISS_PATH
from src.vectorstore.embedder import get_embeddings, normalize


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
