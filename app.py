import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime
import time

# 웹 앱 인터페이스 설정
st.set_page_config(page_title="네이버 뉴스 1면 스크래퍼", page_icon="📰")
st.title("📰 네이버 뉴스 1면 제목 수집기")
st.write("버튼을 누르면 주요 언론사의 1면 헤드라인을 수집하여 정리해 드립니다.")

# 우선순위 리스트
priority_list = ["조선일보", "중앙일보", "동아일보", "한겨레", "경향신문", "한국일보", "세계일보", "문화일보", "매일경제", "한국경제"]


def get_news_data():
    # 브라우저 설정 (웹 서버 환경을 위한 필수 설정)
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # 서버에서는 화면을 띄울 수 없으므로 필수
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    try:
        url = "https://news.naver.com/newspaper/home?viewType=pc"
        driver.get(url)
        wait = WebDriverWait(driver, 15)
        cards = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "offc_item")))

        collected_news = []
        for card in cards:
            try:
                media_name = card.find_element(By.CLASS_NAME, "offc_logo_text").text.strip()
                headline = card.find_element(By.CLASS_NAME, "title").text.strip()
                collected_news.append({'name': media_name, 'title': headline})
            except:
                continue

        # 정렬 로직
        priority_group = sorted([item for item in collected_news if item['name'] in priority_list],
                                key=lambda x: priority_list.index(x['name']))
        others_group = sorted([item for item in collected_news if item['name'] not in priority_list],
                              key=lambda x: x['name'])

        return priority_group + others_group

    finally:
        driver.quit()


# 실행 버튼
if st.button("뉴스 수집 시작"):
    with st.spinner("네이버 뉴스를 읽어오는 중입니다... 잠시만 기다려주세요."):
        final_list = get_news_data()

        if final_list:
            now = datetime.now()
            today_title = now.strftime("%Y.%m.%d.")

            # 결과 텍스트 생성
            result_text = f"{today_title} 주요 지면 매체 1면 제목 스크랩\n\n"
            for news in final_list:
                result_text += f"[{news['name']}] {news['title']}\n\n"

            # 웹 화면에 미리보기 출력
            st.success(f"성공적으로 {len(final_list)}개 매체를 수집했습니다!")
            st.text_area("미리보기", result_text, height=300)

            # 다운로드 버튼
            st.download_button(
                label="📁 메모장 파일(.txt)로 저장하기",
                data=result_text,
                file_name=f"naver_news_{now.strftime('%Y%m%d')}.txt",
                mime="text/plain"
            )
        else:
            st.error("데이터를 가져오지 못했습니다. 다시 시도해 주세요.")