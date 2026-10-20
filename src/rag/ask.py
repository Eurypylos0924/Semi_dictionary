"""질문하면 논문을 근거로 한국어로 답하고 출처를 보여준다.

실행: uv run python -m src.rag.ask "CMP 공정에서 스크래치는 어떻게 줄일 수 있어?" [-k 5]
"""

import argparse

from src.rag.generator import answer
from src.rag.llm import get_llm, resolve
from src.rag.rewrite import search_with_mode


def main() -> None:
    parser = argparse.ArgumentParser(description="논문 근거 QA")
    parser.add_argument("question")
    parser.add_argument("-k", type=int, default=5, help="근거로 검토할 논문 수")
    parser.add_argument("--provider", help="gemini | nvidia | ollama (기본: 환경변수 LLM_PROVIDER 또는 설정값)")
    parser.add_argument("--model", help="모델 이름 (기본: 제공자별 기본 모델)")
    parser.add_argument("--gate-mode", choices=["score", "judge"], help="근거 없음 판단 방식 (기본: 환경변수 GATE_MODE 또는 score)")
    parser.add_argument("--query-mode", choices=["original", "rewrite", "max"], help="검색 방식 (기본: 환경변수 QUERY_MODE 또는 original)")
    args = parser.parse_args()

    provider, model = resolve(args.provider, args.model)
    print(f"[LLM] {provider} / {model}\n")
    search_fn = (lambda q, k: search_with_mode(q, k, mode=args.query_mode)) if args.query_mode else search_with_mode
    result = answer(args.question, k=args.k, llm=get_llm(provider, model), search_fn=search_fn, gate_mode=args.gate_mode)
    if result["verdict"]:
        print(f"[근거 판정] {result['verdict']}: {result['judge_reason']}
")
    print(result["answer"])
    print(f"\n(검색 1위 점수 {result['top_score']:.3f}, LLM 호출 {'함' if result['used_llm'] else '안 함'})")
    if result["invalid_citations"]:
        print(f"경고: 존재하지 않는 논문 번호를 인용함 {result['invalid_citations']}")
    if result["uncited"]:
        print("경고: 답변에 인용 번호가 없음")
    if result["sources"]:
        print("\n출처")
        for p in result["sources"]:
            print(f"- {p['title']} ({p['year']}) {p['source_url']}")


if __name__ == "__main__":
    main()
