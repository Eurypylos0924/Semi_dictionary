"""arXiv 공식 API로 반도체·박막 공정 논문 메타데이터(제목·초록)를 수집한다.

- 크롤링이 아니라 공식 API를 사용한다 (arXiv 이용 규칙: 요청 간 3초 이상 간격, 단일 연결).
- 논문은 거의 바뀌지 않으므로 data/raw/arxiv.jsonl 이 이미 있으면 수집을 건너뛴다.
  새 논문을 더 받고 싶을 때만 --refresh 를 쓰며, arxiv_id 기준으로 기존 논문은 그대로 두고 새 논문만 합친다.
- 같은 논문이 여러 주제에 걸리면 한 번만 저장하고 topics 목록에 주제를 모은다.

실행: uv run python -m src.collector.arxiv_collect --max-per-query 50 [--refresh]
"""

import argparse
import json
import re
import time
import xml.etree.ElementTree as ET
from pathlib import Path

import requests

API_URL = "https://export.arxiv.org/api/query"
REQUEST_INTERVAL_SEC = 3.5
MAX_RETRIES = 5
OUT_PATH = Path("data/raw/arxiv.jsonl")

# 주제 이름 -> arXiv 검색식. 도메인(소재·공정·QA)에 맞게 직접 고르는 부분이라 코드와 분리해 둔다.
TOPICS = {
    "hfo2_ald": 'all:"hafnium oxide" AND all:"atomic layer deposition"',
    "high_k_leakage": 'all:"leakage current" AND all:"high-k"',
    "xrd_thin_film": 'all:"X-ray diffraction" AND all:"thin film" AND (all:crystallinity OR all:"grain size")',
    "cmp_defect": 'all:"chemical mechanical planarization" OR all:"chemical mechanical polishing"',
    "wafer_defect": 'all:"wafer map" OR (all:"wafer" AND all:"defect pattern")',
    "yield_process": 'all:"semiconductor" AND all:"yield" AND (all:"process control" OR all:"root cause")',
}

NS = {"atom": "http://www.w3.org/2005/Atom", "arxiv": "http://arxiv.org/schemas/atom"}
HEADERS = {"User-Agent": "semicon-rag-portfolio/0.1 (personal study project)"}


def fetch(query: str, start: int, max_results: int) -> str:
    """arXiv API를 한 번 호출한다. 한도 초과(429)면 점점 오래 기다렸다가 다시 시도한다."""
    params = {
        "search_query": query,
        "start": start,
        "max_results": max_results,
        "sortBy": "relevance",
        "sortOrder": "descending",
    }
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            resp = requests.get(API_URL, params=params, headers=HEADERS, timeout=60)
            if resp.status_code == 200 and "<feed" in resp.text:
                return resp.text
            reason = f"응답 {resp.status_code} {resp.text[:40]!r}"
        except requests.RequestException as e:
            reason = f"연결 오류 {type(e).__name__}"
        wait = 30 * attempt
        print(f"  {reason} -> {wait}초 대기 후 재시도 {attempt}/{MAX_RETRIES}", flush=True)
        time.sleep(wait)
    raise RuntimeError(f"arXiv 요청 실패: {query}")


def clean(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip()


def parse(xml_text: str) -> list[dict]:
    root = ET.fromstring(xml_text)
    papers = []
    for entry in root.findall("atom:entry", NS):
        abs_url = clean(entry.findtext("atom:id", "", NS))
        # http://arxiv.org/abs/2101.01234v2 -> 2101.01234 (버전 번호 제거)
        arxiv_id = re.sub(r"v\d+$", "", abs_url.rsplit("/abs/", 1)[-1])
        pdf_url = next(
            (l.get("href") for l in entry.findall("atom:link", NS) if l.get("title") == "pdf"), ""
        )
        papers.append(
            {
                "arxiv_id": arxiv_id,
                "title": clean(entry.findtext("atom:title", "", NS)),
                "summary": clean(entry.findtext("atom:summary", "", NS)),
                "authors": [clean(a.findtext("atom:name", "", NS)) for a in entry.findall("atom:author", NS)],
                "published": entry.findtext("atom:published", "", NS)[:10],
                "primary_category": (entry.find("arxiv:primary_category", NS).get("term")
                                     if entry.find("arxiv:primary_category", NS) is not None else ""),
                "categories": [c.get("term") for c in entry.findall("atom:category", NS)],
                "doi": clean(entry.findtext("arxiv:doi", "", NS)),
                "source": "arxiv",
                "source_url": f"https://arxiv.org/abs/{arxiv_id}",
                "pdf_url": pdf_url,
            }
        )
    return papers


def collect(max_per_query: int) -> dict[str, dict]:
    collected: dict[str, dict] = {}
    for i, (topic, query) in enumerate(TOPICS.items()):
        if i > 0:
            time.sleep(REQUEST_INTERVAL_SEC)
        print(f"[{topic}] {query}")
        papers = parse(fetch(query, start=0, max_results=max_per_query))
        new = 0
        for p in papers:
            if p["arxiv_id"] in collected:
                collected[p["arxiv_id"]]["topics"].append(topic)
            else:
                p["topics"] = [topic]
                collected[p["arxiv_id"]] = p
                new += 1
        print(f"  가져온 {len(papers)}건 중 새 논문 {new}건 (누적 {len(collected)}건)")
    return collected


def main() -> None:
    parser = argparse.ArgumentParser(description="arXiv 반도체 논문 메타데이터 수집")
    parser.add_argument("--max-per-query", type=int, default=50, help="주제당 가져올 최대 논문 수")
    parser.add_argument("--refresh", action="store_true", help="이미 수집된 파일이 있어도 새 논문을 추가로 가져옴")
    args = parser.parse_args()

    existing: dict[str, dict] = {}
    if OUT_PATH.exists():
        with OUT_PATH.open(encoding="utf-8") as f:
            existing = {p["arxiv_id"]: p for p in map(json.loads, f)}
        if not args.refresh:
            print(f"{OUT_PATH}에 이미 {len(existing)}건이 있어 수집을 건너뜁니다. 새 논문을 더 받으려면 --refresh")
            return

    collected = collect(args.max_per_query)
    new_count = len(collected.keys() - existing.keys())
    existing.update({k: v for k, v in collected.items() if k not in existing})  # 기존 논문은 그대로 유지

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUT_PATH.open("w", encoding="utf-8") as f:
        for paper in existing.values():
            f.write(json.dumps(paper, ensure_ascii=False) + "\n")
    print(f"\n저장 완료: {OUT_PATH} (전체 {len(existing)}건, 이번에 새로 추가 {new_count}건)")


if __name__ == "__main__":
    main()
