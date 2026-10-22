# 정제 (preprocessing)

> 담당 브랜치: `preprocessing_branch` · 담당 파일: `src/preprocessing/`, `tests/test_clean.py`
> 이 문서는 해당 영역의 PR에서만 수정한다 ([협업 방식](workflow.md)).

수집한 논문(`data/raw/*.jsonl`)에서 주제와 무관한 논문과 **수식이 빠진 초록**을 걸러 `data/processed/papers.jsonl`을 만든다. 현재 356건 → 314건(주제 무관·중복 34건, 수식 누락 8건 제거, 수식 누락 1건은 `math_loss` 표시를 붙여 유지).

```bash
uv run python -m src.preprocessing.clean                    # 정제
uv run python -m src.preprocessing.clean --keep-math-loss   # 수식이 빠진 초록을 모두 남기고 표시를 붙임(비교 실험용)
```

## 규칙 (`src/preprocessing/clean.py`)

| 규칙 | 내용 |
| --- | --- |
| `REQUIRE` | 논문이 속한 주제마다 "제목+초록에 하나라도 있어야 하는 단어". 해당 주제의 단어가 하나도 없으면 제거 (예: 수율 주제에 걸린 일반 제조업 AI 논문) |
| `EXCLUDE` | 초록 어디에 나와도 제거하는 단어 (phthalocyanine, elastomer, inkjet 등 반도체 공정과 먼 소재·분야) |
| `EXCLUDE_TITLE` | **제목에 있을 때만** 제거하는 단어 (polymer, nanocomposite, epoxy 등) |
| 제목 중복 | arXiv와 OpenAlex에 같은 논문이 있을 때 제목으로 중복 제거 |
| `MATH_LOSS_PATTERNS` | 수식·수치가 빠진 초록의 흔적 8종 (아래 참고) |
| `KEEP_WITH_FLAG` | 수식이 빠졌지만 사람이 검토해 **남기되 표시**하기로 한 논문 목록. 남긴 논문에는 `math_loss` 필드(걸린 신호)가 붙는다 |

- 제거한 논문은 이유(어떤 규칙, 수식 누락이면 어떤 신호)와 함께 `data/processed/removed.jsonl`에 남겨 사람이 검토할 수 있다.

## 수식 누락 초록 제거 (2026-10-21)

**배경**: 답변 근거 충실도 측정(`docs/evaluation.md`)에서 진짜 환각이 1건 나왔다. 근거 초록에 `pulse times of must be applied to achieve saturation`처럼 **값이 통째로 빠져 있었고**, 모델이 그 빈자리를 "0.5초 이상"으로 지어냈다. OpenAlex가 초록에서 수식·수치(LaTeX)를 제거해서 생긴 문제다. 데이터가 환각을 부른 사례라 입력 데이터에서 걸러낸다.

**탐지**: 값이 있어야 할 자리가 비어 문장이 어색해진 형태를 정규식 8종으로 찾는다.

| 신호 | 예(실제 초록) |
| --- | --- |
| 전치사·비교어 뒤가 비어 있음 | `ranging from room temperature to .`, `lower than , high ratio` |
| of 뒤 and, from/to/at/of 뒤 for | `a dielectric constant of and a capacitive`, `from for conventional ALD to for` |
| 빈 괄호 | `iridium oxide () thin films` |
| sub-, high- 같은 접두어 뒤가 비어 있음 | `(high- dielectrics and metal gates)`, `sub- devices` |
| 전치사 뒤 조동사 | `pulse times of must be applied`, `thin films of were prepared` |
| 단위만 남음 | `a breakdown field of MV/cm`, `A/cm 2 is achieved` |
| 쉼표·and 뒤 닫는 괄호 | `(thermally grown , HF-cleaned Ge, and )` |
| 글자 깨짐(마침표 뒤 소문자) | `was conf irmed . tant high permittivity` |

- **만든 방법**: 코퍼스 322건을 의심 패턴별로 훑어 걸린 논문을 모두 직접 읽었다. 처음 시도한 패턴 중 `단위만 남음`은 대소문자 무시 때문에 109건이 걸리는 버그였고, `than for ...`(정상적인 비교 문법) 2건은 오탐이어서 뺐다. 정상 문장(`than for`, `up to and including`, `high- and low-resistance`, 아래첨자 사이 공백 `HfO 2 ,`)이 걸리지 않는 것을 테스트로 고정했다.
- **약한 신호(쉼표 앞 공백 등)는 쓰지 않았다.** 걸린 것이 거의 `HfO 2 ,` 같은 정상 아래첨자 표기였다.

**결과**: 9건(2.8%)이 걸렸고 모두 사람이 확인한 진짜 누락이다(8건은 값 누락, 1건은 글자 깨짐). 이 중 **8건은 제거**하고, 환각의 원인이었던 W2076838934 **1건은 표시하고 남겼다**(아래 결정 참고).

| 논문 | 걸린 신호 |
| --- | --- |
| W2076838934 Scaling to Sub-1 nm EOT HfO2 (2006) | 값 누락 4종 (**환각의 원인 논문, 표시하고 유지**) |
| W2162048190 ALD of HfO2 using hafnium nitrate (2002) | of 뒤 and |
| W2086785967 ALD of HfO2 on Ge and GaAs (2008) | 접두어 뒤, 닫는 괄호 |
| W2076784031 Two-step deposition for high-k HfO2 (2001) | 단위만 남음 |
| W2189512959 Epitaxial (Ba,Sr)TiO3 capacitors (1997) | 글자 깨짐 |
| W1972616022 Bismuth selenide thin films (1997) | 전치사 뒤 비어 있음, for |
| W1983265524 Electrical properties of thin films (1998) | for, 조동사 |
| W2030331744 Iridium oxide thin films (2010) | 빈 괄호, for, 조동사 |
| W2045930807 Void defect reduction after CMP (2007) | 전치사 뒤 비어 있음 |

**복구는 시도했으나 현실적이지 않았다.** Crossref가 출판사 초록을 갖고 있을 수 있어 9건을 조회했다. 8건은 Crossref에 초록이 아예 없었고(ECS·IOP·AIP 논문), 초록이 있던 1건(W2030331744)도 `iridium oxide ()`처럼 같은 부분이 비어 있었다(원본부터 수식이 빠진 것).

**결정: 8건은 제거, W2076838934는 "남기되 표시" (2026-10-21, 사용자 결정)**
- 처음에는 9건을 모두 제거했다(PR #12). 그러나 W2076838934는 값이 빠졌을 뿐 **ALD 포화 펄스, 표면 수산화와 누설전류의 관계** 같은 정성적 내용이 유용하고 평가 질문의 정답 논문이기도 해서, 제거 대신 **남기되 `math_loss` 표시를 붙이기로** 했다.
- 구현: `KEEP_WITH_FLAG`에 사람이 검토한 논문 ID와 이유를 적어 두고, 그 논문은 제거하지 않고 `data/processed/papers.jsonl`에 `"math_loss": [걸린 신호 목록]` 필드를 붙여 남긴다. 다른 8건은 그대로 제거한다. 검토 없이 모두 남기고 표시만 붙여 보려면 `--keep-math-loss`.
- **표시는 아직 데이터에만 있고 답변 단계가 이를 읽지 않는다.** 따라서 이 논문이 근거로 들어오면 모델이 빈 수치를 다시 지어낼 위험이 그대로 남아 있다. `math_loss`가 있는 논문의 수치는 만들지 않고 "초록에서 수치가 누락됨"이라고 밝히게 하는 것은 **rag 영역 후속 PR**이 필요하다(그 뒤 충실도를 다시 재서 Q04의 환각이 사라지는지 확인한다).
- 제거(8건)는 그 논문들의 정성적 내용을 잃는 대가가 있다. 되돌리려면 `KEEP_WITH_FLAG`에 추가하면 된다.
- **평가 질문 영향**: 남긴 덕분에 Q04와 F03의 정답이 코퍼스에 그대로 있다. 영향받는 질문은 **F09 하나**(정답 3편 중 W2162048190이 제거되어 2편)다. 평가 파일은 evaluation 영역이라 별도 PR에서 고친다. 그때까지 로컬에서 `test_field_gold_doc_ids_exist_in_corpus`가 실패한다(낡은 정답 목록을 알려 주는 의도된 경고).

**하류 영향 (인덱스를 314건으로 다시 구축해 측정)**

| 질문 세트 | 지표 | 제거 전 (322건) | 이번 결정 후 (314건) |
| --- | --- | ---: | ---: |
| 초록 기반 27개 | Hit@1 / Hit@5 / MRR | 0.889 / 1.000 / 0.929 | 0.889 / 1.000 / 0.929 |
| 현업 표현 14개 | Hit@1 / Hit@5 / MRR | 0.643 / 0.929 / 0.781 | 0.643 / 0.929 / 0.781 |
| 현업 표현 14개 | Recall@5 | 0.606 | 0.606 |

- 두 세트의 검색 지표가 제거 전과 **완전히 같다.** (참고: 9건을 모두 제거했던 PR #12 시점에는 Q04의 정답이 사라져 초록 기반 세트 Hit@5가 0.963으로 내려갔다. 이는 검색 악화가 아니라 정답 논문이 코퍼스에서 사라진 효과였다.)
- 답변 캐시(`faithfulness_answers`)는 코퍼스 기준이 아니라서 낡은 결과가 되므로 따로 보관했다.

## 시행착오

- `polymer`를 초록 전체에서 찾았더니 일반 XRD 입문 논문 2건과 CMP 소모품 논문 1건이 잘못 제거됐다(CMP 패드나 XRD 시료에 고분자가 나오는 정상 논문). 그래서 **제목 기준**으로 좁혔다. 제거 목록을 직접 읽어 보고 발견했다.
- 수식 누락 규칙의 첫 구현에서 정규식의 `\b`(단어 경계)가 셸을 거치며 제어 문자로 바뀌어, 9건이 걸려야 하는데 2건만 걸렸다. 걸린 개수가 직접 확인한 목록과 달라서 알아챘다(규칙 파일을 별도로 작성해 교체).

## 알려진 한계

- 키워드 규칙이라 의미가 비슷한데 단어가 다른 무관 논문은 못 거른다. TiO2 나노입자처럼 반도체와 거리가 먼 소재의 XRD 기본 개념 논문은 Scherrer 식 설명이 목적이라 허용했다.
- 규칙이 도메인 판단에 의존하므로 `removed.jsonl`을 주기적으로 검토해야 한다.
- **수식 누락 탐지는 눈에 보이는 빈자리만 잡는다.** 문장이 멀쩡하게 이어지는 누락은 못 찾으므로 재현율(놓치는 비율)은 알 수 없다. 다른 출처와 대조해 재현율을 재는 것은 Crossref 초록이 대부분 없어 하지 못했다.
- 규칙을 322건에 맞춰 만들었다. 코퍼스를 늘리면 오탐·미탐이 생길 수 있어 새로 수집한 뒤 `removed.jsonl`의 `math_loss` 항목을 검토해야 한다.
- `KEEP_WITH_FLAG`는 사람이 ID로 관리하는 목록이라, 새로 수집한 논문에서 같은 판단이 필요하면 직접 추가해야 한다.
- 아래첨자 사이의 공백(`HfO 2`)은 수식 누락이 아니라 표기 문제이며 이번에는 다루지 않았다(임베딩 품질에 미치는 영향은 측정하지 않음).
