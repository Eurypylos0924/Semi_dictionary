"""data/processed/papers.jsonl 의 논문을 임베딩해 FAISS 인덱스로 저장한다.

- 논문 1건 = 청크 1개. 초록이 평균 1,150자라 따로 쪼개지 않고 "제목 + 초록"을 통째로 임베딩한다.
- 인덱스는 한 번 만들어 두고 검색 때는 파일만 읽는다 (임베딩 API는 새 질문 1건만 호출).
- 인덱스가 이미 있으면 건너뛴다. 논문을 새로 수집했을 때만 --rebuild 로 다시 만든다.

실행: uv run python -m src.vectorstore.build [--rebuild]
"""

import argparse
import json

import faiss

from src.const.config import DOCS_PATH, EMBED_BATCH_SIZE, FAISS_PATH, INDEX_DIR, PROCESSED_PATH
from src.vectorstore.embedder import get_embeddings, normalize


def main() -> None:
    parser = argparse.ArgumentParser(description="논문 임베딩 + FAISS 인덱스 구축")
    parser.add_argument("--rebuild", action="store_true", help="인덱스가 있어도 처음부터 다시 만듦")
    args = parser.parse_args()

    if FAISS_PATH.exists() and not args.rebuild:
        print(f"{FAISS_PATH}가 이미 있어 건너뜁니다. 다시 만들려면 --rebuild")
        return

    with PROCESSED_PATH.open(encoding="utf-8") as f:
        papers = [json.loads(line) for line in f]
    texts = [f"{p['title']}\n{p['summary']}" for p in papers]

    emb = get_embeddings()
    vectors: list[list[float]] = []
    for i in range(0, len(texts), EMBED_BATCH_SIZE):
        vectors += emb.embed_documents(texts[i : i + EMBED_BATCH_SIZE])
        print(f"  임베딩 {min(i + EMBED_BATCH_SIZE, len(texts))}/{len(texts)}", flush=True)

    matrix = normalize(vectors)
    index = faiss.IndexFlatIP(matrix.shape[1])
    index.add(matrix)

    INDEX_DIR.mkdir(parents=True, exist_ok=True)
    faiss.write_index(index, str(FAISS_PATH))
    with DOCS_PATH.open("w", encoding="utf-8") as f:  # FAISS 번호(0..N-1)와 같은 순서로 저장
        for p in papers:
            f.write(json.dumps(p, ensure_ascii=False) + "\n")
    print(f"저장 완료: {FAISS_PATH} (논문 {len(papers)}건, {matrix.shape[1]}차원)")


if __name__ == "__main__":
    main()
