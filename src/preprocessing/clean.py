"""수집한 논문(data/raw/*.jsonl)에서 주제와 무관한 논문을 걸러 data/processed/papers.jsonl 로 만든다.

검색어가 넓어서 유기 고분자 유전체, 프탈로시아닌 박막처럼 반도체 공정과 거리가 먼 논문이 섞인다.
논문마다 "자기 주제에 꼭 있어야 할 단어(REQUIRE)"를 확인하고, 공통 제외 단어(EXCLUDE)가 있으면 뺀다.
뺀 논문은 이유와 함께 data/processed/removed.jsonl 에 남겨서 사람이 검토할 수 있게 한다.

실행: uv run python -m src.preprocessing.clean
"""

import json
import re

from src.const.config import PROCESSED_PATH, RAW_DIR, REMOVED_PATH

# 주제별로 제목+초록에 하나라도 있어야 하는 단어. 도메인 판단이 들어가는 부분이라 코드와 분리해 둔다.
REQUIRE = {
    "hfo2_ald": r"hafnium|hafnia|hfo2|hf-based|zirconi|high-?k|gate dielectric|atomic layer",
    "high_k_leakage": r"leakage|breakdown|gate dielectric|mos(fet)?\b|capacitor|transistor|trap",
    "xrd_thin_film": r"thin film|epitax|crystallin|grain size|scherrer|diffraction",
    "cmp_defect": r"cmp|chemical.mechanical|planariz|slurry|polishing",
    "wafer_defect": r"wafer|semiconductor|die\b|fab\b",
    "yield_process": r"semiconductor|wafer|fab\b|lithograph|etch|deposition|yield",
}

# 반도체 공정과 거리가 먼 소재·분야를 가리키는 단어 (필요하면 검토 후 추가/삭제)
# 초록 어디에 나와도 제외하는 단어
EXCLUDE = r"phthalocyanine|elastomer|polyimide|organic (thin.film )?transistor|biomedical|inkjet|perovskite solar|cancer|protein"
# 제목에 있을 때만 제외하는 단어: 초록에는 CMP 패드나 XRD 시료처럼 정상 논문에도 '고분자'가 나올 수 있다
EXCLUDE_TITLE = r"polymer|poly\(|copolymer|nanocomposite|epoxy|p3ht|pcbm"


def load_raw() -> list[dict]:
    papers = []
    for path in sorted(RAW_DIR.glob("*.jsonl")):
        with path.open(encoding="utf-8") as f:
            for line in f:
                p = json.loads(line)
                p["doc_id"] = p.get("work_id") or p.get("arxiv_id")
                p["year"] = p.get("year") or int((p.get("published") or "0")[:4] or 0)
                papers.append(p)
    return papers


def check(paper: dict) -> str | None:
    """남기면 None, 빼야 하면 이유를 돌려준다."""
    text = f"{paper['title']} {paper['summary']}".lower()
    if m := re.search(EXCLUDE, text):
        return "exclude:" + m.group(0)
    if m := re.search(EXCLUDE_TITLE, paper["title"].lower()):
        return "exclude_title:" + m.group(0)
    if not any(re.search(REQUIRE[t], text) for t in paper["topics"] if t in REQUIRE):
        return "require:" + ",".join(paper["topics"])
    return None


def main() -> None:
    kept, removed, seen_titles = [], [], set()
    for paper in load_raw():
        title_key = re.sub(r"\W+", "", paper["title"].lower())
        if title_key in seen_titles:  # arXiv와 OpenAlex에 같은 논문이 있을 때 제목으로 중복 제거
            removed.append({**paper, "removed_reason": "duplicate_title"})
            continue
        seen_titles.add(title_key)
        reason = check(paper)
        (removed if reason else kept).append({**paper, "removed_reason": reason} if reason else paper)

    PROCESSED_PATH.parent.mkdir(parents=True, exist_ok=True)
    for path, rows in ((PROCESSED_PATH, kept), (REMOVED_PATH, removed)):
        with path.open("w", encoding="utf-8") as f:
            for row in rows:
                f.write(json.dumps(row, ensure_ascii=False) + "\n")
    print(f"남김 {len(kept)}건 -> {PROCESSED_PATH}")
    print(f"제거 {len(removed)}건 -> {REMOVED_PATH} (검토용)")


if __name__ == "__main__":
    main()
