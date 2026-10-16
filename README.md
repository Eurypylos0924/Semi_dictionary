# semicon-rag

반도체·디스플레이 박막 공정의 불량 원인과 분석 방법을 묻는 **QA 어시스턴트(RAG)** 를 만들기 위한 개인 프로젝트.
소재공학 전공 지식과 SKN Family AI 캠프에서 배운 RAG·LLM 기술을 결합하는 것이 목표다.

> 현재 단계: **수집 → 정제 → 임베딩 → 검색 → 평가 질문 → 답변 생성(CLI)까지 완료**. 다음은 Streamlit 화면과 답변 품질 평가.

## 파이프라인

```
src/collector/*_collect.py → data/raw/*.jsonl         논문 제목·초록 수집 (OpenAlex, arXiv)
src/preprocessing/clean.py → data/processed/papers.jsonl  무관 논문 제거 (제거 목록은 removed.jsonl에 남김)
src/vectorstore/build.py   → data/index/papers.faiss      "제목+초록" 1건 = 청크 1개로 임베딩 후 FAISS 저장
src/rag/retriever.py       → 질문과 가까운 논문 출력      한국어 질문으로 영어 논문 검색 가능
src/rag/generator.py       → 검색한 논문을 근거로 한국어 답변 + 출처(인용한 논문만)
src/evaluation/            → 평가 질문 27개 + 검색 지표(Hit@K, Recall@K, MRR) 측정
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
│   ├── rag/                     # 검색, 프롬프트, 답변 생성(generator), CLI(ask)
│   ├── evaluation/              # 평가 질문 세트, 검색 지표 측정, 결과(results/)
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
uv run python -m src.rag.ask "Cu CMP 공정에서 스크래치는 어떻게 줄일 수 있어?"      # 논문 근거 답변 + 출처
uv run python -m src.evaluation.retrieval_eval --save                      # 검색 평가
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

## 평가 질문 세트 (`src/evaluation/questions.jsonl`)

| 구분 | 개수 | 설명 |
| --- | ---: | --- |
| 답이 있는 질문 | 22 | 근거 논문(`gold_doc_ids`)과 정답에 들어가야 할 핵심 내용(`expected_points`)을 함께 기록 |
| 수집 빈틈 (`G`) | 2 | 도메인상 중요하지만 코퍼스에 없는 질문 (Scherrer 식, FWHM) |
| 범위 밖 (`U`) | 3 | 코퍼스에 없어서 "찾지 못했다"고 답해야 하는 질문 |

- 질문은 초록을 보고 초안을 작성했고(`reviewed` 전 단계), 근거 논문 ID는 코퍼스와 대조해 검증했다.
- 코퍼스 초록에 `Scherrer`가 **0건**이다. 챗봇이 XRD 기본 용어(Scherrer 식, FWHM)를 못 다루므로 교재·리뷰 논문 수집이 필요하다.

### 기준선 결과 (임베딩만 사용, 22개 질문)

| Hit@1 | Hit@3 | Hit@5 | Recall@5 | MRR |
| ---: | ---: | ---: | ---: | ---: |
| 0.955 | 1.000 | 1.000 | 1.000 | 0.970 |

> **주의: 이 결과는 검색이 잘 된다는 증거로 보기 어렵다.** 질문을 각 논문의 초록을 보고 썼기 때문에 질문 표현이 논문 제목·초록과 거의 겹쳐서, 어떤 검색기든 높게 나오는 쉬운 평가다.
> 검색 방식을 개선했을 때의 차이를 가려내려면, 논문을 보지 않고 실제 QA 엔지니어가 물을 법한 표현으로 쓴 질문(어휘가 겹치지 않거나 모호한 질문)이 필요하다. 상세 결과: `src/evaluation/results/`

## 답변 생성 (`src/rag/generator.py`)

```
질문 → 검색(상위 5) → [점수 게이트] → 프롬프트([1]~[5] 번호 붙인 초록) → LLM → 인용 번호 검증 → 답변 + 출처
```

환각을 두 겹으로 막는다. (팀 프로젝트 CodeClue에서 "근거 없이 답한 답변의 Faithfulness가 0"이었던 약점을 의식한 설계)

1. **점수 게이트**: 검색 1위 점수가 0.30 미만이면 LLM을 부르지 않고 "제공된 논문에서 근거를 찾지 못했습니다"로 답한다.
   평가 질문 기준 범위 밖 질문은 약 0.21, 답 있는 질문은 0.39 이상이었다. **잠정값이며 어려운 질문으로 재점검이 필요하다.**
2. **프롬프트 규칙 + 사후 검증**: 초록에 없는 내용 금지, 문장마다 `[n]` 인용, 질문과 논문의 조건(소재·공정)이 다르면 밝힐 것.
   답변이 인용한 번호가 실제 있는 논문인지 검사하고(`invalid_citations`), 인용이 하나도 없는 답변은 `uncited`로 표시한다. 출처는 **답변이 실제로 인용한 논문만** 보여준다.

### LLM 제공자 (`src/rag/llm.py`)

무료 서비스는 모델이 예고 없이 종료(EOL)되므로, 코드 수정 없이 환경변수로 갈아탈 수 있게 했다: `LLM_PROVIDER=gemini|nvidia|ollama`, `CHAT_MODEL=모델명`(생략하면 제공자 기본 모델).
CLI에서는 `uv run python -m src.rag.ask "질문" --provider ollama --model gemma3:4b`로 바꿔 쓸 수 있다.

| 제공자 | 기본 모델 | 같은 질문(Cu CMP 스크래치) 결과 |
| --- | --- | --- |
| **gemini** (기본) | `gemini-3.1-flash-lite` | **9초**. 인용한 [5]가 산화막 CMP 논문이라 질문 조건과 다르다고 스스로 밝힘. 초록에 없는 과장 없음 |
| gemini | `gemini-3.5-flash` | 36초, 품질은 비슷(조건 차이도 밝힘) |
| nvidia | `nvidia/nemotron-3-super-120b-a12b` | 약 47초. 앞서 기록한 과장 2곳 |
| ollama (로컬 CPU) | `gemma3:4b` | 91초. "근거를 찾지 못했다"고 말한 뒤 근거를 나열하는 모순. 핵심 근거 일부 누락 |
| ollama | `qwen2.5:7b` | 132초. **인용 번호는 유효하지만 내용을 다른 논문에 잘못 연결**(분사 방식을 [5]에 붙임), 용어 깨짐 |

- 질문 1개로 비교한 인상이므로 **모델 우열의 근거로는 약하다**. 근거 충실도(Faithfulness) 평가로 확인해야 한다.
- 로컬 모델은 비상용이다. 느리고 규칙 준수가 불안정하며, 인용 번호 검사만으로는 "번호는 맞는데 내용은 틀린" 경우를 못 잡는다.
- 모델 이름은 자주 바뀐다. 2026-10-16 확인: NVIDIA는 후보 18개 중 1개만 응답(나머지 EOL), Gemini는 2.5 계열이 종료되고 3.x 계열이 응답.
  Gemini 무료 등급의 한도는 출처마다 설명이 달라 [AI Studio](https://aistudio.google.com)에서 직접 확인해야 한다. 무료 등급에서는 입력이 모델 개선에 쓰일 수 있으므로 비공개 자료는 넣지 않는다.
- 필요한 키: `GOOGLE_API_KEY`(gemini), `nvidiaapi_key`(nvidia, 임베딩에도 사용), ollama는 키 불필요. `.env.example` 참고.

### 수동 확인 결과 (질문 4개, 초록과 대조)

| 질문 | 결과 | 평가 |
| --- | --- | --- |
| Cu CMP에서 스크래치를 줄이는 방법 | 분산제(EDA), 여과·물 분사, 입자 크기 등 인용 5건 | **대체로 충실하나 과장 2곳**: 질문은 Cu CMP인데 인용한 [5]는 산화막 CMP 슬러리 논문이고, "유량 증가가 스크래치를 줄인다"는 초록에 없음(초록은 디싱·침식만 언급). 프롬프트에 두 규칙을 추가했지만 재실행에서도 같은 과장이 남음 |
| EUV 펠리클 재료 | 점수 0.216 → LLM 호출 없이 "근거 없음" | 의도대로 동작 |
| CMP 후 Idsat 저하 원인 | 점수 0.226 → "근거 없음" | 코퍼스에 없는 내용이라 정직하게 거절. 현업 표현 질문에 답하려면 코퍼스 보강 필요 |
| SiC 게이트 산화막 신뢰성 | 점수 0.374로 게이트 통과, 4H-SiC MOS 논문 한 편을 근거로 답변 | 답은 초록에 근거하지만 ZrO2 적층 연구 한 편을 "SiC 소자 신뢰성 전반"으로 **일반화**함. 또한 이 질문은 코퍼스가 커지며 더 이상 범위 밖이 아님 |

- 시사점: **프롬프트만으로는 인용 번호가 맞아도 내용이 약간 부풀려지는 것을 막지 못한다.** 그래서 다음 단계에서 답변의 근거 충실도(Faithfulness)를 따로 측정해야 한다.
- 범위 밖 평가 질문은 코퍼스가 바뀌면 범위 안이 될 수 있다. 코퍼스를 바꿀 때마다 `U` 질문을 다시 확인한다.

## 다음 단계

1. **더 어려운 평가 질문 추가**: 논문을 보지 않고 현업 표현으로 쓴 질문, 근거가 여러 논문에 걸친 질문 (도메인 지식으로 직접 검수)
2. 답변 근거 충실도(Faithfulness) 평가: 답변의 주장이 인용한 초록에 있는지 채점
3. 하이브리드 검색(BM25 + 임베딩)·재정렬 적용 후 지표 비교, Streamlit 화면
