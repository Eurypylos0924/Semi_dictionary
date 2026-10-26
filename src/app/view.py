"""질문 하나에 대한 답변을 화면에 그리는 부품. streamlit 호출만 모아 두고 판단은 logic.py에 맡긴다."""

import streamlit as st

from src.app import logic


def render_reply(reply: dict) -> None:
    """reply = {"result": 파이프라인 결과} 또는 {"error": 메시지}. 대화 기록을 다시 그릴 때도 같은 함수를 쓴다."""
    if "error" in reply:
        st.error(reply["error"], title="답변을 만들지 못했습니다")
        return

    result = reply["result"]
    label, color = logic.status_badge(result)
    st.badge(label, color=color)
    st.markdown(logic.safe_md(result["answer"]))
    for note in logic.warnings_for(result):
        st.warning(note)
    if reason := logic.reason_to_show(result):
        st.caption(logic.safe_md(f"근거 판정 이유: {reason}"))

    papers = logic.numbered_papers(result)
    cited = [p for p in papers if p["cited"]]
    if cited:
        st.markdown("**출처** (답변이 인용한 논문)")
        for p in cited:
            st.markdown(_source_line(p))
    with st.expander(f"검색된 논문 {len(papers)}편 (번호는 답변 속 [n]과 같음)"):
        for p in papers:
            st.markdown(_source_line(p) + f" · 유사도 {p['score']:.2f}" + (" · :material/check: 인용됨" if p["cited"] else ""))
            st.caption(logic.safe_md(p["abstract"]))


def _source_line(p: dict) -> str:
    name = logic.safe_md(p["title"])
    title = f"[{name}]({p['url']})" if p["url"] else name
    flag = " :orange[수치 일부 누락]" if p["math_loss"] else ""
    return f"[{p['number']}] {title} ({p['year']}){flag}"
