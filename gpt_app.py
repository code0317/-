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

client = OpenAI(api_key=st.session_state.api_key)

# --- 실습 1 : 질문 페이지 ---
if page == "질문":
    st.title("질문")

    prompt = st.text_area("User prompt")
    if st.button("Ask!", disabled=(len(prompt.strip()) == 0)):
        with st.spinner("GPT에게 물어보는 중입니다..."):
            response = client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[{"role": "user", "content": prompt}]
            )
            st.write(response.choices[0].message.content)

# --- 실습 2 : Chat 페이지 ---
elif page == "Chat":
    st.title("Chatbot")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    if st.button("Clear"):
        st.session_state.messages = []

    # 대화 내역 표시
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    # 채팅 입력 & 응답
    if prompt := st.chat_input("메시지를 입력하세요:"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)

        chat_response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=st.session_state.messages,
            stream=True
        )

        generated_text = ""
        with st.chat_message("assistant"):
            chat_area = st.empty()
            for chunk in chat_response:
                if hasattr(chunk.choices[0].delta, "content") and chunk.choices[0].delta.content:
                    generated_text += chunk.choices[0].delta.content
                    chat_area.markdown(generated_text)
        st.session_state.messages.append({"role": "assistant", "content": generated_text})
