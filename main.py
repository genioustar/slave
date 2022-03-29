import time

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By


def check_reservation(count=0):
    table = driver.find_element(By.CLASS_NAME, 'ui-datepicker-calendar')
    tbody = table.find_element(By.TAG_NAME, "tbody")
    rows = tbody.find_elements(By.TAG_NAME, "tr")

    for index, row in enumerate(rows):
        td = row.find_elements(By.TAG_NAME, 'td')
        # 캠장 예약 가능한 날짜 보관하는 list

        # tr_disabled += row.find_elements(By.CLASS_NAME, 'date-disabled')

        for tmp in td:
            # print(tmp.get_attribute('class').find('date-disabled') or tmp.get_attribute('class').find('ui-state-disabled'))
            if tmp.get_attribute('class').find('-disabled') != -1:
                # print(tmp.text)
                tr_disabled.append(tmp)
            else:
                # print('posi : ' + tmp.text)
                tr_possible.append(tmp)

    tr_possible[count - 2].click()

    if count == 0:
        print(count)
        count = count + 1
        check_reservation(count)
    
    # 선택한 날짜의 예약 가능한 사이트 리스트 저장
    a = driver.find_elements(By.CLASS_NAME, 'site_info')

    start_date = driver.find_element(By.CSS_SELECTOR, '#container > div > div.imply > div.section.calendar > div.view_date > div > div:nth-child(1) > div > span')
    end_date = driver.find_element(By.CSS_SELECTOR, '#sel_res_days > option:nth-child(2)')

    print(start_date.text)
    print(end_date.text)

    # 마지막 날짜 넣을때 n-1번째 보다 n번째 날이 더 클때는 무시하게 넣기!
    camping_possible_date = []  # [2022.04.01 - 2022.04.02, 2022.04.02 - 2022.04.03, ...]
    camping_possible_site = []  # [[가족형 1, 예약가능 1자리],[계곡파쇄석, 예약가능 3자리],[],[], ...]

    # list에다가 넣고
    for b in a:
        if b.text.find('예약가능') != -1:
            print(b.text)
            print('--------------------------------------')
        else:
            print("예약 불가 : " + b.text)

    time.sleep(2)


url = 'https://m.thankqcamping.com/resv/search.hbb'

driver = webdriver.Chrome('chromedriver.exe')
driver.implicitly_wait(3)
driver.get(url)

driver.find_element(By.CSS_SELECTOR, '#spnResDtInfo > input').send_keys('무릉도원')
driver.find_element(By.ID, 'btn_detail_search').click()
driver.find_element(By.CSS_SELECTOR, '#DivResvList > li:nth-child(2) > a > div.info').click();

# 창 변환
driver.switch_to.window(driver.window_handles[-1])
time.sleep(3)

driver.find_element(By.CSS_SELECTOR, '#container > div > div.fixed_btn > div > button').click()
time.sleep(2)

# 모달 팝업 닫기
driver.switch_to.window(driver.window_handles[-1])
# time.sleep(2)
driver.find_element(By.CLASS_NAME, 'btn_layerClose').click()

tr_disabled = []
tr_possible = []

# 1일부터 말일까지 예약일자 확인하는 것!
check_reservation()

# 다음달로 넘어갈때!
driver.find_element(By.CSS_SELECTOR, '#DivCalendar > div > div > a.ui-datepicker-next.ui-corner-all').click()
time.sleep(2)

tr_disabled = []
tr_possible = []

table = driver.find_element(By.CLASS_NAME, 'ui-datepicker-calendar')
tbody = table.find_element(By.TAG_NAME, "tbody")
rows = tbody.find_elements(By.TAG_NAME, "tr")

for index, row in enumerate(rows):
    td = row.find_elements(By.TAG_NAME, 'td')

    for tmp in td:
        if tmp.get_attribute('class').find('-disabled') != -1:
            print(tmp.text)
            tr_disabled.append(tmp)
        else:
            print('posi : ' + tmp.text)
            tr_possible.append(tmp)

while (True):
    pass
