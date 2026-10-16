# 협업 방식

개인 프로젝트이지만 팀 프로젝트(CodeClue)처럼 **영역별 브랜치 → `dev` → `main`** 으로 진행한다.
코드는 Claude가 작성하고 커밋·push·PR까지 만들며, **검토와 병합은 사람(박종원)이 직접** 한다.

## 영역과 브랜치

| 영역 | 브랜치 | 담당 파일 | 문서 |
| --- | --- | --- | --- |
| 수집 | `collector_branch` | `src/collector/`, `tests/test_collector.py` | [collector.md](collector.md) |
| 정제 | `preprocessing_branch` | `src/preprocessing/`, `tests/test_clean.py` | [preprocessing.md](preprocessing.md) |
| 벡터 저장소 | `vectorstore_branch` | `src/vectorstore/`, `tests/test_vectorstore.py` | [vectorstore.md](vectorstore.md) |
| 검색·답변 | `rag_branch` | `src/rag/`, `tests/test_generator.py`, `tests/test_llm.py` | [rag.md](rag.md) |
| 평가 | `evaluation_branch` | `src/evaluation/`, `tests/test_evaluation.py` | [evaluation.md](evaluation.md) |
| 공유 | `general_branch` | `README.md`, `docs/workflow.md`, `pyproject.toml`, `uv.lock`, `.env.example`, `.gitignore`, `src/const/`, `.github/` | 이 문서 |

- 영역 브랜치는 **자기 영역 파일만** 수정한다. 영역 문서(`docs/<영역>.md`)도 해당 영역 PR에서만 고친다.
- 의존성 추가나 설정 변경처럼 여러 영역이 함께 쓰는 파일은 `general_branch`로 올린다.

## 규칙

1. **작업을 시작하기 전과 PR을 만들기 전에 최신 `dev`를 해당 영역 브랜치에 합친다.** 이미 병합된 PR이 있으면 반드시 합친다. 브랜치가 오래 살수록 `dev`와 벌어지므로 이 규칙이 충돌을 막는 핵심이다.
2. **여러 영역에 걸친 변경은 영역별로 나눠 PR을 만든다.** 병합은 파이프라인 순서를 따른다: `general` → `collector` → `preprocessing` → `vectorstore` → `rag` → `evaluation`.
3. 열려 있는 PR이 병합되기 전에는 같은 영역의 다음 PR을 만들지 않는다.
4. `main`과 `dev`에는 직접 push하지 않는다. 항상 PR로 올리고 사람이 병합한다.
5. 병합한 뒤에는 `dev`를 각 영역 브랜치에 다시 합친다.

## PR 작성

요약, 확인한 내용, 알려진 한계, 리뷰 요청을 쓴다 ([템플릿](../.github/pull_request_template.md)).
평가 지표가 좋게 나오면 평가가 쉬운 것은 아닌지 점검해 한계를 정직하게 적는다.

## 비밀값과 데이터

저장소가 **공개(PUBLIC)** 이므로 API 키(`.env`), 수집 데이터(`data/`)는 커밋하지 않는다. 키 이름은 `.env.example`을 참고한다.

## 이력

- 2026-10-16: 처음에는 기능별 단기 브랜치(`feat/...`)로 시작했으나, PR이 병합되지 않은 채 쌓이면서 `README.md`(모든 영역이 고치는 공유 파일)에서 충돌이 났다.
  이후 영역 구분과 공유 파일 분리를 위해 영역별 브랜치 + `general_branch` 방식으로 바꾸고, README의 영역별 상세 내용을 `docs/`로 나눴다.
