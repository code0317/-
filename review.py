import streamlit as st
import openai
import requests

st.title("🔍 Prospective 1차 필터 + GPT 심층 분석 리뷰 분석기")

api_key_openai = st.text_input("🔐 OpenAI API 키 입력", type="password")
api_key_prospective = st.text_input("🔐 Prospective API 키 입력", type="password")

reviews_input = st.text_area(
    "📋 분석할 리뷰들을 한 줄씩 입력하세요 (여러 리뷰는 줄바꿈으로 구분)",
    height=200
)

def prospective_review_check(review_text, api_key):
    url = "https://api.prospectiveapi.com/v1/review-check"  # 실제 API 주소 확인 필요
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {"review": review_text}

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"API error: {response.status_code}"}
    except Exception as e:
        return {"error": str(e)}

def analyze_review_gpt(review_text, api_key):
    openai.api_key = api_key
    system_prompt = """
    당신은 리뷰 분석 전문가입니다. 다음 리뷰를 보고 요약과 함께 광고성 리뷰인지, 억까 리뷰인지, 일반 리뷰인지 판단해주세요.
    출력 형식:

    [요약]:
    [리뷰 유형]: 광고성 / 억까 / 일반
    [신뢰도 분석]:
    """

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": review_text}
        ],
        max_tokens=200,
        temperature=0.7,
    )
    return response.choices[0].message.content.strip()

if st.button("리뷰 분석 시작"):
    if not api_key_openai:
        st.warning("OpenAI API 키를 입력하세요.")
    elif not api_key_prospective:
        st.warning("Prospective API 키를 입력하세요.")
    elif not reviews_input.strip():
        st.warning("분석할 리뷰를 입력하세요.")
    else:
        reviews = [r.strip() for r in reviews_input.split('\n') if r.strip()]
        st.write(f"총 {len(reviews)}개의 리뷰를 분석합니다.")

        for i, review in enumerate(reviews, 1):
            st.markdown(f"---\n### 리뷰 {i}")
            st.markdown(f"**원문:** {review}")

            with st.spinner("Prospective API 검사 중..."):
                prospective_result = prospective_review_check(review, api_key_prospective)
            if "error" in prospective_result:
                st.error(f"Prospective API 오류: {prospective_result['error']}")
                continue
            
            st.markdown(f"**Prospective API 결과:** {prospective_result}")

            # Prospective API 결과에 따라 GPT 분석 여부 결정
            # 예시: 'is_ad_review' 또는 'is_fake_review'가 True면 GPT 분석 실행
            is_ad_review = prospective_result.get("is_ad_review", False)
            is_fake_review = prospective_result.get("is_fake_review", False)

            if is_ad_review or is_fake_review:
                with st.spinner("GPT 심층 분석 중..."):
                    gpt_result = analyze_review_gpt(review, api_key_openai)
                st.markdown(f"**GPT 분석 결과:**\n{gpt_result}")
            else:
                st.markdown("✅ 정상 리뷰로 판단되어 GPT 분석은 생략합니다.")
