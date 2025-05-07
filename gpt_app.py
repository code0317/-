import streamlit as st
from openai import OpenAI

PKNU_LIBRARY_REGULATIONS = open("library_rule.txt", encoding="utf-8").read()

# 2. 페이지 선택(세 개)
page = st.sidebar.selectbox("페이지를 선택하세요.", ["Chat", "ChatBot", "부경 도서관Chatbot", "pdf chat"])

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

if page == "pdf chat":
    st.title("PDF Chatbot")

    # 1. 파일 업로드 위젯
    pdf_file = st.file_uploader("PDF 파일을 업로드하세요", type=["pdf"])

    # Vector store/상태 초기화 및 Clear 버튼
    if st.button("Clear"):
        if "pdf_chat_history" in st.session_state:
            del st.session_state["pdf_chat_history"]
        if "pdf_text" in st.session_state:
            del st.session_state["pdf_text"]

    # 이전 대화 기록 저장
    if "pdf_chat_history" not in st.session_state:
        st.session_state.pdf_chat_history = []

    # PDF 파일이 업로드되면 텍스트 추출
    if pdf_file is not None and "pdf_text" not in st.session_state:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(pdf_file.read())
            tmp_path = tmp.name

        # PyPDF2로 텍스트 추출
        with open(tmp_path, "rb") as f:
            pdf = PyPDF2.PdfReader(f)
            full_text = ""
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    full_text += text + "\n"
        st.session_state.pdf_text = full_text
        os.remove(tmp_path)

    # PDF가 올라왔을 때만 챗봇챗 활성화
    if "pdf_text" in st.session_state:
        st.success("PDF 업로드 및 텍스트 추출이 완료되었습니다.")

        # 이전 대화 출력
        for msg in st.session_state.pdf_chat_history:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])

        query = st.chat_input("PDF 내용에 대해 질문을 입력하세요.")
        if query:
            st.session_state.pdf_chat_history.append({"role": "user", "content": query})

            # system 프롬프트에 PDF 전체내용을 포함(간단 버전)
            messages = [{"role": "system", "content": "다음은 업로드된 PDF 파일의 전문입니다. 아래 내용을 참고해 사용자에게 답하세요.\n\n" + st.session_state.pdf_text}]
            for msg in st.session_state.pdf_chat_history:
                messages.append(msg)

            with st.spinner("답변 생성 중..."):
                response = client.chat.completions.create(
                    model="gpt-4.1-mini",
                    messages=messages,
                    stream=True
                )
                generated = ""
                with st.chat_message("assistant"):
                    chat_area = st.empty()
                    for chunk in response:
                        if hasattr(chunk.choices[0].delta, "content") and chunk.choices[0].delta.content:
                            generated += chunk.choices[0].delta.content
                            chat_area.markdown(generated)
                st.session_state.pdf_chat_history.append({"role": "assistant", "content": generated})
    else:
        st.info("PDF 파일을 먼저 업로드하세요.")

