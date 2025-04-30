import streamlit as st
import openai

# 페이지 기본 설정
st.set_page_config(page_title="GPT-4.1-mini QA", layout="centered")

st.title("💬 GPT-4.1-mini에게 물어봐!")

# 사용자로부터 API 키 입력 받기
api_key = st.text_input("🔑 OpenAI API 키를 입력하세요", type="password")

# 입력 필드 잠금 설정
if api_key:
    openai.api_key = api_key
    user_input = st.text_area("✍️ 질문을 입력하세요")

    if st.button("질문하기") and user_input.strip():
        with st.spinner("GPT-4.1-mini가 답변 중..."):
            try:
                response = openai.ChatCompletion.create(
                    model="gpt-4-1106-preview",  # 현재 gpt-4.1-mini는 이 모델명 사용
                    messages=[
                        {"role": "system", "content": "당신은 친절한 AI 도우미입니다."},
                        {"role": "user", "content": user_input}
                    ],
                    temperature=0.7
                )
                st.markdown("### 🤖 GPT의 답변")
                st.write(response['choices'][0]['message']['content'])
            except Exception as e:
                st.error(f"❌ 에러 발생: {e}")
else:
    st.warning("먼저 OpenAI API 키를 입력해주세요.")

