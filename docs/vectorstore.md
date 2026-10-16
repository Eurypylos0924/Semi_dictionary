# 벡터 저장소 (vectorstore)

> 담당 브랜치: `vectorstore_branch` · 담당 파일: `src/vectorstore/`, `tests/test_vectorstore.py`
> 이 문서는 해당 영역의 PR에서만 수정한다 ([협업 방식](workflow.md)).

정제된 논문을 임베딩해 로컬 FAISS 인덱스로 저장한다.

```bash
uv run python -m src.vectorstore.build            # 인덱스가 이미 있으면 건너뜀
uv run python -m src.vectorstore.build --rebuild  # 코퍼스를 바꿨을 때 다시 구축
```

## 설계

| 항목 | 선택 | 이유 |
| --- | --- | --- |
| 청크 | 논문 1건 = 청크 1개 (`제목
초록`) | 초록이 평균 약 1,150자라 따로 쪼갤 필요가 없다 |
| 임베딩 | NVIDIA `nemotron-3-embed-1b` (2048차원, 무료 API) | 한국어 질문으로 영어 논문을 찾을 수 있다. 키는 `.env`의 `nvidiaapi_key` |
| 정규화 | 벡터 길이를 1로 맞춤 | 내적(inner product)이 곧 코사인 유사도가 된다 |
| 인덱스 | FAISS `IndexFlatIP` (정확 검색) | 논문 322건 규모라 근사 검색이 필요 없다 |
| 긴 입력 | `truncate="END"` | 모델 한도를 넘으면 오류 대신 뒷부분을 자른다 |
| 재사용 | 인덱스는 한 번 만들고 검색 때는 파일만 읽음 | 질문 1건당 임베딩 API는 1번만 호출 |

- 저장 위치: `data/index/papers.faiss`(벡터), `data/index/papers_meta.jsonl`(FAISS 번호와 같은 순서의 논문 정보). 둘 다 git에 올리지 않는다.

## 알려진 한계

- 임베딩 검색만 사용한다. 모델명·약어처럼 정확한 단어가 중요한 질문에는 BM25 같은 키워드 검색을 섞는 하이브리드 검색이 도움이 될 수 있다(미구현).
- 논문 수가 수만 건으로 늘면 정확 검색이 느려지므로 근사 인덱스를 검토해야 한다.
