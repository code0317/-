import streamlit as st
import openai
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time

# 🔑 GPT API 키 입력받기
st.title("🛒 쿠팡 리뷰 분석기 (GPT 기반)")
api_key = st.text_input("🔐 OpenAI API 키를 입력하세요", type="password")

if api_key:
    openai.api_key = api_key
else:
    st.warning("API 키를 먼저 입력해주세요.")
    st.stop()

# 쿠팡 리뷰 크롤링 함수
def get_reviews_from_coupang(product_url, max_pages=1):
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(options=options)

    driver.get(product_url)
    time.sleep(3)

    try:
        review_tab = driver.find_element(By.XPATH, '//a[@data-tab="review"]')
        review_tab.click()
        time.sleep(2)
    except:
        st.warning("리뷰 탭을 찾을 수 없습니다.")
        driver.quit()
        return []

    reviews = []

    for _ in range(max_pages):
        soup = BeautifulSoup(driver.page_source, "html.parser")
        blocks = soup.select("article.sdp-review__article__list__review")

        for b in blocks:
            text = b.select_one("div.sdp-review__article__list__review__content")
            if text:
                reviews.append(text.get_text(strip=True))

        try:
            next_btn = driver.find_element(By.XPATH, '//button[@aria-label="다음 페이지"]')
            next_btn.click()
            time.sleep(2)
        except:
            break

    driver.quit()
    return reviews

# GPT 분석 함수
def analyze_review(review_text):
    system_prompt = """
    당신은 리뷰 분석 전문가입니다. 다음 리뷰를 요약하고, 광고성 리뷰인지, 무지성 비판(억까) 리뷰인지, 일반적인 사용자 리뷰인지 판단하세요.
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
        ]
    )
    return response.choices[0].message.content.strip()

# Streamlit UI
product_url = st.text_input("📎 쿠팡 상품 URL을 입력하세요")

if st.button("리뷰 크롤링 및 분석"):
    if not product_url:
        st.warning("쿠팡 상품 URL을 입력해주세요.")
    else:
        with st.spinner("쿠팡 리뷰 크롤링 중..."):
            reviews = get_reviews_from_coupang(product_url, max_pages=1)

        if not reviews:
            st.warning("리뷰가 없거나 가져올 수 없습니다.")
        else:
            st.success(f"{len(reviews)}개의 리뷰를 가져왔습니다.")

            for i, review in enumerate(reviews[:5]):
                st.markdown(f"---\n### 리뷰 {i+1}")
                st.markdown(f"**원문:** {review}")
                with st.spinner("GPT 분석 중..."):
                    result = analyze_review(review)
                st.markdown(result)
