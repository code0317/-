import streamlit as st
from openai import OpenAI

api_key= st.text_input("OpenAI API Key", type="password")
client = OpenAI(api_key=api_key)

st.title("OpenAI GPT model")

prompt = st.text_area("User prompt")

if st.button("Ask!", disabled=(len(prompt)==0)):
    response = client.responses.create(
        model="gpt-4.1-mini",
        input=prompt
    )

    st.write(response.output_text)
