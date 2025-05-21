import streamlit as st
import matplotlib.pyplot as plt
import random
import matplotlib.font_manager as fm
import matplotlib

# 한글 폰트 설정 (예: 나눔고딕)
matplotlib.rc('font', family='NanumGothic')


# 한글 폰트 설정 (예: 나눔고딕)
matplotlib.rc('font', family='NanumGothic')


st.set_page_config(layout="wide")

# --------- Title ---------
st.title("플랫폼 선택")

# --------- Platform Selection ---------
platforms = ["쿠팡", "11번가", "G마켓", "위메프", "SSG", "롯데ON", "인터파크", "티몬"]
cols = st.columns(4)
selected_platform = None

for i, platform in enumerate(platforms):
    with cols[i % 4]:
        if st.button(platform):
            selected_platform = platform

st.markdown("---")

# --------- Graph (Mock Data) ---------
st.subheader("그래프")
fig, ax = plt.subplots()
labels = ['정상 리뷰', '광고성 리뷰', '악성 리뷰']
data = [random.randint(20, 50), random.randint(5, 20), random.randint(5, 20)]
colors = ['#6DE1D2', '#FFD63A', '#F75A5A']
ax.pie(data, labels=labels, autopct='%1.1f%%', startangle=90, colors=colors)
ax.axis('equal')
st.pyplot(fig)

# --------- 요약 ---------
st.subheader("요약")
st.write("선택한 플랫폼의 리뷰 중 광고성 리뷰가 다수 포착되었으며, 악성 리뷰 또한 일정 수 존재합니다. 사용자 판단에 유의가 필요합니다.")

# --------- 신뢰도 표시 ---------
confidence = random.randint(30, 100)  # 모의 신뢰도 점수

# 색상과 메시지 결정
if confidence >= 70:
    color = "blue"
elif confidence >= 50:
    color = "orange"
else:
    color = "red"

# HTML로 신뢰도 크게 표시
st.markdown(f"""
    <div style='text-align:center; padding-top:20px;'>
        <p style='font-size:18px;'>신뢰도는</p>
        <p style='font-size:54px; font-weight:bold; color:{color};'>{confidence}%</p>
        <p style='font-size:18px;'>입니다.</p>
    </div>
""", unsafe_allow_html=True)
