import time

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By

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

table = driver.find_element(By.CLASS_NAME, 'ui-datepicker-calendar')
tbody = table.find_element(By.TAG_NAME, "tbody")
rows = tbody.find_elements(By.TAG_NAME, "tr")

# print(rows[0].find_elements(By.CLASS_NAME, 'date-disabled')[0].text)
# print(rows[0].find_elements(By.CLASS_NAME, 'date-disabled')[1].text)
# print(rows[0].find_elements(By.CLASS_NAME, 'date-disabled')[2].text)
tr_disabled = []
tr_possible = []

for index, row in enumerate(rows):
    td = row.find_elements(By.TAG_NAME, 'td')
    # 캠장 예약 가능한 날짜 보관하는 list

    # tr_disabled += row.find_elements(By.CLASS_NAME, 'date-disabled')

    for tmp in td:
        # print(tmp.get_attribute('class').find('date-disabled') or tmp.get_attribute('class').find('ui-state-disabled'))
        if tmp.get_attribute('class').find('date-disabled') != -1:
            # print(tmp.text)
            tr_disabled.append(tmp)
        else:
            # print('posi : ' + tmp.text)
            tr_possible.append(tmp)

tr_possible[-2].click()

# TODO 페이지가 새로고처지는 바람에 이런일이 발생하는데... 중복 되는 코드를 줄일 방법을 찾아보기...
table = driver.find_element(By.CLASS_NAME, 'ui-datepicker-calendar')
tbody = table.find_element(By.TAG_NAME, "tbody")
rows = tbody.find_elements(By.TAG_NAME, "tr")

tr_disabled = []
tr_possible = []

for index, row in enumerate(rows):
    td = row.find_elements(By.TAG_NAME, 'td')
    # 캠장 예약 가능한 날짜 보관하는 list

    # tr_disabled += row.find_elements(By.CLASS_NAME, 'date-disabled')

    for tmp in td:
        # print(tmp.get_attribute('class').find('date-disabled') or tmp.get_attribute('class').find('ui-state-disabled'))
        if tmp.get_attribute('class').find('date-disabled') != -1:
            # print(tmp.text)
            tr_disabled.append(tmp)
        else:
            # print('posi : ' + tmp.text)
            tr_possible.append(tmp)

# for a in tr_possible:
#     print(a)

tr_possible[-1].click()

a = driver.find_elements(By.CLASS_NAME, 'site_info')

start_date = driver.find_element(By.CSS_SELECTOR, '#container > div > div.imply > div.section.calendar > div.view_date > div > div:nth-child(1) > div > span')
end_date = driver.find_element(By.CSS_SELECTOR, '#sel_res_days > option:nth-child(2)')

print(start_date.text)
print(end_date.text)

for b in a:
    if b.text.find('예약완료') == -1:
        print(b.text)
        print('--------------------------------------')

while (True):
    pass
