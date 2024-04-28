# 로그인 후 사용자의 주문목록을 크롤링하는 코드 (2024.3.3)
"""
크롤링할 정보
1. 구매한 상품이름
2. 구매가격
3. 구입날짜
4. 배송된 제품인지 취소한 제품인지.
"""

import os
from dotenv import load_dotenv

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

import time
from datetime import datetime
import csv

load_dotenv(verbose=True)

C_ID = os.getenv('C_ID')
C_PW = os.getenv('C_PW')


def get_page_data(driver: webdriver.Chrome):
    """
    크롤링 코드.

    disabled를 발견했다면
        next page는 없는 것.
    리턴값
    last_page 여부, 크롤링한 데이터
    """

    # 주문목록 div
    div_order_elements = driver.find_element(By.CLASS_NAME, "sc-qxzqk9-0.iQgKJk")
    time.sleep(0.3)

    # 일자별 주문상품목록 div
    order_elements = div_order_elements.find_elements(By.XPATH, "./child::div")

    result = []
    for order_element in order_elements[:-1]:
        # 주문 날짜 - 일자별. div class="sc-abukv2-1 kSZYgn"
        kSZYgn = order_element.find_element(By.CSS_SELECTOR, "div")
        order_date = kSZYgn.find_element(By.CSS_SELECTOR, "div").text
        # 주문 항목. tr 한 개당 주문상품 한 개.
        # 같은 날짜에 여러 상품을 주문한 경우 tr도 여러개임. tr class="sc-gnmni8-3 gmGnuU"
        trs = order_element.find_elements(By.CSS_SELECTOR, "tr")

        for tr in trs:
            # 하나의 tr은 2개의 td로 이루어져 있음. (제품정보덩어리, 배송조회/교환반품신청/리뷰작성)
            # td class="sc-gnmni8-5 hUzAOG"
            hUzAOG = tr.find_elements(By.CSS_SELECTOR, "td")[0]
            # sc-ki5ja7-0 bQVZKC
            delivery_status = hUzAOG.find_element(By.CLASS_NAME, "sc-ki5ja7-1.krPkOP").text.split()[0]
            a_tags = hUzAOG.find_elements(By.CSS_SELECTOR, "a")
            product_name = a_tags[2].text
            product_price = a_tags[4].find_element(By.CSS_SELECTOR, "span").text
            processed_price = product_price.replace(' 원', '').replace(',', '')
            processed_date = order_date.replace(' 주문', '')
            result.append([product_name, processed_price, processed_date, delivery_status])
    
    # 현재 페이지에서 다음 버튼이 disabled일 경우 이를 변수에 기록한다.
    # 다음 버튼 찾기
    next_btn = div_order_elements.find_elements(By.CLASS_NAME, "sc-1k9quwu-0.fwNiMs.sc-1o307be-1.dTwpud")[1]
    button_html = next_btn.get_attribute('outerHTML')
    if 'disabled' in button_html:
        last_page = True
    else:
        last_page = False

    return last_page, result


def save_file(data: list):
    today_str = datetime.today().strftime('%Y-%m-%d')
    with open(f'result_{today_str}.csv', 'w') as f:
        wr = csv.writer(f)
        header = ['product_name', 'product_price', 'order_date', 'status']
        wr.writerow(header)
        for row in data:
            wr.writerow(row)


if __name__ == "__main__":
    
    options = webdriver.ChromeOptions()
    # headless 옵션을 추가하는 순간 계속 NoSuchElementException이 뜨는데 이 둘이 연관이 있나??? 그럴리가 없는데..
    # options.add_argument('headless')
    # 창의 위치
    options.add_argument("--window-position=1000,600")
    # 창의 크기
    options.add_argument("--window-size=100,50")

    # 
    print('option :: headless')
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    # 쿠팡 크롤링 방지 설정을 undefined로 변경
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {"source": """ Object.defineProperty(navigator, 'webdriver', { get: () => undefined }) """})
    
    url = 'https://login.coupang.com/login/login.pang?login_challenge=37f17d5f8200421e87d212a057965818'
    driver.get(url)
    print('driver get url')
    print('finding login element ... ')
    driver.implicitly_wait(3)

    # 로그인
    driver.find_element(By.ID, "login-email-input").send_keys(C_ID)
    driver.find_element(By.ID, "login-password-input").send_keys(C_PW)
    driver.find_element(By.CLASS_NAME, "login__button.login__button--submit._loginSubmitButton.login__button--submit-rds").click()
    time.sleep(3)

    # 마이페이지 > 주문목록
    # url_mypage = 'https://mc.coupang.com/ssr/desktop/order/list'
    # driver.get(url_mypage)

    result = []
    # 년도별 주문목록
    for year in range(2024, 2019, -1):
    # for year in range(2024, 2023, -1):
        print(f'<year {year}> crawling ... ')
        page_index = 0
        last_page = False
        while(not last_page):
            print(f' page {page_index} crawling ..')
            url_year = f'https://mc.coupang.com/ssr/desktop/order/list?orderType=ALL&pageIndex={page_index}&requestYear={year}'
            driver.get(url_year)
            time.sleep(0.3)
            last_page, data = get_page_data(driver=driver)
            print(f' crawled data count: {len(data)}')
            result.extend(data)
            page_index += 1
    
    print('crawling finished.')

    save_file(result)
    print(f'saving {len(result)} data finished.')

    driver.quit()


"""
TODO
1. (완료) 년도별 넘어가기
  1-1) 지금은 2019년이 최대이므로 range로 범위 지정해주기
2. (완료) 같은 년도에서 페이지 넘어가기
  2-1) '다음'이 disabled일 때까지 넘어가야 함
3. (완료) product_price, order_date 크롤링 데이터 전처리 ('원', '주문' 등 실제 데이터가 아닌 것들 제거)
4. 배송완료/반품완료가 혼재함. 이에 대한 정보도 필요.
5. (완료) 각 날짜별로 첫번째 상품만 크롤링되고 있음!!!!
  5-1) 같은 날 2개 이상 구매했을 경우 가장 위의 상품 1개만 크롤링되는 경우 고치기 -> tr을 find_elements로 해서 반복문
6. 배송완료날짜도 크롤링 데이터에 추가할지?
7. README.md 파일 추가
"""