import streamlit as st
from openai import OpenAI

if "api_key" not in st.session_state:
    st.session_state.api_key = ""
api_key_input = st.text_input("OpenAI API Key", type="password", value=st.session_state.api_key)
if api_key_input and api_key_input != st.session_state.api_key:
    st.session_state.api_key = api_key_input
if not st.session_state.api_key:
    st.warning("API Key를 입력해 주세요.")
    st.stop()

@st.cache_data(show_spinner="GPT에게 물어보는 중입니다...")
def get_gpt_response(api_key, messages):
    client = OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=messages
    )
    return response.choices[0].message.content

page = st.sidebar.selectbox("페이지를 선택하세요.", ["질문", "Chat"])

if page == "Chat":
    st.header("Chatbot (실습2)")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    if st.button("Clear"):
        st.session_state.messages = []

    # 대화 내역 보여주기
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.markdown(f":bust_in_silhouette: {msg['content']}")
        elif msg["role"] == "assistant":
            st.markdown(f":robot_face: {msg['content']}")

    # (1) 입력창 값은 반드시 세션에서 뽑기!
    user_input = st.text_input("메시지를 입력하세요:", key="chat_input")

    # (2) Send 버튼 눌렀을 때 조건 CLEAR하게 체크
    if st.button("Send"):
        ui = st.session_state["chat_input"]  # 반드시 최신값 가져오기!
        if ui.strip():  # 빈칸 아닐 때만
            st.session_state.messages.append({"role": "user", "content": ui})
            gpt_output = get_gpt_response(
                st.session_state.api_key,
                st.session_state.messages
            )
            st.session_state.messages.append({"role": "assistant", "content": gpt_output})
            st.session_state["chat_input"] = ""  # 입력창 비우기
         
