import asyncio
import time
from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By

from camp_site_crawler import CampSiteCrawler


def reserve_site_main(site_list):
    if len(site_list) == 0:
        quit()
    else:
        for site in site_list:
            url = 'https://m.thankqcamping.com/resv/view.hbb?cseq=' + site
            driver = webdriver.Chrome('chromedriver.exe')
            driver.implicitly_wait(3)
            driver.get(url)
            print(url)

            if driver.find_element(By.CSS_SELECTOR, '#wrap > div.btm_foot > div > ul > li.btn_wp > button > span').text.find('홈페이지') == -1:
                driver.find_element(By.CSS_SELECTOR, '#wrap > div.btm_foot > div > ul > li.btn_wp > button').click()
                time.sleep(1)
                try:
                    check_reservation(driver, 0, 0, True)
                except:
                    driver.quit()
            else:
                driver.quit()
                time.sleep(1)

        # url = 'https://m.thankqcamping.com/resv/view.hbb?cseq=' + site_list[0]
        #
        # driver = webdriver.Chrome('chromedriver.exe')
        # driver.implicitly_wait(3)
        # driver.get(url)
        #
        # driver.find_element(By.CSS_SELECTOR, '#spnResDtInfo > input').send_keys(site_list.pop(0))
        # driver.find_element(By.ID, 'btn_detail_search').click()
        # driver.find_element(By.CSS_SELECTOR, '#DivResvList > li:nth-child(2) > a > div.info').click();
        #
        # # 창 변환
        # driver.switch_to.window(driver.window_handles[-1])
        # time.sleep(3)
        #
        # driver.find_element(By.CSS_SELECTOR, '#container > div > div.fixed_btn > div > button').click()
        # time.sleep(2)
        #
        # # 모달 팝업 닫기
        # driver.switch_to.window(driver.window_handles[-1])
        # driver.find_element(By.CLASS_NAME, 'btn_layerClose').click()
        # # time.sleep(2)
        #
        # # 1일부터 말일까지 예약일자 확인하는 것!
        # check_reservation(driver, site_list)


def check_reservation(driver, count=0, click=0, first_come=False):
    time.sleep(1)

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
                # print('possi : ' + tmp.text)
                tr_possible.append([index, tmp])

    x = driver.find_element(By.XPATH, '//*[@id="DivCalendar"]/div/div/div').location.get('x')
    y = driver.find_element(By.XPATH, '//*[@id="DivCalendar"]/div/div/div').location.get('y') - 200
    if count < len(tr_possible) - 1:
        # print('count : ' + str(count))
        # print('click : ' + str(click))
        # print(driver.find_element(By.XPATH, '//*[@id="DivCalendar"]/div/div/div').location)

        # print('date : ' + tr_possible[count][1].text)
        # 연달아 있는날일때
        if int(tr_possible[count][1].text) + 1 == int(tr_possible[count + 1][1].text) or (count == 0 and tr_possible[count][1].text in first_day_check):
            # 처음시작하는 날짜가 마지막 날이고 1일이 아닐때!
            if tr_possible[count][0] > 3 and int(tr_possible[count][1].text) < 8:
                next_month_check(driver)
            else:
                if click % 2 == 1:
                    tr_possible[count][1].click()
                    click = 0
                    save_site_info(driver)
                    check_reservation(driver, count, click)
                else:
                    if not first_come:
                        # print('111111111111')
                        # driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.PAGE_UP)
                        time.sleep(1)
                        driver.execute_script(f"window.scrollTo('{x}', '{y}')")
                        time.sleep(2)
                    tr_possible[count][1].click()
                    time.sleep(1)
                    click = click + 1
                    count = count + 1
                    check_reservation(driver, count, click)

        # 연달아 있는날이 아닐때!
        elif int(tr_possible[count][1].text) + 1 != int(tr_possible[count + 1][1].text):
            # print("연달아 있는날 아님" + tr_possible[count][1].text)
            if click % 2 == 1:
                tr_possible[count][1].click()
                save_site_info(driver)
                click = 0
                count = count + 1
                check_reservation(driver, count, click)

            if int(tr_possible[count][1].text) > int(tr_possible[count + 1][1].text):
                time.sleep(1)
                driver.execute_script(f"window.scrollTo('{x}', '{y}')")
                # driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.PAGE_UP)
                time.sleep(2)
                # print('22222')
                next_month_check(driver)

    else:
        if click % 2 == 1:
            tr_possible[count][1].click()
            click = 0
            save_site_info(driver)

        # driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.PAGE_UP)
        time.sleep(2)
        driver.execute_script(f"window.scrollTo('{x}', '{y}')")
        time.sleep(2)
        next_month_check(driver)


def save_site_info(driver):
    # 선택한 날짜의 예약 가능한 사이트 리스트 저장
    site_info = driver.find_elements(By.CLASS_NAME, 'site_div')

    start_date = driver.find_element(By.CSS_SELECTOR, '#wrap > div.wrap_in > section.site_dtl_sec > div > div.view_date > div > div:nth-child(1) > div > span')
    end_date = driver.find_element(By.CSS_SELECTOR, '#sel_res_days > option:nth-child(2)')

    print(driver.current_url)
    print(start_date.text)
    print(end_date.text)

    # 마지막 날짜 넣을때 n-1번째 보다 n번째 날이 더 클때는 무시하게 넣기!
    camping_possible_date = []  # [2022.04.01 - 2022.04.02, 2022.04.02 - 2022.04.03, ...]
    camping_possible_site = []  # [[가족형 1, 예약가능 1자리],[계곡파쇄석, 예약가능 3자리],[],[], ...]

    camping_possible_date.append(start_date.text + '-' + end_date.text)
    print(camping_possible_date)

    # list에다가 넣고
    for site in site_info:
        if site.text.find('예약가능') != -1:
            print(site.text)
            reserve = site.text.split('\n')[0]
            position = site.text.split('\n')[1]
            ty = site.text.split('\n')[2]
            price = site.text.split('\n')[3]
            print('--------------------------------------')
            print(reserve + " : " + position + " : " + ty + " : " + price)
        else:
            print("예약 불가 : " + site.text)


def next_month_check(driver):
    # 다음달이 없는지 체크
    if driver.find_element(By.CSS_SELECTOR, '#DivCalendar > div > div > a.ui-datepicker-next.ui-corner-all').get_attribute('data-handler') == 'next':
        # 다음달로 넘어갈때!
        # time.sleep(100)
        driver.find_element(By.CSS_SELECTOR, '#DivCalendar > div > div > a.ui-datepicker-next.ui-corner-all').click()
        time.sleep(2)
        count = 0
        click = 0
        check_reservation(driver, count, click, True)

    else:
        print("끝!")
        # driver.quit()
        # reserve_site_main(site_list)


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
            # _driver.close()
            scroll_location = _driver.execute_script("return document.body.scrollHeight")
            while True:
                # 현재 스크롤의 가장 아래로 내림
                _driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
                # 전체 스크롤이 늘어날 때까지 대기
                time.sleep(5)
                # 늘어난 스크롤 높이
                scroll_height = _driver.execute_script("return document.body.scrollHeight")
                # 늘어난 스크롤 위치와 이동 전 위치 같으면(더 이상 스크롤이 늘어나지 않으면) 종료
                if scroll_location == scroll_height:
                    break
                    # 같지 않으면 스크롤 위치 값을 수정하여 같아질 때까지 반복
                else:
                    # 스크롤 위치값을 수정
                    scroll_location = _driver.execute_script("return document.body.scrollHeight")

            for aa in _driver.find_elements(By.CLASS_NAME, 'camp_div'):
                # print(len(aa.find_element(By.CSS_SELECTOR, 'a').get_attribute('href').split(',')))
                if len(aa.find_element(By.CSS_SELECTOR, 'a').get_attribute('href').split(',')) == 3:
                    # print(aa.find_element(By.CSS_SELECTOR, 'a').get_attribute('href').split(',')[1])
                    sub_region_list.append('https://m.thankqcamping.com/resv/view.hbb?cseq=' +
                                           aa.find_element(By.CSS_SELECTOR, 'a').get_attribute('href').split(',')[1])
                else:
                    # print(aa.find_element(By.CSS_SELECTOR, 'a').get_attribute('href').split(',')[0].split('(')[1])
                    sub_region_list.append('https://m.thankqcamping.com/resv/view.hbb?cseq=' +
                                           aa.find_element(By.CSS_SELECTOR, 'a').get_attribute('href').split(',')[0].split('(')[1])
            _driver.back()
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
    # 업데이트되면서 사라짐
    # camp_type = ['BB000', 'BB001', 'BB002', 'BB003', 'BB004', 'BB006']
    # for camp in camp_type:
    #     campTypeUrl = url + camp
    #     print(campTypeUrl)
    #     driver.get(campTypeUrl)
    #     campTypeUrl=''
    #     time.sleep(1)

    # 오토캠핑장 1개만 가져오는거
    # campTypeUrl = url + camp_type[0]
    driver.get(url)

    # city별 캠핑장 url 가져오기
    for city in driver.find_element(By.CSS_SELECTOR, '#wrap > div > div.container > div > div.iscroll_1 > div > ul').find_elements(By.CSS_SELECTOR, 'li'):
        camp_site_crawler = CampSiteCrawler()
        # 페이지가 리뉴얼 되면서 한번에 모든 list를 순차적으로 가져오게 바뀜...
        # camp_list = get_sub_region(driver, city)
        result.extend(get_sub_region(driver, city))
        print(result)

        # if len(camp_list) == 0:
        #     pass
        # else:
        #     # result = asyncio.run(camp_site_crawler.gether_sub_region(camp_list, result))
        #     result = camp_site_crawler.gether_sub_region(camp_list, result)
        # break

    return result
    # driver.switch_to.window(driver.window_handles[-1])
    # time.sleep(2)

    # while True:
    #     pass


def read_camp_file():
    f = open('site_list.txt', 'r')
    a = f.readlines()
    f.close()

    b = []
    for line in a:
        line = line.strip()
        line = line.strip('{')
        line = line.strip('}')
        b.append(line)

    site_count = b[0]
    strings = b[1].split(',')
    strings = list(map(lambda x: x.replace("'", ''), strings))
    return site_count, strings


if __name__ == "__main__":
    # 캠핑장 list 가져오는 part
    # site_info = get_site_list()
    # print(len(site_info))
    # print(site_info)
    # site_info = set(site_info)
    # f = open('site_list.txt', 'w')
    # f.write(str(len(site_info)))
    # f.write('\n')
    # f.write(str(site_info))
    # f.close()


    # 캠장정보 읽어오기
    s_count, camp_url = read_camp_file()
    site_list = []

    # 예약 가능일 가져오는 part
    for cseq in camp_url:
        site_list.append(cseq.split('cseq=')[1])
    reserve_site_main(site_list)

    # print(s_count)
    # print(camp_url)

    # 캠핑장 상세정보 가져오는 부분
    # camp_site_crawler = CampSiteCrawler()
    # camp_site_crawler.camp_site_info(camp_url)
