import streamlit as st
from openai import OpenAI

PKNU_LIBRARY_REGULATIONS = open("library_rule.txt", encoding="utf-8").read()

# 2. 페이지 선택(세 개)
page = st.sidebar.selectbox("페이지를 선택하세요.", ["Chat", "ChatBot", "부경 도서관Chatbot"])

# 3. API key 입력 (기존과 동일)
if "api_key" not in st.session_state:
    st.session_state.api_key = ""
api_key_input = st.text_input("OpenAI API Key", type="password", value=st.session_state.api_key)
if api_key_input and api_key_input != st.session_state.api_key:
    st.session_state.api_key = api_key_input
if not st.session_state.api_key:
    st.warning("API Key를 입력해 주세요.")
    st.stop()

client = OpenAI(api_key=st.session_state.api_key)

# --- 실습1 ---
if page == "Chat":
    st.title("Chat")
    prompt = st.text_area("User prompt")
    if st.button("Ask!", disabled=(len(prompt.strip()) == 0)):
        with st.spinner("GPT에게 물어보는 중입니다..."):
            response = client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[{"role": "user", "content": prompt}]
            )
            st.write(response.choices[0].message.content)

# --- 실습2 ---
elif page == "ChatBot":
    st.title("Chatbot")
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if st.button("Clear"):
        st.session_state.messages = []
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
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

# --- 실습3 Chatbot(도서관 챗봇) ---
elif page == "부경 도서관Chatbot":
    st.title("국립부경대학교 도서관 챗봇")
    # 대화 상태 분리해서 관리
    if "lib_messages" not in st.session_state:
        st.session_state.lib_messages = [
            {"role": "system", "content": "너는 국립부경대학교 도서관 규정에 대해 답변하는 챗봇이야. 규정 내용만 바탕으로 답변하라:\n" + PKNU_LIBRARY_REGULATIONS}
        ]
    if st.button("Clear"):
        st.session_state.lib_messages = [
            {"role": "system", "content": "너는 국립부경대학교 도서관 규정에 대해 답변하는 챗봇이야. 규정 내용만 바탕으로 답변하라:\n" + PKNU_LIBRARY_REGULATIONS}
        ]
    for msg in st.session_state.lib_messages:
        if msg["role"] == "system":
            continue
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
    if prompt := st.chat_input("도서관 질문을 입력하세요:"):
        st.session_state.lib_messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)
        chat_response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=st.session_state.lib_messages,
            stream=True
        )
        generated_text = ""
        with st.chat_message("assistant"):
            chat_area = st.empty()
            for chunk in chat_response:
                if hasattr(chunk.choices[0].delta, "content") and chunk.choices[0].delta.content:
                    generated_text += chunk.choices[0].delta.content
                    chat_area.markdown(generated_text)
        st.session_state.lib_messages.append({"role": "assistant", "content": generated_text})
