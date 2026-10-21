"""쿼리 재작성 방식(original | rewrite | max)을 두 질문 세트에서 비교한다 (docs/rag.md '쿼리 재작성 실험').

검색 지표(Hit@K, Recall@5, MRR)와 점수 게이트 관점(답 있는 질문 거절 수, 답 없는 질문 통과 수, AUC)을 출력한다.
재작성에 LLM(Gemini)을 쓰며 결과는 data/cache/rewrites.jsonl 에 캐시된다.

실행: uv run python -m src.evaluation.ablation_rewrite
"""

import sys
import os, sys, statistics
from pathlib import Path
from src.const.config import MIN_RETRIEVAL_SCORE
from src.evaluation.gate_signals import auc
from src.evaluation.retrieval_eval import load_questions, score_question, summarize
from src.rag.rewrite import search_with_mode, rewrite_query

SETS = {"초록 기반": Path("src/evaluation/questions.jsonl"), "현업 표현": Path("src/evaluation/questions_field.jsonl")}
MODES = ["original", "rewrite", "max"]


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    print("## 재작성 결과 (현업 표현 세트 전체 + 초록 기반 일부)")
    for name, path in SETS.items():
        qs = load_questions(path)
        for q in (qs if name == "현업 표현" else qs[:6] + qs[-3:]):
            print(f"[{q['id']}] {q['question']}\n      -> {rewrite_query(q['question'])}")
    for name, path in SETS.items():
        for q in load_questions(path):
            rewrite_query(q["question"])  # 나머지도 모두 캐시

    res = {}
    for name, path in SETS.items():
        qs = load_questions(path)
        for mode in MODES:
            rows, tops = [], {"answerable": [], "unanswerable": []}
            detail = {}
            for q in qs:
                results = search_with_mode(q["question"], 10, mode)
                top = results[0]["score"]
                detail[q["id"]] = top
                if q["answerable"]:
                    rows.append({**score_question(q, [p["doc_id"] for p in results])})
                    tops["answerable"].append(top)
                else:
                    tops["unanswerable"].append(top)
            res[(name, mode)] = (summarize(rows), tops, detail)

    print("\n## 검색 지표")
    print("| 세트 | 방식 | 질문 수 | Hit@1 | Hit@3 | Hit@5 | Recall@5 | MRR |")
    print("| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |")
    for name in SETS:
        for mode in MODES:
            s, tops, _ = res[(name, mode)]
            print(f"| {name} | {mode} | {len(tops['answerable'])} | {s['hit@1']:.3f} | {s['hit@3']:.3f} | {s['hit@5']:.3f} | {s['recall@5']:.3f} | {s['mrr']:.3f} |")

    print("\n## 점수 게이트 관점 (top1 점수, 게이트 %.2f)" % MIN_RETRIEVAL_SCORE)
    print("| 세트 | 방식 | 답 있는 질문 중앙값 | 답 없는 질문 중앙값 | AUC | 답 있는 질문 거절 | 답 없는 질문 통과 |")
    print("| --- | --- | ---: | ---: | ---: | ---: | ---: |")
    for name in SETS:
        for mode in MODES:
            _, tops, _ = res[(name, mode)]
            a, u = tops["answerable"], tops["unanswerable"]
            print(f"| {name} | {mode} | {statistics.median(a):.3f} | {statistics.median(u):.3f} | {auc(a, u):.3f} | {sum(x < MIN_RETRIEVAL_SCORE for x in a)}/{len(a)} | {sum(x >= MIN_RETRIEVAL_SCORE for x in u)}/{len(u)} |")

    print("\n## 현업 표현 세트의 질문별 top1 점수 (원문 / 재작성 / max)")
    field = load_questions(SETS["현업 표현"])
    for q in field:
        d = [res[("현업 표현", m)][2][q["id"]] for m in MODES]
        tag = "답 있음" if q["answerable"] else q.get("unanswerable_kind", "")
        print(f"{q['id']} [{tag}] {d[0]:.3f} / {d[1]:.3f} / {d[2]:.3f}  {q['question'][:40]}")


if __name__ == "__main__":
    main()
