import streamlit as st
import requests
from bs4 import BeautifulSoup

# 크롤링 함수 정의
def extract_notice_data(url):
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')
    board_list = soup.select_one('.board-list-wrap ul')
    if not board_list:
        return "board-list-wrap not found or no data available."
    
    notices = []
    for li in board_list.find_all('li'):
        count = li.select_one('.count').get_text(strip=True) if li.select_one('.count') else None
        subject_tag = li.select_one('.subject a')
        subject = subject_tag.get_text(strip=True) if subject_tag else None
        link = subject_tag['href'] if subject_tag and 'href' in subject_tag.attrs else None
        if link and link.startswith('./'):
            link = link.replace('./', 'https://fsc.go.kr/')
        info_spans = li.select('.info span')
        info = {span.get_text(strip=True).split(" : ")[0]: span.get_text(strip=True).split(" : ")[1] for span in info_spans}
        day = li.select_one('.day').get_text(strip=True) if li.select_one('.day') else None
        
        notices.append({
            'count': count,
            'subject': subject,
            'link': link,
            'info': info,
            'date': day,
        })
    return notices

# Streamlit UI 구성
st.title("금융위원회 입법예고")
st.write("데이터가져오기")

# URL 하드코딩
url = "https://www.fsc.go.kr/po040301"

if st.button("데이터 가져오기"):
    try:
        notice_data = extract_notice_data(url)
        if isinstance(notice_data, str):  # 에러 메시지 처리
            st.error(notice_data)
        else:
            for notice in notice_data:
                with st.container():  # 컨테이너로 각 공지사항 구분
                    st.markdown(f"### {notice['subject']}")
                    st.write(f"**링크:** [바로가기]({notice['link']})")
                    st.write("**정보:**")
                    st.json(notice['info'])
                    st.write(f"**날짜:** {notice['date']}")
                    st.divider()
    except Exception as e:
        st.error(f"오류 발생: {e}")
