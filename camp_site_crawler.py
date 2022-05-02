import asyncio
import time
import json
from collections import OrderedDict
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By


class CampSiteCrawler:

    async def get_camp_site_url(self, param, result):
        url = param
        driver = webdriver.Chrome('chromedriver.exe')
        driver.implicitly_wait(3)
        driver.get(url)

        # htmslDoc = driver.page_source
        #
        # soup = BeautifulSoup(htmslDoc, 'html.parser')
        # # print(soup.find('form', {'name': 'form'}).select('input'))
        # url_parms = {}
        # for f in soup.find('form', {'name': 'form'}).select('input'):
        #     url_parms[f.get('name')] = f.get('name')
        #
        # print(url_parms)

        scroll_location = driver.execute_script("return document.body.scrollHeight")
        while True:
            # 현재 스크롤의 가장 아래로 내림
            driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
            # 전체 스크롤이 늘어날 때까지 대기
            await asyncio.sleep(5)
            # 늘어난 스크롤 높이
            scroll_height = driver.execute_script("return document.body.scrollHeight")
            # 늘어난 스크롤 위치와 이동 전 위치 같으면(더 이상 스크롤이 늘어나지 않으면) 종료
            if scroll_location == scroll_height:
                break
                # 같지 않으면 스크롤 위치 값을 수정하여 같아질 때까지 반복
            else:
                # 스크롤 위치값을 수정
                scroll_location = driver.execute_script("return document.body.scrollHeight")

        for aa in driver.find_elements(By.CLASS_NAME, 'item'):
            # print(len(aa.find_element(By.CSS_SELECTOR, 'a').get_attribute('href').split(',')))
            if len(aa.find_element(By.CSS_SELECTOR, 'a').get_attribute('href').split(',')) == 3:
                # print(aa.find_element(By.CSS_SELECTOR, 'a').get_attribute('href').split(',')[1])
                result.append('https://m.thankqcamping.com/resv/view.hbb?cseq=' +
                              aa.find_element(By.CSS_SELECTOR, 'a').get_attribute('href').split(',')[1])
            else:
                # print(aa.find_element(By.CSS_SELECTOR, 'a').get_attribute('href').split(',')[0].split('(')[1])
                result.append('https://m.thankqcamping.com/resv/view.hbb?cseq=' +
                              aa.find_element(By.CSS_SELECTOR, 'a').get_attribute('href').split(',')[0].split('(')[1])

    async def gether_sub_region(self, siteList, result):
        tmpList = []
        for url in siteList:
            tmpList.append(self.get_camp_site_url(url, result))
            # break

        await asyncio.wait(tmpList)
        print(len(result))
        print(result)
        return result

    def camp_site_info(self, urls):
        driver = webdriver.Chrome('chromedriver.exe')
        driver.implicitly_wait(3)
        # camp_info_list = []
        json_data = OrderedDict()
        try:
            for url in urls:
                driver.get(url)
                driver.execute_script("window.scrollTo(0,700)")
                print(url.split('cseq=')[1])
                temp_camp_info = {}
                camp_info_list = {}
                indexing = ['camp_type', 'amenity', 'available', 'leisure']

                temp_list = []
                # 사진
                for img in driver.find_elements(By.CSS_SELECTOR, '#wrap > div.wrap_in > div.container > section > div.swiper-container.ci_top_swiper > ul > li > a'):
                    temp_list.append(img.find_element(By.CSS_SELECTOR, 'img').get_attribute('src'))
                # 동영상
                for img in driver.find_elements(By.CSS_SELECTOR, '#wrap > div.wrap_in > div.container > section > div.swiper-container.ci_top_swiper > ul > li > div > iframe'):
                     temp_list.append(img.get_attribute('src'))
                temp_camp_info['img'] = temp_list


                if driver.find_element(By.CSS_SELECTOR, '#wrap > div.wrap_in > div.container > section').get_attribute('class').find('tip_set'):
                    temp_camp_info['tip'] = driver.find_element(By.CSS_SELECTOR, '#wrap > div.wrap_in > div.container > section > div.txt_box > div.tip_set').text.replace('\n', ',')

                temp_camp_info['site_name'] = driver.find_element(By.CSS_SELECTOR, '#wrap > div.wrap_in > div.container > section > div.txt_box > p').text
                temp_camp_info['tel'] = driver.find_element(By.CLASS_NAME, 'tel').text
                temp_camp_info['address'] = driver.find_element(By.CLASS_NAME, 'addr').text
                temp_camp_info['fee'] = driver.find_element(By.CLASS_NAME, 'pri').text
                # 소개글처리
                if driver.find_element(By.CSS_SELECTOR, '#wrap > div.wrap_in > div.container').get_attribute('class').find('ci_top_sec') != -1:
                    camp_info_list['intro'] = driver.find_element(By.CSS_SELECTOR, '#wrap > div.wrap_in > section.ci_intro_sec > div > div.txt').text

                for camp_data in driver.find_elements(By.CSS_SELECTOR, '#wrap > div.wrap_in > section.use_info_sec > div > div.dtl_info > ul > li'):
                    dl = camp_data.find_element(By.CSS_SELECTOR, 'dl')
                    dt = dl.find_elements(By.TAG_NAME, 'dt')
                    dd = dl.find_elements(By.TAG_NAME, 'dd')

                    if dt[0].text =='관련 사이트':
                        temp_camp_info[dt[0].text] = dd[0].text
                        camp_info_list['summary'] = temp_camp_info
                    elif dt[0].text == '':
                        temp_camp_info['관련 사이트'] = ''
                        camp_info_list['summary'] = temp_camp_info
                    else:
                        str = ''
                        for idx in range(len(dd)):
                            str +=dd[idx].text + ','
                        camp_info_list[dt[0].text] = str.strip(',')

                for a in driver.find_elements(By.CSS_SELECTOR, '#wrap > div.wrap_in > section.use_info_sec > div > div'):
                    # 예약가능한 사이트일 경우 예약정보 크롤링
                    if a.get_attribute('class').find('res_info') != -1:
                        temp_camp_info = {}
                        for camp_data in driver.find_elements(By.CSS_SELECTOR, '#wrap > div.wrap_in > section.use_info_sec > div > div.res_info > ul > li'):
                            dl = camp_data.find_element(By.CSS_SELECTOR, 'dl')
                            dt = dl.find_elements(By.TAG_NAME, 'dt')
                            dd = dl.find_elements(By.TAG_NAME, 'dd')

                            temp_camp_info[dt[0].text] = dd[0].text.replace('\n', ',')

                        camp_info_list['reserve'] = temp_camp_info

                    if a.get_attribute('class').find('time_info') != -1:
                        temp_camp_info = {}
                        for camp_data in driver.find_elements(By.CSS_SELECTOR, '#wrap > div.wrap_in > section.use_info_sec > div > div.time_info > div.time_div'):
                            temp_dict = {}
                            for time in camp_data.find_elements(By.CSS_SELECTOR, 'ul > li > dl'):
                                temp_dict[time.find_element(By.TAG_NAME, 'dt').text] = time.find_element(By.TAG_NAME, 'dd').text
                            temp_camp_info[camp_data.find_element(By.CLASS_NAME, 'tit').text.split('\n')[0]] = temp_dict

                        camp_info_list['time'] = temp_camp_info
                        camp_info_list['id'] = url.split('cseq=')[1]

                # print(camp_info_list)
                json_data[url.split('cseq=')[1]] = camp_info_list
                print(json.dumps(json_data, indent='\t', ensure_ascii=False))
        except:
            pass

        finally:
            with open('camp_site_info.json', 'w', encoding='utf-8') as make_file:
                json.dump(json_data, make_file, ensure_ascii=False, indent='\t')




def camp_site_info_old(self, urls):
    driver = webdriver.Chrome('chromedriver.exe')
    driver.implicitly_wait(3)
    # camp_info_list = []
    json_data = OrderedDict()
    try:
        for url in urls:
            driver.get(url)
            driver.execute_script("window.scrollTo(0,700)")
            print(url.split('cseq=')[1])
            # print('총 정보의 갯수 : ' + str(len(driver.find_elements(By.CSS_SELECTOR, '#divResInfo > div.if_sc'))))
            temp_camp_info = {}
            camp_info_list = {}
            indexing = ['camp_type', 'amenity', 'available', 'leisure']
            # 특수정보 있으면 넣는 부분
            if driver.find_element(By.CSS_SELECTOR, '#container > div > div.section.top > div.if_emblem').find_elements(
                    By.TAG_NAME, 'span') != '':
                for special in driver.find_elements(By.CSS_SELECTOR,
                                                    '#container > div > div.section.top > div.if_emblem > span'):
                    temp_camp_info[special.get_attribute('class')] = driver.find_element(By.CSS_SELECTOR,
                                                                                         '#container > div > div.section.top > div.if_emblem > span.' + special.get_attribute(
                                                                                             'class')).text

            # 요약 정보 넣는 부분
            temp_camp_info['img'] = driver.find_element(By.CSS_SELECTOR,
                                                        '#wrap > div.wrap_in > div.container > section > div.swiper-container.ci_top_swiper.swiper-container-initialized.swiper-container-horizontal > ul > li.swiper-slide.swiper-slide-active > a > img').get_attribute(
                'src')
            temp_camp_info['site_name'] = driver.find_element(By.CSS_SELECTOR,
                                                              '#wrap > div.wrap_in > div.container > section > div.txt_box > p').text
            for summary in driver.find_elements(By.CSS_SELECTOR,
                                                '#container > div > div.section.top > div.info.pT0 >p'):
                temp_camp_info[summary.get_attribute('class')] = driver.find_element(By.CSS_SELECTOR,
                                                                                     '#container > div > div.section.top > div.info.pT0 > p.' + summary.get_attribute(
                                                                                         'class')).text
            # print(driver.find_element(By.CSS_SELECTOR, '#container > div > div.section.top').text.split('\n'))
            camp_info_list['summary'] = temp_camp_info

            first_table_meet = True
            for idx, camp_data in enumerate(driver.find_elements(By.CSS_SELECTOR, '#divResInfo > div')):
                temp_camp_info = {}
                data = OrderedDict()
                if camp_data.get_attribute('class').find('info_Hd if_sc') != -1:
                    # 소개글이 있을때 처리
                    camp_info_list['intro'] = camp_data.find_element(By.CSS_SELECTOR, 'div > p').text.replace('\n', ' ')
                elif camp_data.get_attribute('class').find('if_sc bdB0') != -1:
                    if first_table_meet:
                        reindex = idx
                        first_table_meet = False
                    for table in camp_data.find_elements(By.CSS_SELECTOR, 'table > tbody > tr'):
                        # print(table.text)
                        for index, td in enumerate(table.find_elements(By.TAG_NAME, 'td')):
                            if index % 2 == 0:
                                key = td.text
                            if index % 2 == 1:
                                try:
                                    if td.find_element(By.TAG_NAME, 'span').get_attribute('class').find(
                                            'itemChk') != -1:
                                        value = '가능'
                                    else:
                                        value = '불가능'
                                    temp_camp_info[key] = value
                                except NoSuchElementException:
                                    # print('익셉션 발생')
                                    continue
                    camp_info_list[indexing[idx - reindex]] = temp_camp_info
                else:
                    if camp_data.find_element(By.CSS_SELECTOR, 'h4').text == '기타정보':
                        camp_info_list['etc'] = camp_data.find_element(By.CSS_SELECTOR, 'div').text.replace('-',
                                                                                                            '').replace(
                            '\n', '')
                    else:
                        # 일반 dl 정보들
                        dl = camp_data.find_element(By.CSS_SELECTOR, 'dl')
                        dt = dl.find_elements(By.TAG_NAME, 'dt')
                        dd = dl.find_elements(By.TAG_NAME, 'dd')
                        for idx in range(len(dt)):
                            if dt[idx].text.find('연락처') != -1 or dd[idx].text == '':
                                continue
                            temp_camp_info[dt[idx].text.replace('-', '').replace('\n', '').replace(':', '')] = dd[
                                idx].text.replace('-', '').replace('\n', '')
                        if camp_data.find_element(By.CSS_SELECTOR, 'h4').text == '기본정보':
                            camp_info_list['base'] = temp_camp_info
                            # camp_info_list.append(data)
                        elif camp_data.find_element(By.CSS_SELECTOR, 'h4').text == '요금정보':
                            camp_info_list['fee'] = temp_camp_info
                            # camp_info_list.append(data)
                        elif camp_data.find_element(By.CSS_SELECTOR, 'h4').text == '예약정보':
                            camp_info_list['reserve'] = temp_camp_info
                        # camp_info_list.append(data)

            json_data[url.split('cseq=')[1]] = camp_info_list
    except:
        pass

    # finally:
    #     with open('camp_site_info.json', 'w', encoding='utf-8') as make_file:
    #         json.dump(json_data, make_file, ensure_ascii=False, indent='\t')
