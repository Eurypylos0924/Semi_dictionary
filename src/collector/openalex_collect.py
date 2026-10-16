"""OpenAlex 공식 API로 반도체·박막 공정 논문 메타데이터(제목·초록)를 수집한다.

- arXiv가 이 네트워크에서 rate limit(429)에 걸려 대체/보완용으로 추가한 수집기.
  OpenAlex는 arXiv 외 학술지 논문까지 포함하므로 반도체 소재·공정 논문 범위가 더 넓다.
- OpenAlex는 초록을 '단어 -> 위치 목록' 형태(inverted index)로 주기 때문에 문장으로 복원해 저장한다.
- 논문은 거의 바뀌지 않으므로 data/raw/openalex.jsonl 이 이미 있으면 수집을 건너뛴다.
  새 논문을 더 받고 싶을 때만 --refresh 를 쓰며, 기존 논문은 그대로 두고 새 논문만 합친다.

실행: uv run python -m src.collector.openalex_collect --max-per-query 40 [--refresh]
"""

import argparse
import json
import re
import time
from pathlib import Path

import requests

API_URL = "https://api.openalex.org/works"
REQUEST_INTERVAL_SEC = 1.5
OUT_PATH = Path("data/raw/openalex.jsonl")
HEADERS = {"User-Agent": "semicon-rag-portfolio/0.1 (personal study project)"}
SELECT = "id,doi,title,publication_year,authorships,abstract_inverted_index,cited_by_count,type"

# 주제 이름 -> 검색어. OpenAlex는 따옴표로 묶으면 구(phrase) 검색이 된다.
TOPICS = {
    "hfo2_ald": '"hafnium oxide" "atomic layer deposition"',
    "high_k_leakage": '"leakage current" "high-k" dielectric',
    "xrd_thin_film": '"X-ray diffraction" "thin film" crystallinity grain size',
    "cmp_defect": '"chemical mechanical planarization" defect',
    "wafer_defect": '"wafer map" defect pattern classification',
    "yield_process": 'semiconductor manufacturing yield "root cause" analysis',
}


def restore_abstract(inverted_index: dict | None) -> str:
    """{'단어': [위치, ...]} 를 위치 순서대로 이어 붙여 원래 초록 문장으로 되돌린다."""
    if not inverted_index:
        return ""
    words: dict[int, str] = {}
    for word, positions in inverted_index.items():
        for pos in positions:
            words[pos] = word
    return re.sub(r"\s+", " ", " ".join(words[i] for i in sorted(words))).strip()


def fetch(query: str, per_page: int) -> list[dict]:
    params = {
        "search": query,
        "filter": "has_abstract:true,type:article,language:en",
        "per-page": per_page,
        "select": SELECT,
    }
    resp = requests.get(API_URL, params=params, headers=HEADERS, timeout=60)
    if resp.status_code != 200:
        raise RuntimeError(f"OpenAlex 응답 {resp.status_code}: {resp.text[:200]}")
    return resp.json()["results"]


def to_record(work: dict, topic: str) -> dict:
    openalex_id = work["id"].rsplit("/", 1)[-1]
    doi = work.get("doi") or ""
    return {
        "work_id": openalex_id,
        "title": re.sub(r"\s+", " ", work.get("title") or "").strip(),
        "summary": restore_abstract(work.get("abstract_inverted_index")),
        "authors": [a["author"]["display_name"] for a in work.get("authorships", [])],
        "year": work.get("publication_year"),
        "doi": doi,
        "cited_by_count": work.get("cited_by_count", 0),
        "source": "openalex",
        "source_url": doi or work["id"],
        "topics": [topic],
    }


def collect(max_per_query: int) -> dict[str, dict]:
    collected: dict[str, dict] = {}
    for i, (topic, query) in enumerate(TOPICS.items()):
        if i > 0:
            time.sleep(REQUEST_INTERVAL_SEC)
        print(f"[{topic}] {query}", flush=True)
        new = 0
        for work in fetch(query, max_per_query):
            rec = to_record(work, topic)
            if not rec["summary"]:
                continue
            if rec["work_id"] in collected:
                collected[rec["work_id"]]["topics"].append(topic)
            else:
                collected[rec["work_id"]] = rec
                new += 1
        print(f"  새 논문 {new}건 (누적 {len(collected)}건)", flush=True)
    return collected


def main() -> None:
    parser = argparse.ArgumentParser(description="OpenAlex 반도체 논문 메타데이터 수집")
    parser.add_argument("--max-per-query", type=int, default=40, help="주제당 가져올 최대 논문 수")
    parser.add_argument("--refresh", action="store_true", help="이미 수집된 파일이 있어도 새 논문을 추가로 가져옴")
    args = parser.parse_args()

    existing: dict[str, dict] = {}
    if OUT_PATH.exists():
        with OUT_PATH.open(encoding="utf-8") as f:
            existing = {p["work_id"]: p for p in map(json.loads, f)}
        if not args.refresh:
            print(f"{OUT_PATH}에 이미 {len(existing)}건이 있어 수집을 건너뜁니다. 새 논문을 더 받으려면 --refresh")
            return

    collected = collect(args.max_per_query)
    new_count = len(collected.keys() - existing.keys())
    existing.update({k: v for k, v in collected.items() if k not in existing})

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUT_PATH.open("w", encoding="utf-8") as f:
        for paper in existing.values():
            f.write(json.dumps(paper, ensure_ascii=False) + "\n")
    print(f"\n저장 완료: {OUT_PATH} (전체 {len(existing)}건, 이번에 새로 추가 {new_count}건)")


if __name__ == "__main__":
    main()
