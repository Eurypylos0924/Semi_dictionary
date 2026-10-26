"""논문 근거 QA 챗봇 화면.

실행: uv run streamlit run src/app/main.py
질문마다 파이프라인(src/rag)을 독립적으로 실행한다. 이전 대화를 기억하지 않는다.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]  # `streamlit run`은 스크립트 폴더만 import 경로에 넣으므로 프로젝트 루트를 직접 추가한다
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import streamlit as st  # noqa: E402

from src.app import logic, view  # noqa: E402
from src.const.config import DOCS_PATH  # noqa: E402
from src.rag.llm import resolve  # noqa: E402

st.set_page_config(page_title="반도체 박막 논문 QA", page_icon=":material/biotech:")


@st.cache_data
def corpus_size() -> int | None:
    """검색 대상 논문 수. 인덱스가 아직 없으면 None."""
    if not DOCS_PATH.exists():
        return None
    with DOCS_PATH.open(encoding="utf-8") as f:
        return sum(1 for _ in f)


if "messages" not in st.session_state:
    st.session_state.messages = []  # [{"role": "user", "content": str} | {"role": "assistant", "reply": dict}]
if "chat_epoch" not in st.session_state:
    st.session_state.chat_epoch = 0  # 대화를 지울 때마다 올려서 예시 버튼을 새 위젯으로 만든다(이전에 고른 예시가 남아 자동으로 다시 질문되는 것을 막는다)

with st.sidebar:
    st.header("설정")
    query_mode = st.segmented_control("검색 방식", logic.QUERY_MODES, default="max", help="max: 질문과 영어 재작성문을 함께 검색 / original: 질문만 검색") or "max"
    gate_mode = st.segmented_control("근거 판단", logic.GATE_MODES, default="judge", help="judge: LLM이 검색된 초록이 질문의 근거가 되는지 판정 / score: 검색 점수만 확인") or "judge"
    provider, model = resolve()
    st.caption(f"답변 모델: {provider} / {model}")
    size = corpus_size()
    if size is None:
        st.warning("인덱스가 없습니다. `uv run python -m src.vectorstore.build`로 먼저 만드세요.")
    else:
        st.caption(f"검색 대상: 반도체·디스플레이 박막 공정 논문 초록 {size}편")
    if st.button("대화 지우기", icon=":material/delete:"):  # 사이드바는 질문을 처리하기 전에 그려지므로 대화가 있는지로 비활성화하면 첫 답변 뒤에도 꺼져 있다
        st.session_state.messages = []
        st.session_state.chat_epoch += 1
        st.rerun()

st.title("반도체 박막 논문 QA")
st.caption("질문하면 논문 초록을 근거로 한국어로 답하고, 인용한 논문을 함께 보여줍니다. 논문에 없는 내용은 모른다고 답합니다.")
st.info(
    "수치·실험 조건은 초록에 없는 경우가 많고, 코퍼스에 없는 주제는 답하지 못합니다. 각 질문은 독립적으로 처리되어 이전 대화를 기억하지 않습니다.",
    icon=":material/info:",
)

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if message["role"] == "user":
            st.write(logic.safe_md(message["content"]))
        else:
            view.render_reply(message["reply"])

prompt = st.chat_input("질문을 입력하세요 (예: CMP 후 웨이퍼에 긁힌 자국을 어떻게 줄여?)", submit_mode="disable")

if not st.session_state.messages:
    suggestions = st.empty()
    selected = suggestions.pills("이런 질문을 해 보세요", list(logic.EXAMPLES), key=f"examples_{st.session_state.chat_epoch}")
    if selected:
        prompt = selected
    if prompt:
        suggestions.empty()  # 첫 답변이 그려지기 전에 예시 버튼을 치운다

if prompt:
    prompt = prompt.strip()
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(logic.safe_md(prompt))
    with st.chat_message("assistant"):
        with st.spinner("논문을 검색하고 근거를 판정하는 중... (보통 10~30초)"):
            try:
                reply = {"result": logic.run_question(prompt, query_mode=query_mode, gate_mode=gate_mode)}
            except Exception as e:  # noqa: BLE001 - 무료 API 한도·네트워크 오류 등을 화면에 알려 준다. 메시지는 키가 섞일 수 있어 종류만 보여 준다
                reply = {"error": f"{type(e).__name__}가 발생했습니다. API 한도, 키 설정(.env), 인덱스 구축 여부를 확인하세요."}
        view.render_reply(reply)
    st.session_state.messages.append({"role": "assistant", "reply": reply})
