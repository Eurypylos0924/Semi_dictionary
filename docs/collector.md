# 수집 (collector)

> 담당 브랜치: `collector_branch` · 담당 파일: `src/collector/`, `tests/test_collector.py`
> 이 문서는 해당 영역의 PR에서만 수정한다 ([협업 방식](workflow.md)).

논문 제목과 초록만 수집한다 (본문 PDF는 저작권·용량 문제로 제외). 모든 주제는 `TOPICS`에서 바꿀 수 있다.

| 주제 | 내용 |
| --- | --- |
| `hfo2_ald` | HfO2 박막의 원자층 증착 |
| `high_k_leakage` | 고유전율 소재의 누설전류 |
| `xrd_thin_film` | 박막 XRD 결정성·결정립 크기 분석 |
| `cmp_defect` | CMP 공정 결함 |
| `wafer_defect` | 웨이퍼 맵 결함 패턴 |
| `yield_process` | 공정 수율·근본 원인 분석 |
| `xrd_scherrer`, `xrd_williamson_hall` | XRD 기본 개념: Scherrer 식, FWHM, 결정립 크기·변형률 분석 (평가에서 드러난 빈틈 보강) |
| `hfo2_leakage_mechanism` | HfO2 누설 전도 메커니즘 (Poole-Frenkel 등, 빈틈 보강) |

| 수집기 | 출처 | 상태 |
| --- | --- | --- |
| `src/collector/openalex_collect.py` | OpenAlex 공식 API (학술지 포함) | 사용 중 — 356건 수집 (정제 후 314건) |
| `src/collector/arxiv_collect.py` | arXiv 공식 API | 이 네트워크 IP에서 429(rate limit)로 수집 실패, 네트워크가 바뀌면 재시도 |

## 동작 방식

- 논문은 거의 바뀌지 않으므로 결과 파일(`data/raw/*.jsonl`)이 있으면 수집을 건너뛴다.
- `--refresh`는 기존 논문을 그대로 두고 새 논문만 합친다 (같은 ID는 한 번만 저장하므로 재실행해도 중복이 쌓이지 않음).
- OpenAlex는 초록을 `단어 -> 위치` 형태(inverted index)로 주므로 문장으로 복원해 저장한다.
- arXiv는 요청 간격 3.5초, 한도 초과(429) 시 대기 시간을 늘려 재시도한다.

## 검색어를 정한 방식

새 주제를 추가하기 전에 검색어를 한 번 호출해 결과를 눈으로 확인한다. 예: `"peak broadening"` 검색어는 제약·생물 논문이 섞여 버리고 Williamson-Hall 검색어로 교체했다.
새 주제를 `TOPICS`에 추가하면 `src/preprocessing/clean.py`의 `REQUIRE`에도 규칙을 추가해야 한다(없으면 그 주제 논문이 전부 걸러진다. 테스트가 이를 확인한다).

## 알려진 한계

- HfO2 ALD 주제는 관련도순 상위가 2000년대 초반 논문 위주라, 연도 필터나 인용 수 기준 보완이 필요하다.
- 초록만 수집하므로 수치·실험 조건이 필요한 질문에는 근거가 부족할 수 있다.
- 현업 표현 질문(예: CMP 후 Idsat 저하)에 답할 논문이 코퍼스에 없다.
- arXiv는 이 네트워크 IP에서 429로 수집하지 못했다.
