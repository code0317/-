import streamlit as st
import requests
from bs4 import BeautifulSoup
import openai

def scrape_yes24_reviews(url):
    """
    Yes24 책 리뷰를 스크래핑하는 함수. 실제 HTML 구조에 맞게 수정 필요.
    """
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        reviews = []
        # 가정: 리뷰가 'reviewContent' 클래스에 있음
        review_divs = soup.find_all('div', class_='reviewContent')
        for div in review_divs:
            rating = div.find('span', class_='rating').text.strip() if div.find('span', class_='rating') else "N/A"
            text = div.find('p', class_='reviewText').text.strip() if div.find('p', class_='reviewText') else "N/A"
            reviews.append({'rating': rating, 'text': text})
        return reviews
    except Exception as e:
        st.error(f"스크래핑 오류: {e}")
        return []

def scrape_book_info(url):
    """
    책 제목과 저자 정보를 스크래핑.
    """
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        title = soup.find('h1', class_='bookTitle').text.strip() if soup.find('h1', class_='bookTitle') else "Unknown Title"
        author = soup.find('span', class_='author').text.strip() if soup.find('span', class_='author') else "Unknown Author"
        return {'title': title, 'author': author}
    except Exception as e:
        st.error(f"책 정보 스크래핑 오류: {e}")
        return {'title': "Unknown Title", 'author': "Unknown Author"}

def analyze_with_sapling(review_text, sapling_api_key):
    """
    Sapling.ai로 감정 분석. 실제 API 문서에 맞게 수정 필요.
    """
    try:
        headers = {"Authorization": f"Bearer {sapling_api_key}"}
        data = {"text": review_text}
        response = requests.post("https://api.sapling.ai/v1/sentiment", headers=headers, json=data)
        if response.status_code == 200:
            return response.json()['sentiment']
        else:
            return "분석 실패"
    except Exception as e:
        return f"오류: {e}"

def analyze_with_gpt(review_text, openai_api_key):
    """
    GPT로 리뷰 신뢰도 평가.
    """
    try:
        openai.api_key = openai_api_key
        prompt = f"Assess the reliability of this review (in Korean if applicable): {review_text}"
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            max_tokens=50
        )
        return response.choices[0].text.strip()
    except Exception as e:
        return f"오류: {e}"

def main():
    st.title("Yes24 리뷰 분석기")
    
    # API 키 입력 필드
    sapling_api_key = st.text_input("Sapling.ai API 키를 입력하세요:", placeholder="Sapling.ai API 키")
    openai_api_key = st.text_input("OpenAI API 키를 입력하세요:", placeholder="OpenAI API 키")
    
    # 입력 방식 선택
    input_type = st.radio("입력 방식 선택:", ("URL", "텍스트"))
    
    if input_type == "URL":
        url = st.text_input("Yes24 책 URL을 입력하세요:")
        if st.button("분석 시작"):
            if not sapling_api_key or not openai_api_key:
                st.error("Sapling.ai 및 OpenAI API 키를 모두 입력해주세요.")
            elif url:
                with st.spinner("리뷰를 가져오고 분석 중..."):
                    book_info = scrape_book_info(url)
                    st.write(f"**책 제목**: {book_info['title']}")
                    st.write(f"**저자**: {book_info['author']}")
                    reviews = scrape_yes24_reviews(url)
                    if reviews:
                        st.success(f"{len(reviews)}개의 리뷰를 분석했습니다.")
                        for i, review in enumerate(reviews, 1):
                            sapling_result = analyze_with_sapling(review['text'], sapling_api_key)
                            gpt_result = analyze_with_gpt(review['text'], openai_api_key)
                            st.subheader(f"리뷰 {i}")
                            st.write(f"**평점**: {review['rating']}")
                            st.write(f"**리뷰 내용**: {review['text']}")
                            st.write(f"**감정 분석 (Sapling.ai)**: {sapling_result}")
                            st.write(f"**신뢰도 평가 (GPT)**: {gpt_result}")
                            st.write("---")
                    else:
                        st.warning("리뷰를 찾을 수 없습니다. URL을 확인하세요.")
            else:
                st.error("URL을 입력해주세요.")
    else:
        review_text = st.text_area("리뷰 텍스트를 입력하세요:")
        if st.button("분석 시작"):
            if not sapling_api_key or not openai_api_key:
                st.error("Sapling.ai 및 OpenAI API 키를 모두 입력해주세요.")
            elif review_text:
                with st.spinner("분석 중..."):
                    sapling_result = analyze_with_sapling(review_text, sapling_api_key)
                    gpt_result = analyze_with_gpt(review_text, openai_api_key)
                    st.write(f"**리뷰 내용**: {review_text}")
                    st.write(f"**감정 분석 (Sapling.ai)**: {sapling_result}")
                    st.write(f"**신뢰도 평가 (GPT)**: {gpt_result}")
            else:
                st.error("리뷰 텍스트를 입력해주세요.")

if __name__ == "__main__":
    main()
