"""점수 게이트와 LLM 근거 판정 게이트를 두 질문 세트·두 검색 방식에서 비교한다 (docs/rag.md 'LLM 근거 판정').

답 있는 질문을 거절한 수, 답 없는 질문을 통과시킨 수, 판정 분포, 판정이 정답 논문을 얼마나 남기는지를 출력한다.
판정에 LLM(Gemini)을 쓰며 결과는 data/cache/judgements.jsonl 에 캐시된다.

실행: uv run python -m src.evaluation.ablation_judge
"""

import sys
from collections import Counter
from pathlib import Path
from src.const.config import MIN_RETRIEVAL_SCORE
from src.evaluation.retrieval_eval import load_questions
from src.rag.judge import judge, HARD_FLOOR
from src.rag.rewrite import search_with_mode

SETS = {"초록 기반": Path("src/evaluation/questions.jsonl"), "현업 표현": Path("src/evaluation/questions_field.jsonl")}
RETRIEVAL_MODES = ["original", "max"]


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    rec = {}
    for name, path in SETS.items():
        for q in load_questions(path):
            for mode in RETRIEVAL_MODES:
                papers = search_with_mode(q["question"], 5, mode)
                top = papers[0]["score"]
                if top < HARD_FLOOR:
                    j, floor_blocked = None, True
                else:
                    j, floor_blocked = judge(q["question"], papers), False
                gold = set(q["gold_doc_ids"]); ids = [p["doc_id"] for p in papers]
                kept = {ids[n - 1] for n in j.relevant} if j else set()
                rec[(name, mode, q["id"])] = dict(q=q, top=top, floor=floor_blocked, j=j, gold_in_top5=len(gold & set(ids)), gold_kept=len(gold & kept))

    print("## 게이트 비교 (답 있는 질문을 거절한 수 / 답 없는 질문을 통과시킨 수)")
    print("| 세트 | 검색 방식 | 점수 게이트(0.30) 거절 | 점수 게이트 통과 | LLM 판정 거절 | LLM 판정 통과 |")
    print("| --- | --- | ---: | ---: | ---: | ---: |")
    for name in SETS:
        for mode in RETRIEVAL_MODES:
            rows = [r for (n, m, _), r in rec.items() if n == name and m == mode]
            A = [r for r in rows if r["q"]["answerable"]]; U = [r for r in rows if not r["q"]["answerable"]]
            score_ref = sum(r["top"] < MIN_RETRIEVAL_SCORE for r in A); score_pass = sum(r["top"] >= MIN_RETRIEVAL_SCORE for r in U)
            refused = lambda r: r["floor"] or (r["j"] is not None and r["j"].verdict == "none")
            print(f"| {name} | {mode} | {score_ref}/{len(A)} | {score_pass}/{len(U)} | {sum(refused(r) for r in A)}/{len(A)} | {sum(not refused(r) for r in U)}/{len(U)} |")

    print("\n## 판정 분포")
    for name in SETS:
        for mode in RETRIEVAL_MODES:
            rows = [r for (n, m, _), r in rec.items() if n == name and m == mode]
            for label, sel in (("답 있음", [r for r in rows if r["q"]["answerable"]]), ("답 없음", [r for r in rows if not r["q"]["answerable"]])):
                c = Counter("하한선 차단" if r["floor"] else (r["j"].verdict if r["j"] else "형식오류") for r in sel)
                print(f"{name} / {mode} / {label}: {dict(c)}")

    print("\n## 답 있는 질문인데 LLM 판정이 거절한 경우")
    for (n, m, qid), r in rec.items():
        if r["q"]["answerable"] and (r["floor"] or (r["j"] and r["j"].verdict == "none")):
            print(f"[{n}/{m}] {qid} top1 {r['top']:.3f} {'(하한선)' if r['floor'] else '-> ' + r['j'].reason}\n     {r['q']['question'][:60]}")
    print("\n## 답 없는 질문인데 LLM 판정이 통과시킨 경우")
    for (n, m, qid), r in rec.items():
        if not r["q"]["answerable"] and not (r["floor"] or (r["j"] and r["j"].verdict == "none")):
            print(f"[{n}/{m}] {qid} top1 {r['top']:.3f} 판정 {r['j'].verdict if r['j'] else '형식오류'}: {r['j'].reason if r['j'] else ''}\n     {r['q']['question'][:60]}")

    print("\n## 판정이 근거 논문을 얼마나 남기는가 (상위5 안에 있는 정답 논문 중 판정이 고른 비율)")
    for name in SETS:
        for mode in RETRIEVAL_MODES:
            rows = [r for (n, m, _), r in rec.items() if n == name and m == mode and r["q"]["answerable"] and not r["floor"] and r["j"]]
            have = sum(r["gold_in_top5"] for r in rows); kept = sum(r["gold_kept"] for r in rows)
            print(f"{name} / {mode}: 상위5 안 정답 {have}편 중 판정이 선택 {kept}편 ({kept / have:.0%})" if have else f"{name} / {mode}: -")

    print("\n## 현업 표현 세트 질문별 판정 (original 검색)")
    for q in load_questions(SETS["현업 표현"]):
        r = rec[("현업 표현", "original", q["id"])]
        tag = "답 있음" if q["answerable"] else q.get("unanswerable_kind")
        v = "하한선 차단" if r["floor"] else (r["j"].verdict if r["j"] else "형식오류")
        sel = f" 선택 {r['j'].relevant}" if r["j"] and r["j"].verdict != "none" else ""
        print(f"{q['id']} [{tag}] top1 {r['top']:.3f} -> {v}{sel}  {q['question'][:34]}")


if __name__ == "__main__":
    main()
