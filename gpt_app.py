import streamlit as st
from openai import OpenAI

# --- 사이드바에서 페이지 선택 ---
page = st.sidebar.selectbox("페이지를 선택하세요.", ["질문", "Chat"])

# --- API Key 입력 및 session_state 저장 ---
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
def get_gpt_response(api_key, prompt, chat_history=None):
    client = OpenAI(api_key=api_key)
    # chat_history: [[role, content], ...]
    if chat_history is None:
        chat_history = [{"role": "user", "content": prompt}]
    else:
        chat_history = chat_history + [{"role": "user", "content": prompt}]
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=chat_history
    )
    return response.choices[0].message.content

# --- '질문' 페이지(실습1) ---
if page == "질문":
    prompt = st.text_area("User prompt")
    if st.button("Ask!", disabled=(len(prompt.strip()) == 0)):
        output = get_gpt_response(st.session_state.api_key, prompt)
        st.write(output)

# --- 'Chat' 페이지(실습2) ---
elif page == "Chat":
    st.header("Chatbot (실습2)")
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    if st.button("Clear"):
        st.session_state.chat_history = []

    # 채팅 내역 보여주기
    for item in st.session_state.chat_history:
        if item["role"] == "user":
            st.markdown(f"**👤 User:** {item['content']}")
        else:
            st.markdown(f"**🤖 GPT:** {item['content']}")

    user_input = st.text_input("메시지를 입력하세요:", key="chat_input")
    if st.button("Send", disabled=(len(user_input.strip()) == 0)):
        # 대화 내역에 추가 (user)
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        # gpt 응답 받기
        gpt_response = get_gpt_response(st.session_state.api_key, user_input, st.session_state.chat_history[:-1])
        # 대화 내역에 추가 (assistant)
        st.session_state.chat_history.append({"role": "assistant", "content": gpt_response})
