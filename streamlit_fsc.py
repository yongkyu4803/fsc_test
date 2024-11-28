import requests
from bs4 import BeautifulSoup
import streamlit as st

def extract_notice_data(url):
    # URL 요청 및 응답 처리
    response = requests.get(url)
    response.raise_for_status()  # 요청 실패 시 예외 발생

    # HTML 파싱
    soup = BeautifulSoup(response.text, 'html.parser')

    # board-list-wrap 클래스 내 ul > li 요소 추출
    board_list = soup.select_one('.board-list-wrap ul')
    if not board_list:
        return "board-list-wrap not found or no data available."

    # li 태그를 데이터로 처리
    notices = []
    for li in board_list.find_all('li'):
        # 데이터 추출
        count = li.select_one('.count').get_text(strip=True) if li.select_one('.count') else None
        subject_tag = li.select_one('.subject a')
        subject = subject_tag.get_text(strip=True) if subject_tag else None
        link = subject_tag['href'] if subject_tag and 'href' in subject_tag.attrs else None
        if link and link.startswith('./'):
            link = link.replace('./', 'https://fsc.go.kr/')
        info_spans = li.select('.info span')
        info = {span.get_text(strip=True).split(" : ")[0]: span.get_text(strip=True).split(" : ")[1] for span in info_spans}
        day = li.select_one('.day').get_text(strip=True) if li.select_one('.day') else None

    
        # 데이터 집합 생성
        notices.append({
            'count': count,
            'subject': subject,
            'link': link,
            'info': info,
            'date': day,
        })
    return notices

# Streamlit 인터페이스 설정
st.title("FSC 공지사항 데이터 크롤링")

# URL 입력
url = st.text_input("크롤링할 URL을 입력하세요:", "https://www.fsc.go.kr/po040301")

if st.button("데이터 가져오기"):
    try:
        # 데이터 크롤링
        notice_data = extract_notice_data(url)

        if isinstance(notice_data, str):  # 에러 메시지 처리
            st.error(notice_data)
        else:
            # 데이터 출력
            for notice in notice_data:
                st.subheader(notice['subject'])
                st.write(f"**링크:** {notice['link']}")
                st.write(f"**정보:** {notice['info']}")
                st.write(f"**날짜:** {notice['date']}")
                st.markdown("---")
    except Exception as e:
        st.error(f"오류 발생: {e}")
