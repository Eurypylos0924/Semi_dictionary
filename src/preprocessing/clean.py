"""수집한 논문(data/raw/*.jsonl)에서 주제와 무관한 논문을 걸러 data/processed/papers.jsonl 로 만든다.

검색어가 넓어서 유기 고분자 유전체, 프탈로시아닌 박막처럼 반도체 공정과 거리가 먼 논문이 섞인다.
논문마다 "자기 주제에 꼭 있어야 할 단어(REQUIRE)"를 확인하고, 공통 제외 단어(EXCLUDE)가 있으면 뺀다.
뺀 논문은 이유와 함께 data/processed/removed.jsonl 에 남겨서 사람이 검토할 수 있게 한다.

수식이 빠진 초록은 빼되, 사람이 검토해 남기기로 한 논문(KEEP_WITH_FLAG)은 math_loss 표시를 붙여 남긴다. OpenAlex 초록에서는 수식·수치(LaTeX)가 통째로 사라져 "pulse times of must be applied",
"from room temperature to ."처럼 값이 빠진 문장이 남고, LLM이 그 빈자리를 지어내 환각을 만든 사례가 있었다(docs/evaluation.md).
Crossref 등 다른 출처로 복구하는 것은 시도해 보았으나 해당 논문들의 초록이 아예 없거나 같은 부분이 비어 있어 현실적이지 않았다.

실행: uv run python -m src.preprocessing.clean
"""

import argparse
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
    "xrd_scherrer": r"scherrer|crystallite size|fwhm|full width|line broadening",
    "xrd_williamson_hall": r"williamson|crystallite size|strain|line broadening|peak profile",
    "hfo2_leakage_mechanism": r"leakage|conduction|poole|tunnel|schottky|trap",
}

# 반도체 공정과 거리가 먼 소재·분야를 가리키는 단어 (필요하면 검토 후 추가/삭제)
# 초록 어디에 나와도 제외하는 단어
EXCLUDE = r"phthalocyanine|elastomer|polyimide|organic (thin.film )?transistor|biomedical|inkjet|perovskite solar|cancer|protein"
# 제목에 있을 때만 제외하는 단어: 초록에는 CMP 패드나 XRD 시료처럼 정상 논문에도 '고분자'가 나올 수 있다
EXCLUDE_TITLE = r"polymer|poly\(|copolymer|nanocomposite|epoxy|p3ht|pcbm"

# 수식·수치가 빠진 초록의 흔적: 값이 있어야 할 자리가 비어 문장이 어색해진 형태. 코퍼스 322건을 직접 훑어 만들었다.
# 정상 문법을 오탐하지 않도록 'than for'(비교), 'up to and'(범위), 'high- and low-'(접두어 나열)는 일부러 걸리지 않게 했다.
# 한계: 눈에 보이는 빈자리만 잡는다. 문장이 멀쩡하게 이어지는 누락은 못 찾는다.
MATH_LOSS_PATTERNS = {
    "값 누락(전치사·비교어 뒤가 비어 있음)": r"(?i:\b(?:of|to|from|by|at|than|between|above|below|about|around|near|over|under|until)\s+[,.;)])",
    "값 누락(of 뒤 and, from/to/at/of 뒤 for)": r"(?i:\bof\s+and\b|\b(?:from|to|at|of)\s+for\b)",
    "수식 누락(빈 괄호)": r"\(\s*\)|\[\s*\]",
    "값 누락(sub-, high- 같은 접두어 뒤)": r"(?i:\b(?:sub|high|low|ultra|near|multi|wide|narrow)-\s+(?!and\b|or\b|to\b)[a-z])",
    "주어 누락(전치사 뒤 조동사)": r"(?i:\b(?:of|from|by|at|than)\s+(?:must|should|can|will|is|are|was|were|has|have)\b)",
    "값 누락(단위만 남음)": r"(?i:\b(?:of|at|to|from|than|above|below|about|around|under|over|between))\s+(?:nm|μm|µm|eV|MV|kV|°C|Å|fF|pF|GHz|A/cm)\b",
    "수식 누락(쉼표·and 뒤 닫는 괄호)": r"(?i:(?:,|\band)\s*\))",
    "글자 깨짐(마침표 뒤 소문자)": r"\s\.\s+[a-z]",
}


def math_loss_signals(summary: str) -> list[str]:
    """초록에서 수식·수치 누락으로 보이는 신호의 이름 목록. 없으면 빈 목록."""
    return [name for name, pattern in MATH_LOSS_PATTERNS.items() if re.search(pattern, summary)]


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


# 수식이 빠졌지만 사람이 검토해 "남기되 표시"하기로 한 논문 (doc_id -> 이유). 남긴 논문에는 math_loss 필드(걸린 신호 목록)가 붙는다.
KEEP_WITH_FLAG = {
    "W2076838934": "ALD 포화 펄스·표면 수산화와 누설전류의 관계 등 정성적 내용이 유용함 (2026-10-21 사용자 결정). 펄스 시간 등 수치는 초록에 없으므로 답변에서 만들면 안 됨",
}


def apply_math_loss_policy(paper: dict, reason: str | None, keep_all: bool = False) -> tuple[dict, str | None]:
    """수식 누락으로 제거될 논문 중 남기기로 한 것(KEEP_WITH_FLAG 또는 keep_all)은 math_loss 표시를 붙여 남긴다."""
    if not (reason and reason.startswith("math_loss:")):
        return paper, reason
    if keep_all or paper["doc_id"] in KEEP_WITH_FLAG:
        return {**paper, "math_loss": math_loss_signals(paper["summary"])}, None
    return paper, reason


def check(paper: dict, drop_math_loss: bool = True) -> str | None:
    """남기면 None, 빼야 하면 이유를 돌려준다."""
    text = f"{paper['title']} {paper['summary']}".lower()
    if m := re.search(EXCLUDE, text):
        return "exclude:" + m.group(0)
    if m := re.search(EXCLUDE_TITLE, paper["title"].lower()):
        return "exclude_title:" + m.group(0)
    if not any(re.search(REQUIRE[t], text) for t in paper["topics"] if t in REQUIRE):
        return "require:" + ",".join(paper["topics"])
    if drop_math_loss and (signals := math_loss_signals(paper["summary"])):
        return "math_loss:" + ",".join(signals)
    return None


def main() -> None:
    parser = argparse.ArgumentParser(description="수집한 논문 정제")
    parser.add_argument("--keep-math-loss", action="store_true", help="수식이 빠진 초록을 모두 남기고 math_loss 표시를 붙인다(기본은 KEEP_WITH_FLAG의 논문만 남기고 나머지는 제거)")
    args = parser.parse_args()

    kept, removed, seen_titles = [], [], set()
    for paper in load_raw():
        title_key = re.sub(r"\W+", "", paper["title"].lower())
        if title_key in seen_titles:  # arXiv와 OpenAlex에 같은 논문이 있을 때 제목으로 중복 제거
            removed.append({**paper, "removed_reason": "duplicate_title"})
            continue
        seen_titles.add(title_key)
        paper, reason = apply_math_loss_policy(paper, check(paper), keep_all=args.keep_math_loss)
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
