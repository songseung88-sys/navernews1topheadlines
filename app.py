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

# 1. 웹 앱 인터페이스 설정
st.set_page_config(page_title="네이버 뉴스 1면 스크래퍼", page_icon="📰", layout="wide")
st.title("📰 네이버 뉴스 1면 제목 수집기")
st.info("주요 언론사의 1면 헤드라인을 수집하여 가공 없이 본문에 바로 보여드립니다.")

# 우선순위 리스트
priority_list = ["조선일보", "중앙일보", "동아일보", "한겨레", "경향신문", "한국일보", "세계일보", "문화일보", "매일경제", "한국경제"]

def get_news_data():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    
    # Streamlit Cloud 환경 설정 (지난번 에러 해결책 유지)
    chrome_options.binary_location = "/usr/bin/chromium"
    service = Service("/usr/bin/chromedriver")
    
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
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

# --- 실행 부분 ---
if st.button("뉴스 수집 시작"):
    with st.spinner("데이터를 가져오는 중입니다..."):
        final_list = get_news_data()
        
        if final_list:
            now = datetime.now()
            today_title = now.strftime("%Y.%m.%d.")
            
            # 1. 파일 저장용 텍스트 미리 생성 (다운로드 버튼용)
            result_text = f"{today_title} 주요 지면 매체 1면 제목 스크랩\n\n"
            for news in final_list:
                result_text += f"[{news['name']}] {news['title']}\n\n"

            # 2. 다운로드 버튼을 결과 '위'에 배치
            st.success(f"{len(final_list)}개 매체의 제목을 수집했습니다.")
            st.download_button(
                label="📁 메모장 파일(.txt)로 다운로드",
                data=result_text,
                file_name=f"naver_news_{now.strftime('%Y%m%d')}.txt",
                mime="text/plain"
            )
            
            st.divider() # 구분선 추가
            
            # 3. 결과 본문 출력 (스크롤 박스 없이 하나씩 출력)
            # 메인 창 스크롤을 이용하도록 개별 write 문 사용
            st.subheader(f"📍 {today_title} 수집 결과")
            
            for news in final_list:
                # 가공된 텍스트를 하나씩 화면에 뿌려줌
                st.markdown(f"**[{news['name']}]** {news['title']}")
                # 행 사이 간격을 위해 약간의 여백(마진)을 줌
                st.write("") 
                
        else:
            st.error("데이터 수집에 실패했습니다. 잠시 후 다시 시도해 주세요.")
