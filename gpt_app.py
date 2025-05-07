import streamlit as st
from openai import OpenAI

# API 키 입력
api_key = st.text_input("OpenAI API Key", type="password")

# 클라이언트 생성 함수 (캐싱 X)
def create_client(api_key):
    return OpenAI(api_key=api_key)

# GPT 응답 함수 (캐싱 O)
@st.cache_data(show_spinner="응답을 불러오는 중...")
def get_gpt_response(api_key, prompt):
    client = create_client(api_key)
    response = client.responses.create(
        model="gpt-4.1-mini",
        input=prompt
    )
    return response.output_text

# UI 구성
st.title("OpenAI GPT model")
prompt = st.text_area("User prompt")

if st.button("Ask!", disabled=(len(prompt) == 0 or not api_key)):
    output = get_gpt_response(api_key, prompt)
    st.write(output)
