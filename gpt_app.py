import streamlit as st
from openai import OpenAI

# --- 페이지 선택 ---
page = st.sidebar.selectbox("페이지를 선택하세요.", ["질문", "Chat"])

# --- API Key 입력 ---
if "api_key" not in st.session_state:
    st.session_state.api_key = ""

api_key_input = st.text_input("OpenAI API Key", type="password", value=st.session_state.api_key)
if api_key_input and api_key_input != st.session_state.api_key:
    st.session_state.api_key = api_key_input
if not st.session_state.api_key:
    st.warning("API Key를 입력해 주세요.")
    st.stop()

# --- GPT 응답 함수 ---
@st.cache_data(show_spinner="GPT에게 물어보는 중입니다...")
def get_gpt_response(api_key, messages):
    client = OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=messages
    )
    return response.choices[0].message.content

# --- Chat 페이지 ---
if page == "Chat":
    st.header("Chatbot (실습2)")

    # 대화 내역 저장용
    if "messages" not in st.session_state:
        st.session_state.messages = []  # [{"role": "user", "content": ...}, {"role": "assistant", ...}]

    # Clear 버튼
    if st.button("Clear"):
        st.session_state.messages = []

    # 채팅 내역 보여주기
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.markdown(f":bust_in_silhouette: {msg['content']}")
        elif msg["role"] == "assistant":
            st.markdown(f":robot_face: {msg['content']}")

    # 사용자 입력
    user_input = st.text_input("메시지를 입력하세요:", key="chat_input")

    # Send 버튼
    if st.button("Send", disabled=(len(user_input.strip()) == 0)):
        # 1. 사용자의 입력을 messages에 추가
        st.session_state.messages.append({"role": "user", "content": user_input})

        # 2. gpt-4.1-mini 모델로 전체 메세지 히스토리 전달 => 응답 생성
        gpt_output = get_gpt_response(st.session_state.api_key, st.session_state.messages)

        # 3. assistant 응답 추가
        st.session_state.messages.append({"role": "assistant", "content": gpt_output})

        # 4. 입력창 비우기
        st.session_state["chat_input"] = ""

        # 새로고침 (streamlit은 자동 렌더링됨)
