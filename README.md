# semicon-rag

반도체·디스플레이 박막 공정의 불량 원인과 분석 방법을 묻는 **논문 근거 QA 챗봇(RAG)** 을 만드는 개인 프로젝트.
소재공학 전공 지식과 SKN Family AI 캠프에서 배운 RAG·LLM 기술을 결합하는 것이 목표다.
질문하면 검색한 논문 초록을 근거로 한국어로 답하고, 답변이 인용한 논문만 출처로 보여준다.

> 현재 단계: **수집 → 정제 → 임베딩 → 검색 → 평가 질문 → 답변 생성 → 답변 근거 충실도 평가까지 완료**하고, 측정 결과로 검색·게이트·답변 길이의 기본값을 정했다. Streamlit 챗봇 화면을 붙이는 중이다.

## 파이프라인

```
수집      src/collector/      OpenAlex·arXiv 논문 제목·초록 수집          → data/raw/*.jsonl
정제      src/preprocessing/  무관·수식 누락 논문 제거 (356건 → 314건)  → data/processed/papers.jsonl
벡터저장  src/vectorstore/    "제목+초록"을 임베딩해 FAISS에 저장        → data/index/
검색·답변 src/rag/            검색(원문+영어 재작성) → LLM 근거 판정 → 답변 → 인용 검증 → 답변 + 출처
화면      src/app/            Streamlit 챗봇 화면(답변·판정·출처 표시)
평가      src/evaluation/     평가 질문 50개(초록 기반 30 + 현업 표현 20), Hit@K·Recall@K·MRR, 답변 근거 충실도
```

| 영역 | 상세 문서 |
| --- | --- |
| 수집 (주제, 수집기, 한계) | [docs/collector.md](docs/collector.md) |
| 정제 (제거 규칙, 시행착오) | [docs/preprocessing.md](docs/preprocessing.md) |
| 벡터 저장소 (임베딩, FAISS 설계) | [docs/vectorstore.md](docs/vectorstore.md) |
| 검색·답변 (쿼리 재작성, 근거 판정, 기본값 변경 이유, LLM 제공자) | [docs/rag.md](docs/rag.md) |
| 평가 (질문 세트, 기준선, 충실도, 실험 결과, 평가의 한계) | [docs/evaluation.md](docs/evaluation.md) |
| 화면 (Streamlit 챗봇) | [docs/app.md](docs/app.md) |
| 협업 방식 (영역별 브랜치, PR 규칙) | [docs/workflow.md](docs/workflow.md) |

## 디렉토리 구조

```text
semicon-rag
├── pyproject.toml / uv.lock     # 의존성 (uv)
├── .env.example                 # 환경변수 이름 (실제 키는 .env, git 제외)
├── src
│   ├── collector/               # 논문 수집 (OpenAlex, arXiv)
│   ├── preprocessing/           # 무관 논문 제거
│   ├── vectorstore/             # 임베딩, FAISS 인덱스 구축
│   ├── rag/                     # 검색, 프롬프트, LLM 제공자, 답변 생성, CLI
│   ├── evaluation/              # 평가 질문 세트, 검색 지표·충실도 측정, 결과(results/)
│   ├── app/                     # Streamlit 챗봇 화면
│   └── const/                   # 경로·모델 설정
├── tests/                       # 영역별 테스트
├── data/                        # raw → processed → index (git 제외)
├── docs/                        # 영역별 상세 문서
└── .github/                     # PR 템플릿
```

## 빠른 시작

```bash
uv sync
cp .env.example .env     # nvidiaapi_key(임베딩), GOOGLE_API_KEY(답변 생성) 채우기
uv run python -m src.collector.openalex_collect --max-per-query 40   # 수집
uv run python -m src.preprocessing.clean                              # 정제
uv run python -m src.vectorstore.build                                # 인덱스 구축
uv run python -m src.rag.ask "Cu CMP 공정에서 스크래치는 어떻게 줄일 수 있어?"   # 논문 근거 답변 + 출처 (CLI)
uv run streamlit run src/app/main.py                                  # 챗봇 화면
uv run python -m src.evaluation.retrieval_eval --save                 # 검색 평가
uv run python -m src.evaluation.faithfulness --configs baseline --sets field --save   # 답변 근거 충실도 평가(채점 LLM 호출, 오래 걸림)
uv run pytest                                                         # 테스트
```

## 알려진 한계

- 초록 기반 질문 30개는 초록을 보고 써서 **쉬운 평가**다(Hit@5 약 1.0). 논문을 보지 않고 쓴 현업 표현 질문 14개(답이 있는 질문)에서는 Hit@5 0.93, 정답 논문을 모두 찾는 Recall@5는 0.61이다. 질문 수가 적어 질문 하나가 지표를 크게 흔든다. ([평가 문서](docs/evaluation.md))
- 기본 파이프라인(`max` 검색 + `judge` 게이트, 답변 길이 제한 해제)에서 현업 표현 질문 14개 중 2개를 거절하고(F14, F15; 정답 메모상 부분 답변 질문), 답한 질문의 충실도는 98.4%(주장 기준, 채점자도 LLM), 핵심 내용 포함 비율(완결성)은 50.6%다. 이 수치들은 질문이 적고 한 번 측정한 것이라 우연의 영향이 있을 수 있다. 근거 없는 수치 환각 1건은 원인이 데이터(OpenAlex가 초록의 수식·수치를 지움)였고 정제와 프롬프트로 막았지만 확인은 한 질문뿐이다. 답변이 길어졌고 인용 번호만 틀린 주장이 1~2% 생겼다. ([평가 문서](docs/evaluation.md), [rag 문서](docs/rag.md))
- 초록만 사용하므로 수치·실험 조건이 필요한 질문에는 근거가 부족하고, 코퍼스에 없는 현업 표현 질문(예: CMP 후 Idsat 저하)은 답하지 못한다.

## 다음 단계

1. 충실도 검수용 표본을 사람이 확인 (지금까지 채점은 LLM이 했다)
2. 직접 쓴 현업 표현 질문 5~10개 추가 (지금 14개로는 지표가 질문 하나에 크게 흔들린다)
3. 인용 번호만 틀린 주장 줄이기
4. 하이브리드 검색(BM25 + 임베딩)·재정렬: Recall@5 0.56~0.61이 완결성의 상한이지만, 거절의 주된 원인은 검색이 아니었다(`docs/rag.md`)
