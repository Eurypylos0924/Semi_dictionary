# semicon-rag

반도체·디스플레이 박막 공정의 불량 원인과 분석 방법을 묻는 **QA 어시스턴트(RAG)** 를 만들기 위한 개인 프로젝트.
소재공학 전공 지식과 SKN Family AI 캠프에서 배운 RAG·LLM 기술을 결합하는 것이 목표다.

> 현재 단계: **수집 → 정제 → 임베딩 → 검색 테스트까지 완료**. 다음은 평가 질문 세트와 검색 품질 개선.

## 파이프라인

```
src/collector/*_collect.py → data/raw/*.jsonl         논문 제목·초록 수집 (OpenAlex, arXiv)
src/preprocessing/clean.py → data/processed/papers.jsonl  무관 논문 제거 (제거 목록은 removed.jsonl에 남김)
src/vectorstore/build.py   → data/index/papers.faiss      "제목+초록" 1건 = 청크 1개로 임베딩 후 FAISS 저장
src/rag/retriever.py       → 질문과 가까운 논문 출력      한국어 질문으로 영어 논문 검색 가능
```

- 임베딩: NVIDIA `nemotron-3-embed-1b` (2048차원, 무료 API). 키는 `.env`의 `nvidiaapi_key`에 둔다.
- 벡터 DB: 로컬 FAISS (`IndexFlatIP` + 정규화 벡터 = 코사인 유사도). 논문 206건 규모라 정확 검색으로 충분하다.

## 수집 데이터

논문 제목과 초록만 수집한다 (본문 PDF는 저작권·용량 문제로 제외). 모든 주제는 `TOPICS`에서 바꿀 수 있다.

| 주제 | 내용 |
| --- | --- |
| `hfo2_ald` | HfO2 박막의 원자층 증착 |
| `high_k_leakage` | 고유전율 소재의 누설전류 |
| `xrd_thin_film` | 박막 XRD 결정성·결정립 크기 분석 |
| `cmp_defect` | CMP 공정 결함 |
| `wafer_defect` | 웨이퍼 맵 결함 패턴 |
| `yield_process` | 공정 수율·근본 원인 분석 |

| 수집기 | 출처 | 상태 |
| --- | --- | --- |
| `src/collector/openalex_collect.py` | OpenAlex 공식 API (학술지 포함) | 사용 중 — 239건 수집 |
| `src/collector/arxiv_collect.py` | arXiv 공식 API | 이 네트워크 IP에서 429(rate limit)로 수집 실패, 네트워크가 바뀌면 재시도 |

## 디렉토리 구조

```text
semicon-rag
├── pyproject.toml / uv.lock     # 의존성 (uv)
├── .env.example                 # 환경변수 이름 (실제 키는 .env, git 제외)
├── src
│   ├── collector/               # 논문 수집 (OpenAlex, arXiv)
│   ├── preprocessing/           # 무관 논문 제거
│   ├── vectorstore/             # 임베딩, FAISS 인덱스 구축
│   ├── rag/                     # 검색 (이후 답변 생성 단계 추가)
│   └── const/                   # 경로·모델 설정
├── tests/                       # collector · preprocessing · vectorstore 테스트
├── data/                        # raw → processed → index (git 제외)
└── docs/                        # 설계·평가 문서 (예정)
```

## 실행

```bash
uv sync
cp .env.example .env                                                  # nvidiaapi_key 값 채우기
uv run python -m src.collector.openalex_collect --max-per-query 40            # 최초 수집
uv run python -m src.collector.openalex_collect --max-per-query 40 --refresh  # 새 논문만 추가
uv run python -m src.preprocessing.clean                                                # 정제 (239건 -> 206건)
uv run python -m src.vectorstore.build                                                # 인덱스 구축 (--rebuild로 재구축)
uv run python -m src.rag.retriever "CMP 공정에서 스크래치 결함이 생기는 메커니즘" -k 3
uv run pytest                                                             # 테스트
```

- 논문은 거의 바뀌지 않으므로 결과 파일(`data/raw/*.jsonl`)이 있으면 수집을 건너뛴다.
- `--refresh`는 기존 논문을 그대로 두고 새 논문만 합친다 (재실행해도 중복이 쌓이지 않음).
- `data/`는 git에 올리지 않는다 (`.gitignore`).

## 알려진 한계

- 주제와 무관한 논문이 일부 섞인다 (예: 유기 고분자 유전체, 프탈로시아닌 박막). 검색어 정교화나 필터가 필요하다.
- HfO2 ALD 주제는 관련도순 상위가 2000년대 초반 논문 위주라, 연도 필터나 인용 수 기준 보완이 필요하다.
- 초록만 사용하므로 수치·실험 조건이 필요한 질문에는 근거가 부족할 수 있다.

## 검색 테스트 관찰 (2026-10-16, 질문 3개 수동 확인)

- CMP 스크래치 메커니즘, 웨이퍼맵 딥러닝 분류: 상위 3건이 모두 질문과 직접 관련된 논문이었다.
- "HfO2 박막에서 누설전류가 커지는 원인은?": 상위 3건이 증착 방법 논문이고, 누설전류 원인을 다룬 논문은 없었다.
  코퍼스에 HfO2 **누설전류 메커니즘** 논문이 부족한 것으로 보이며, 검색 모델보다 **수집 검색어의 문제**일 가능성이 크다.

## 다음 단계

1. 평가 질문 세트(질문 + 근거 논문) 15~20개를 도메인 지식으로 직접 작성하고 Hit@K, MRR 측정
2. 부족한 주제(HfO2 누설전류 메커니즘 등)의 수집 검색어 보강
3. 하이브리드 검색(BM25 + 임베딩)과 재정렬 적용 후 지표 비교
4. 검색 결과를 근거로 답변하는 LLM 단계(출처 표시 포함)
