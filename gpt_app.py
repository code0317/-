import streamlit as st
from openai import OpenAI

if "api_key" not in st.session_state:
    st.session_state.api_key = ""

api_key = st.text_input("OpenAI API Key", type="password", value=st.session_state.api_key)

if api_key != st.session_state.api_key:
    st.session_state.api_key = api_key
    
if st.session_state.api_key:
    client = OpenAI(api_key=st.session_state.api_key)
    
    st.title("OpenAI GPT model")
    
    prompt = st.text_area("User prompt")

    if st.button("Ask!", disabled=(len(prompt)==0)):
    response = client.responses.create(
        model="gpt-4.1-mini",
        input=prompt
    )
    st.write(response.output_text)

else:st.warning("API Key를 입력해 주세요.") 
