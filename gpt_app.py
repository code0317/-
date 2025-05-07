import streamlit as st
from openai import OpenAI

# 1. API 키 저장 (session_state 이용)
if "api_key" not in st.session_state:
    st.session_state.api_key = ""

api_key = st.text_input("OpenAI API Key", type="password", value=st.session_state.api_key)

if api_key != st.session_state.api_key:
    st.session_state.api_key = api_key

# 2. OpenAI 클라이언트 생성
def create_client(api_key):
    return OpenAI(api_key=api_key)

# 3. GPT 응답 함수 (캐싱)
@st.cache_data(show_spinner="GPT에게 물어보는 중입니다...")
def get_gpt_response(api_key, prompt):
    client = create_client(api_key)
    response = client.responses.create(
        model="gpt-4.1-mini",
        input=prompt
    )
    return response.output_text

# 4. Streamlit UI
st.title("GPT 응답 웹앱")
prompt = st.text_area("질문을 입력하세요:")

if st.button("Ask!", disabled=(len(prompt) == 0 or not api_key)):
    output = get_gpt_response(api_key, prompt)
    st.write(output)
