import asyncio
import time
from selenium import webdriver
from selenium.webdriver.common.by import By

from camp_site_crawler import CampSiteCrawler


def reserve_site_main(site_list):
    if len(site_list) == 0:
        quit()
    else:
        print(site_list)
        url = 'https://m.thankqcamping.com/resv/search.hbb'

        driver = webdriver.Chrome('chromedriver.exe')
        driver.implicitly_wait(3)
        driver.get(url)

        driver.find_element(By.CSS_SELECTOR, '#spnResDtInfo > input').send_keys(site_list.pop(0))
        driver.find_element(By.ID, 'btn_detail_search').click()
        driver.find_element(By.CSS_SELECTOR, '#DivResvList > li:nth-child(2) > a > div.info').click();

        # 창 변환
        driver.switch_to.window(driver.window_handles[-1])
        time.sleep(3)

        driver.find_element(By.CSS_SELECTOR, '#container > div > div.fixed_btn > div > button').click()
        time.sleep(2)

        # 모달 팝업 닫기
        driver.switch_to.window(driver.window_handles[-1])
        driver.find_element(By.CLASS_NAME, 'btn_layerClose').click()
        # time.sleep(2)

        # 1일부터 말일까지 예약일자 확인하는 것!
        check_reservation(driver, site_list)


def check_reservation(driver, site_list, count=0, click=0):
    table = driver.find_element(By.CLASS_NAME, 'ui-datepicker-calendar')
    tbody = table.find_element(By.TAG_NAME, "tbody")
    rows = tbody.find_elements(By.TAG_NAME, "tr")
    # 예약사이트의 매월 첫날은 전달 마지막일일수 있다.
    first_day_check = ['28', '29', '30', '31']

    tr_disabled = []
    tr_possible = []

    # for 문으로 예약 가능한날짜 append하는 부분
    for index, row in enumerate(rows):
        # print(row.text)
        td = row.find_elements(By.TAG_NAME, 'td')
        for tmp in td:
            if tmp.get_attribute('class').find('-disabled') != -1:
                # print('disabled : ' + tmp.text)
                tr_disabled.append([index, tmp])
            else:
                tr_possible.append([index, tmp])

    if count < len(tr_possible) - 1:
        if int(tr_possible[count][1].text) + 1 == int(tr_possible[count + 1][1].text) or (count == 0 and tr_possible[count][1].text in first_day_check):
            # 처음시작하는 날짜가 마지막 날이고 1일이 아닐때!
            if tr_possible[count][0] > 3 and int(tr_possible[count][1].text) < 8:
                next_month_check(driver, site_list)
            else:
                if click % 2 == 1:
                    tr_possible[count][1].click()
                    click = 0
                    save_site_info(driver)
                    check_reservation(driver, site_list, count, click)
                else:
                    tr_possible[count][1].click()
                    click = click + 1
                    count = count + 1
                    check_reservation(driver, site_list, count, click)

        elif int(tr_possible[count][1].text) + 1 != int(tr_possible[count + 1][1].text):
            if click % 2 == 1:
                tr_possible[count][1].click()
                save_site_info(driver)
                click = 0
                count = count + 1
                check_reservation(driver, site_list, count, click)

            if int(tr_possible[count][1].text) > int(tr_possible[count + 1][1].text):
                next_month_check(driver, site_list)

    else:
        if click % 2 == 1:
            tr_possible[count][1].click()
            click = 0
            save_site_info(driver)

        next_month_check(driver, site_list)


def save_site_info(driver):
    # 선택한 날짜의 예약 가능한 사이트 리스트 저장
    site_info = driver.find_elements(By.CLASS_NAME, 'site_info')

    start_date = driver.find_element(By.CSS_SELECTOR, '#container > div > div.imply > div.section.calendar > div.view_date > div > div:nth-child(1) > div > span')
    end_date = driver.find_element(By.CSS_SELECTOR, '#sel_res_days > option:nth-child(2)')

    print(start_date.text)
    print(end_date.text)

    # 마지막 날짜 넣을때 n-1번째 보다 n번째 날이 더 클때는 무시하게 넣기!
    camping_possible_date = []  # [2022.04.01 - 2022.04.02, 2022.04.02 - 2022.04.03, ...]
    camping_possible_site = []  # [[가족형 1, 예약가능 1자리],[계곡파쇄석, 예약가능 3자리],[],[], ...]

    camping_possible_date.append(start_date.text + '-' + end_date.text)
    print(camping_possible_date)

    # list에다가 넣고
    # for site in site_info:
    #     if site.text.find('예약가능') != -1:
    #         print(site.text)
    #         print('--------------------------------------')
    #     else:
    #         print("예약 불가 : " + site.text)


def next_month_check(driver, site_list):
    # 다음달이 없는지 체크
    if driver.find_element(By.CSS_SELECTOR, '#DivCalendar > div > div > a.ui-datepicker-next.ui-corner-all').get_attribute('data-handler') == 'next':
        # 다음달로 넘어갈때!
        driver.find_element(By.CSS_SELECTOR, '#DivCalendar > div > div > a.ui-datepicker-next.ui-corner-all').click()
        time.sleep(2)
        count = 0
        click = 0
        check_reservation(driver, site_list, count, click)

    else:
        print("끝!")
        driver.quit()
        reserve_site_main(site_list)


def get_sub_region(_driver, _city) -> list:
    sub_region_list = []
    _city.click()
    time.sleep(2)
    for sub_cities in _driver.find_elements(By.ID, 'all_sub_region'):
        # print(_driver.find_elements(By.CSS_SELECTOR, '#li_sub_region'))
        sub_cities.click()
        find_location = ''
        # 삽질 지렸다... #li_sub_region이 많아서... 실제 선택되어있는놈을 찾아주는게 아래 for문;;
        for f_location in _driver.find_elements(By.CSS_SELECTOR, '#li_sub_region'):
            if f_location.get_attribute('style').find('display: block;') == 0:
                find_location = f_location

        for sub_region in find_location.find_elements(By.CLASS_NAME, 'wdh_sub'):
            sub_region.click()
            time.sleep(1)
            _driver.find_element(By.ID, 'btnSearch').click()
            _driver.switch_to.window(_driver.window_handles[-1])
            sub_region_list.append(_driver.current_url)
            _driver.close()
            _driver.switch_to.window(_driver.window_handles[-1])
            sub_region.click()
            # 강원군만 누르기
            # break
    # 강원권만 할라고 break 실제로는 빼기

    return sub_region_list


def get_site_list():
    url = 'https://m.thankqcamping.com/resv/regionSearch.hbb?site_tp='

    driver = webdriver.Chrome('chromedriver.exe')
    driver.implicitly_wait(3)

    result = []

    # 오토캠핑, 글램핑, 카라반, 펜션, 렌트, 캠프닉 url 만들어서 직접 호출함
    camp_type = ['BB000', 'BB001', 'BB002', 'BB003', 'BB004', 'BB006']
    # for camp in camp_type:
    #     campTypeUrl = url + camp
    #     print(campTypeUrl)
    #     driver.get(campTypeUrl)
    #     campTypeUrl=''
    #     time.sleep(1)

    # 오토캠핑장 1개만 가져오는거
    campTypeUrl = url + camp_type[0]
    driver.get(campTypeUrl)

    # city별 캠핑장 url 가져오기
    for city in driver.find_element(By.CSS_SELECTOR, '#container > div.area_wp > div.iscroll_1 > div > ul').find_elements(By.CSS_SELECTOR, 'li'):
        camp_site_crawler = CampSiteCrawler()
        camp_list = get_sub_region(driver, city)

        if len(camp_list) == 0:
            pass
        else:
            result = asyncio.run(camp_site_crawler.gether_sub_region(camp_list, result))
        # break

    return result
    # driver.switch_to.window(driver.window_handles[-1])
    # time.sleep(2)

    # while True:
    #     pass


if __name__ == "__main__":
    # TODO 캠핑장 site 정보 크롤링
    # site_list = ['무릉도원', '마의태자']
    # reserve_site_main(site_list)
    site_info = get_site_list()
    site_info = set(site_info)
    print(len(site_info))
    print(site_info)

