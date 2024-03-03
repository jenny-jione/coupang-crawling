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


if __name__ == "__main__":
    
    options = webdriver.ChromeOptions()
    # options.add_argument('headless')
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    # 쿠팡 크롤링 방지 설정을 undefined로 변경
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {"source": """ Object.defineProperty(navigator, 'webdriver', { get: () => undefined }) """})
    
    url = 'https://login.coupang.com/login/login.pang?login_challenge=37f17d5f8200421e87d212a057965818'
    driver.get(url)

    # 로그인
    driver.find_element(By.ID, "login-email-input").send_keys(C_ID)
    driver.find_element(By.ID, "login-password-input").send_keys(C_PW)
    driver.find_element(By.CLASS_NAME, "login__button.login__button--submit._loginSubmitButton.login__button--submit-rds").click()
    time.sleep(2)

    # 마이페이지 > 주문목록
    # url_mypage = 'https://mc.coupang.com/ssr/desktop/order/list'
    # driver.get(url_mypage)

    # 년도별 주문목록
    # for i in range(2024, 2018, -1):
    #     print(i)
    url_year = 'https://mc.coupang.com/ssr/desktop/order/list?orderType=ALL&requestYear=2024'
    driver.get(url_year)
    time.sleep(0.3)

    div_order_elements = driver.find_element(By.CLASS_NAME, "sc-qxzqk9-0.iQgKJk")
    time.sleep(0.3)
    print('주문목록 div 찾음.')

    order_elements = div_order_elements.find_elements(By.XPATH, "./child::div")
    print('일자별 주문목록 div 찾음.')

    for order_element in order_elements[:-1]:
        # 주문 날짜 - 일자별. div class="sc-abukv2-1 kSZYgn"
        kSZYgn = order_element.find_element(By.CSS_SELECTOR, "div")
        order_date = kSZYgn.find_element(By.CSS_SELECTOR, "div").text
        print(order_date)
        # 주문 항목. tr 한 개당 주문상품 한 개.
        # 같은 날짜에 여러 상품을 주문한 경우 tr도 여러개임. tr class="sc-gnmni8-3 gmGnuU"
        gmGnuU = order_element.find_element(By.CSS_SELECTOR, "tr")
        # 하나의 tr은 2개의 td로 이루어져 있음. (제품정보덩어리, 배송조회/교환반품신청/리뷰작성)
        # td class="sc-gnmni8-5 hUzAOG"
        hUzAOG = gmGnuU.find_elements(By.CSS_SELECTOR, "td")[0]
        a_tags = hUzAOG.find_elements(By.CSS_SELECTOR, "a")
        print(type(a_tags))
        print(len(a_tags))
        product_name = a_tags[2].text
        product_price = a_tags[4].find_element(By.CSS_SELECTOR, "span").text

        print(product_name)
        print(product_price)

    driver.quit()


"""
TODO
1. 년도별 넘어가기
  1-1) 지금은 2019년이 최대이므로 range로 범위 지정해주기
2. 같은 년도에서 페이지 넘어가기
  2-1) '다음'이 disabled일 때까지 넘어가야 함
"""