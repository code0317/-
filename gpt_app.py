import streamlit as st
from openai import OpenAI

if "api_key" not in st.session_state:
    st.session_state.api_key = ""

api_key_input = st.text_input("OpenAI API Key", type="password", value=st.session_state.api_key)

if api_key_input and api_key_input != st.session_state.api_key:
    st.session_state.api_key = api_key_input

if not st.session_state.api_key:
    st.warning("API Key를 입력해 주세요.")

@st.cache_data(show_spinner="GPT에게 물어보는 중입니다...")
def get_gpt_response(api_key, prompt):
    client = OpenAI(api_key=api_key)
    response = client.responses.create(
        model="gpt-4.1-mini",
        input=prompt
    )
    return response.output_text

st.title("GPT 응답 웹앱")
prompt = st.text_area("질문을 입력하세요:")

if st.button("Ask!", disabled=(len(prompt) == 0 or not st.session_state.api_key)):
    output = get_gpt_response(st.session_state.api_key, prompt)
    st.write(output)
