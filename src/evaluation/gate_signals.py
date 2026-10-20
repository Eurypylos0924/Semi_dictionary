"""'근거가 있는 질문'과 '근거가 없는 질문'을 가르는 검색 점수 신호를 비교한다.

현재 점수 게이트는 검색 1위 점수(top1) 하나가 0.30 미만이면 거절한다. 현업 표현 질문에서는 답 있는 질문도 막혀서,
점수 하나 대신 상대 신호(1위와 5위의 차이, 코퍼스 전체 점수 분포 대비 편차 등)가 더 잘 가르는지 실험한다. LLM 호출은 없다.

- AUC: 답 있는 질문의 신호가 답 없는 질문보다 클 확률. 1.0이면 완벽히 분리, 0.5면 무작위.
- 교차 검증: 한 질문 세트에서 임계값을 정해 다른 세트에 적용한다(같은 세트로 정하고 재면 과적합이므로).

실행: uv run python -m src.evaluation.gate_signals [--save]
"""

import argparse
import json
import statistics
from datetime import date
from pathlib import Path

import faiss
import numpy as np

from src.const.config import FAISS_PATH, MIN_RETRIEVAL_SCORE
from src.evaluation.retrieval_eval import RESULTS_DIR, load_questions
from src.vectorstore.embedder import get_embeddings, normalize

SETS = {
    "초록 기반": Path("src/evaluation/questions.jsonl"),
    "현업 표현": Path("src/evaluation/questions_field.jsonl"),
}


def compute_signals(scores: np.ndarray) -> dict[str, float]:
    """한 질문의 코퍼스 전체 유사도(내림차순)에서 신호를 뽑는다."""
    mean_all, std_all = float(scores.mean()), float(scores.std())
    top5 = scores[:5]
    return {
        "top1 (현재 게이트)": float(scores[0]),
        "1위-2위 차이": float(scores[0] - scores[1]),
        "1위-5위 차이": float(scores[0] - scores[4]),
        "상위5 평균": float(top5.mean()),
        "z(1위)": (float(scores[0]) - mean_all) / std_all,
        "z(상위5 평균)": (float(top5.mean()) - mean_all) / std_all,
    }


def auc(positives: list[float], negatives: list[float]) -> float:
    wins = sum((p > n) + 0.5 * (p == n) for p in positives for n in negatives)
    return wins / (len(positives) * len(negatives))


def best_threshold(positives: list[float], negatives: list[float]) -> float:
    """Youden J(민감도+특이도-1)가 최대인 임계값(신호 >= 임계값이면 통과). 동률이면 답 있는 질문을 더 통과시키는 쪽."""
    values = sorted(set(positives + negatives))
    candidates = [values[0] - 1e-9] + [(a + b) / 2 for a, b in zip(values, values[1:])] + [values[-1] + 1e-9]
    best = max(
        candidates,
        key=lambda t: (
            sum(p >= t for p in positives) / len(positives) + sum(n < t for n in negatives) / len(negatives),
            sum(p >= t for p in positives),
        ),
    )
    return best


def rates(threshold: float, positives: list[float], negatives: list[float]) -> tuple[float, float]:
    """(답 있는 질문을 거절한 비율, 답 없는 질문을 통과시킨 비율)"""
    return (
        sum(p < threshold for p in positives) / len(positives),
        sum(n >= threshold for n in negatives) / len(negatives),
    )


def collect() -> dict[str, dict[str, dict[str, list[float]]]]:
    """세트별로 {신호 이름: {'answerable': [...], 'unanswerable': [...]}} 를 만든다."""
    index = faiss.read_index(str(FAISS_PATH))
    embeddings = get_embeddings()
    out: dict[str, dict] = {}
    for set_name, path in SETS.items():
        per_signal: dict[str, dict[str, list[float]]] = {}
        for q in load_questions(path):
            vec = normalize([embeddings.embed_query(q["question"])])
            scores, _ = index.search(vec, index.ntotal)
            for name, value in compute_signals(scores[0]).items():
                per_signal.setdefault(name, {"answerable": [], "unanswerable": []})["answerable" if q["answerable"] else "unanswerable"].append(value)
        out[set_name] = per_signal
    return out


def build_report(data: dict) -> str:
    set_names = list(SETS)
    signals = list(data[set_names[0]])
    lines = ["### 신호별 분리력 (AUC: 1.0 완벽, 0.5 무작위)", "", "| 신호 | " + " | ".join(f"{s}" for s in set_names) + " | 두 세트 합친 값 |", "| --- | " + " | ".join("---:" for _ in set_names) + " | ---: |"]
    for sig in signals:
        cells = [f"{auc(data[s][sig]['answerable'], data[s][sig]['unanswerable']):.3f}" for s in set_names]
        pooled_pos = sum((data[s][sig]["answerable"] for s in set_names), [])
        pooled_neg = sum((data[s][sig]["unanswerable"] for s in set_names), [])
        lines.append(f"| {sig} | " + " | ".join(cells) + f" | {auc(pooled_pos, pooled_neg):.3f} |")
    n_info = " · ".join(f"{s}: 답 있음 {len(data[s][signals[0]]['answerable'])}, 답 없음 {len(data[s][signals[0]]['unanswerable'])}" for s in set_names)
    lines += ["", f"(질문 수 — {n_info})", "", "### 교차 검증: 한 세트에서 임계값을 정해 다른 세트에 적용", "",
              "| 신호 | 정한 세트 → 적용한 세트 | 임계값 | 답 있는 질문을 거절 | 답 없는 질문을 통과 |", "| --- | --- | ---: | ---: | ---: |"]
    for sig in signals:
        for fit, test in ((set_names[0], set_names[1]), (set_names[1], set_names[0])):
            t = best_threshold(data[fit][sig]["answerable"], data[fit][sig]["unanswerable"])
            refused, passed = rates(t, data[test][sig]["answerable"], data[test][sig]["unanswerable"])
            lines.append(f"| {sig} | {fit} → {test} | {t:.3f} | {refused:.0%} | {passed:.0%} |")
    lines += ["", "### 현재 게이트(top1 < %.2f 거절)가 각 세트에서 하는 일" % MIN_RETRIEVAL_SCORE, "", "| 세트 | 답 있는 질문을 거절 | 답 없는 질문을 통과 |", "| --- | ---: | ---: |"]
    for s in set_names:
        refused, passed = rates(MIN_RETRIEVAL_SCORE, data[s]["top1 (현재 게이트)"]["answerable"], data[s]["top1 (현재 게이트)"]["unanswerable"])
        lines.append(f"| {s} | {refused:.0%} | {passed:.0%} |")
    lines += ["", "### 신호 분포 (중앙값)", "", "| 신호 | 세트 | 답 있는 질문 | 답 없는 질문 |", "| --- | --- | ---: | ---: |"]
    for sig in signals:
        for s in set_names:
            lines.append(f"| {sig} | {s} | {statistics.median(data[s][sig]['answerable']):.3f} | {statistics.median(data[s][sig]['unanswerable']):.3f} |")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="점수 게이트 신호 비교 실험")
    parser.add_argument("--save", action="store_true", help="결과를 src/evaluation/results/ 에 저장")
    args = parser.parse_args()

    text = build_report(collect())
    print(text)
    if args.save:
        RESULTS_DIR.mkdir(parents=True, exist_ok=True)
        path = RESULTS_DIR / f"gate_signals_{date.today().isoformat()}.md"
        path.write_text(f"# 점수 게이트 신호 비교 ({date.today().isoformat()})\n\n임베딩 점수만 사용, LLM 호출 없음. 코퍼스 322건.\n\n{text}\n", encoding="utf-8")
        print(f"\n저장: {path}")


if __name__ == "__main__":
    main()
