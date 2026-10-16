# 정제 (preprocessing)

> 담당 브랜치: `preprocessing_branch` · 담당 파일: `src/preprocessing/`, `tests/test_clean.py`
> 이 문서는 해당 영역의 PR에서만 수정한다 ([협업 방식](workflow.md)).

수집한 논문(`data/raw/*.jsonl`)에서 주제와 무관한 논문을 걸러 `data/processed/papers.jsonl`을 만든다. 현재 356건 → 322건.

```bash
uv run python -m src.preprocessing.clean
```

## 규칙 (`src/preprocessing/clean.py`)

| 규칙 | 내용 |
| --- | --- |
| `REQUIRE` | 논문이 속한 주제마다 "제목+초록에 하나라도 있어야 하는 단어". 해당 주제의 단어가 하나도 없으면 제거 (예: 수율 주제에 걸린 일반 제조업 AI 논문) |
| `EXCLUDE` | 초록 어디에 나와도 제거하는 단어 (phthalocyanine, elastomer, inkjet 등 반도체 공정과 먼 소재·분야) |
| `EXCLUDE_TITLE` | **제목에 있을 때만** 제거하는 단어 (polymer, nanocomposite, epoxy 등) |
| 제목 중복 | arXiv와 OpenAlex에 같은 논문이 있을 때 제목으로 중복 제거 |

- 제거한 논문은 이유와 함께 `data/processed/removed.jsonl`에 남겨 사람이 검토할 수 있다.

## 시행착오

- `polymer`를 초록 전체에서 찾았더니 일반 XRD 입문 논문 2건과 CMP 소모품 논문 1건이 잘못 제거됐다(CMP 패드나 XRD 시료에 고분자가 나오는 정상 논문). 그래서 **제목 기준**으로 좁혔다. 제거 목록을 직접 읽어 보고 발견했다.

## 알려진 한계

- 키워드 규칙이라 의미가 비슷한데 단어가 다른 무관 논문은 못 거른다. TiO2 나노입자처럼 반도체와 거리가 먼 소재의 XRD 기본 개념 논문은 Scherrer 식 설명이 목적이라 허용했다.
- 규칙이 도메인 판단에 의존하므로 `removed.jsonl`을 주기적으로 검토해야 한다.
