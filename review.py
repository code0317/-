import streamlit as st
import requests
import openai

# --- 네이버 스마트스토어 리뷰 크롤러 ---
def get_naver_shopping_reviews(product_id, max_pages=2):
    reviews = []
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    for page in range(1, max_pages+1):
        url = f"https://smartstore.naver.com/i/v1/reviews?productId={product_id}&page={page}"
        res = requests.get(url, headers=headers)
        if res.status_code != 200:
            st.warning(f"페이지 {page} 요청 실패, 상태코드: {res.status_code}")
            break

        data = res.json()
        for review in data.get("reviewList", []):
            reviews.append(review.get("content", ""))

        if not data.get("hasNext"):
            break

    return reviews

# --- Prospective API 리뷰 검사 ---
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

# --- GPT 리뷰 심층 분석 ---
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

# --- 스트림릿 UI 시작 ---
st.title("🛍️ 네이버 스마트스토어 리뷰 신뢰도 분석기")

api_key_openai = st.text_input("🔐 OpenAI API 키 입력", type="password")
api_key_prospective = st.text_input("🔐 Prospective API 키 입력", type="password")
product_id = st.text_input("📦 네이버 스마트스토어 상품 ID 입력")

max_pages = st.number_input("최대 크롤링할 리뷰 페이지 수", min_value=1, max_value=10, value=2, step=1)

if st.button("리뷰 크롤링 및 분석 시작"):
    if not api_key_openai:
        st.warning("OpenAI API 키를 입력하세요.")
    elif not api_key_prospective:
        st.warning("Prospective API 키를 입력하세요.")
    elif not product_id:
        st.warning("상품 ID를 입력하세요.")
    else:
        with st.spinner("리뷰 크롤링 중..."):
            reviews = get_naver_shopping_reviews(product_id, max_pages=max_pages)

        if len(reviews) == 0:
            st.error("리뷰를 가져오지 못했습니다.")
        else:
            st.write(f"총 {len(reviews)}개의 리뷰를 가져왔습니다.")

            for i, review in enumerate(reviews, 1):
                st.markdown(f"---\n### 리뷰 {i}")
                st.markdown(f"**원문:** {review}")

                with st.spinner("Prospective API 검사 중..."):
                    prospective_result = prospective_review_check(review, api_key_prospective)
                if "error" in prospective_result:
                    st.error(f"Prospective API 오류: {prospective_result['error']}")
                    continue
                
                st.markdown(f"**Prospective API 결과:** {prospective_result}")

                # Prospective API 결과 기반 필터 (키 이름은 API 문서에 맞게 수정)
                is_ad_review = prospective_result.get("is_ad_review", False)
                is_fake_review = prospective_result.get("is_fake_review", False)

                if is_ad_review or is_fake_review:
                    with st.spinner("GPT 심층 분석 중..."):
                        gpt_result = analyze_review_gpt(review, api_key_openai)
                    st.markdown(f"**GPT 분석 결과:**\n{gpt_result}")
                else:
                    st.markdown("✅ 정상 리뷰로 판단되어 GPT 분석은 생략합니다.")
