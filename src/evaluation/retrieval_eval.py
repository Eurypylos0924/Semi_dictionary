"""평가 질문 세트(questions.jsonl)로 검색 품질(Hit@K, Recall@K, MRR)을 측정한다.

- 근거 논문(gold_doc_ids)이 있는 질문(answerable=true)만 대상으로 한다.
- Hit@K   : 상위 K개 안에 근거 논문이 하나라도 있는 질문의 비율
- Recall@K: 질문마다 (상위 K개에서 찾은 근거 논문 수 / 전체 근거 논문 수)의 평균
- MRR     : 첫 근거 논문의 순위 역수(1/순위)의 평균. 상위 10개 안에 없으면 0

실행: uv run python -m src.evaluation.retrieval_eval [--save]
"""

import argparse
import json
from collections import defaultdict
from datetime import date
from pathlib import Path

from src.const.config import MIN_RETRIEVAL_SCORE
from src.rag.retriever import search

QUESTIONS_PATH = Path("src/evaluation/questions.jsonl")
RESULTS_DIR = Path("src/evaluation/results")
KS = (1, 3, 5)
MAX_K = 10


def load_questions(path: Path = QUESTIONS_PATH) -> list[dict]:
    with path.open(encoding="utf-8") as f:
        return [json.loads(line) for line in f]


def gate_report(rows: list[dict]) -> list[str]:
    """답이 없는 질문의 검색 1위 점수와, 점수 게이트(MIN_RETRIEVAL_SCORE)가 어떻게 처리하는지 보여준다."""
    lines = ["| id | 종류 | 1위 점수 | 게이트 | 질문 |", "| --- | --- | ---: | --- | --- |"]
    for r in rows:
        blocked = r["top_score"] < MIN_RETRIEVAL_SCORE
        lines.append(f"| {r['id']} | {r['unanswerable_kind']} | {r['top_score']:.3f} | {'차단(근거 없음 응답)' if blocked else '통과(LLM이 거절해야 함)'} | {r['question']} |")
    return lines


def score_question(question: dict, ranked_ids: list[str]) -> dict:
    gold = set(question["gold_doc_ids"])
    ranks = [i + 1 for i, doc_id in enumerate(ranked_ids) if doc_id in gold]
    result = {"first_rank": ranks[0] if ranks else None, "mrr": 1 / ranks[0] if ranks else 0.0}
    for k in KS:
        found = len([r for r in ranks if r <= k])
        result[f"hit@{k}"] = 1.0 if found else 0.0
        result[f"recall@{k}"] = found / len(gold)
    return result


def summarize(rows: list[dict]) -> dict:
    keys = [f"{m}@{k}" for m in ("hit", "recall") for k in KS] + ["mrr"]
    return {key: sum(r[key] for r in rows) / len(rows) for key in keys}


def format_table(title: str, groups: dict[str, list[dict]]) -> str:
    keys = [f"hit@{k}" for k in KS] + [f"recall@{k}" for k in KS] + ["mrr"]
    lines = [f"### {title}", "", "| 구분 | 질문 수 | " + " | ".join(keys) + " |", "| --- | ---: | " + " | ".join("---:" for _ in keys) + " |"]
    for name, rows in groups.items():
        s = summarize(rows)
        lines.append(f"| {name} | {len(rows)} | " + " | ".join(f"{s[k]:.3f}" for k in keys) + " |")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="검색 품질 평가")
    parser.add_argument("--questions", type=Path, default=QUESTIONS_PATH, help="평가 질문 파일(jsonl)")
    parser.add_argument("--save", action="store_true", help="결과를 src/evaluation/results/ 에 markdown으로 저장")
    parser.add_argument("--tag", default="", help="결과 파일 이름에 붙일 구분자 (예: 322docs)")
    args = parser.parse_args()

    questions = load_questions(args.questions)
    scored, unanswerable = [], []
    for q in questions:
        results = search(q["question"], MAX_K)
        if q["answerable"]:
            scored.append({**q, **score_question(q, [p["doc_id"] for p in results]), "top_score": results[0]["score"]})
        else:
            unanswerable.append({**q, "top_score": results[0]["score"]})

    group_key = "topic" if len({r["topic"] for r in scored}) > 1 else "type"
    groups_by: dict[str, list[dict]] = defaultdict(list)
    for r in scored:
        groups_by[r[group_key]].append(r)
    groups = {"전체": scored, **dict(sorted(groups_by.items()))}

    misses = [r for r in scored if r["first_rank"] is None or r["first_rank"] > 5]
    blocked_wrongly = [r for r in scored if r["top_score"] < MIN_RETRIEVAL_SCORE]
    report = [format_table("검색 지표 (근거 논문이 있는 질문)", groups), "", f"### 상위 5위 밖이거나 못 찾은 질문 ({len(misses)}개)", ""]
    for r in misses:
        rank = r["first_rank"] or f">{MAX_K}"
        report.append(f"- {r['id']} [{r[group_key]}] 첫 근거 순위 {rank} (1위 점수 {r['top_score']:.3f}): {r['question']}")
    report += ["", f"### 점수 게이트(0.30)에 잘못 막히는 '답 있는 질문' ({len(blocked_wrongly)}개)", ""]
    report += [f"- {r['id']} 1위 점수 {r['top_score']:.3f}: {r['question']}" for r in blocked_wrongly] or ["- 없음"]
    if unanswerable:
        report += ["", "### 답이 없는 질문의 검색 1위 점수와 게이트 처리", ""] + gate_report(unanswerable)
    text = "\n".join(report)
    print(text)

    if args.save:
        RESULTS_DIR.mkdir(parents=True, exist_ok=True)
        suffix = f"_{args.tag}" if args.tag else ""
        path = RESULTS_DIR / f"retrieval_baseline_{date.today().isoformat()}{suffix}.md"
        header = f"# 검색 기준선 평가 ({date.today().isoformat()})\n\n질문 파일: `{args.questions}`. 임베딩만 사용(NVIDIA nemotron-3-embed-1b, FAISS), 상위 {MAX_K}개 기준.\n\n"
        path.write_text(header + text + "\n", encoding="utf-8")
        print(f"\n저장: {path}")


if __name__ == "__main__":
    main()
