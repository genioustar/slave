import time
from selenium import webdriver
from selenium.webdriver.common.by import By


def main(site_list):
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
        print('count : ' + str(count))
        print('len : ' + str(len(tr_possible)))
        print('posi_tr : ' + tr_possible[count][1].text)
        print('posi_tr_idx : ' + str(tr_possible[count]))
        if int(tr_possible[count][1].text) + 1 == int(tr_possible[count + 1][1].text) or (count == 0 and tr_possible[count][1].text in first_day_check):
            # 처음시작하는 날짜가 마지막 날이고 1일이 아닐때!
            if tr_possible[count][0] > 3 and int(tr_possible[count][1].text) < 8:
                next_month_check(driver, site_list)
            else:
                print('33333')
                if click % 2 == 1:
                    print('4444444')
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
                print('123123')
                tr_possible[count][1].click()
                save_site_info(driver)
                click = 0
                count = count + 1
                check_reservation(driver, site_list, count, click)

            if int(tr_possible[count][1].text) > int(tr_possible[count + 1][1].text):
                print('22222')
                next_month_check(driver, site_list)

    else:
        print('count11 : ' + str(count))
        print('len11 : ' + str(len(tr_possible)))
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
        main(site_list)


if __name__ == "__main__":
    # TODO 캠핑장 site 정보 크롤링
    site_list = ['무릉도원', '마의태자']
    main(site_list)
