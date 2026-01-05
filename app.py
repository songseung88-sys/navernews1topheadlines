import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
# from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime
import time

# 1. 웹 앱 인터페이스 및 세션 설정
st.set_page_config(page_title="네이버 뉴스 1면 스크래퍼", page_icon="📰", layout="wide")
st.title("📰 네이버 뉴스 1면 제목 수집기")

# 세션 상태 초기화
if 'news_list' not in st.session_state:
    st.session_state.news_list = []
if 'last_scraped_date' not in st.session_state:
    st.session_state.last_scraped_date = ""

# 우선순위 리스트
priority_list = ["조선일보", "중앙일보", "동아일보", "한겨레", "경향신문", "한국일보", "세계일보", "문화일보", "매일경제", "한국경제"]

def get_news_data():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    
    # Streamlit Cloud 환경 설정
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
                link = card.find_element(By.CLASS_NAME, "offc_ct_wraplink").get_attribute("href")
                
                collected_news.append({
                    'name': media_name, 
                    'title': headline,
                    'link': link
                })
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

# --- 실행 버튼 부분 ---
if st.button("뉴스 수집 시작"):
    with st.spinner("데이터를 가져오는 중입니다..."):
        results = get_news_data()
        if results:
            st.session_state.news_list = results
            st.session_state.last_scraped_date = datetime.now().strftime("%Y.%m.%d.")
            st.success(f"{len(results)}개 매체를 수집했습니다!")
        else:
            st.error("데이터 수집에 실패했습니다.")

# --- 결과 출력 및 다운로드 부분 ---
if st.session_state.news_list:
    now = datetime.now()
    today_title = st.session_state.last_scraped_date
    
    # 1. 다운로드용 텍스트 생성 (여기에서 링크 부분을 제거했습니다)
    result_text = f"{today_title} 주요 지면 매체 1면 제목 스크랩\n\n"
    for news in st.session_state.news_list:
        result_text += f"[{news['name']}] {news['title']}\n\n" # 제목만 포함하고 한 줄 띄움

    # 2. 다운로드 버튼
    st.download_button(
        label="📁 메모장 파일(.txt)로 다운로드",
        data=result_text,
        file_name=f"naver_news_{now.strftime('%Y%m%d')}.txt",
        mime="text/plain"
    )
    
    st.divider()
    
    # 3. 웹 화면 본문 출력 (화면에서는 링크가 계속 보입니다)
    st.subheader(f"📍 {today_title} 수집 결과")
    for news in st.session_state.news_list:
        st.markdown(f"### **[{news['name']}]** {news['title']}")
        st.markdown(f"[지면보기 바로가기]({news['link']})")
        st.write("")

