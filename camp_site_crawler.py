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
                result.append('https://m.thankqcamping.com/resv/view.hbb?cseq=' + aa.find_element(By.CSS_SELECTOR, 'a').get_attribute('href').split(',')[1])
            else:
                # print(aa.find_element(By.CSS_SELECTOR, 'a').get_attribute('href').split(',')[0].split('(')[1])
                result.append('https://m.thankqcamping.com/resv/view.hbb?cseq=' + aa.find_element(By.CSS_SELECTOR, 'a').get_attribute('href').split(',')[0].split('(')[1])

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
        for url in urls:
            driver.get(url)
            driver.find_element(By.CSS_SELECTOR, '#container > div > div.section.reser_info').click()
            time.sleep(1)
            print(url.split('cseq=')[1])
            print('총 정보의 갯수 : ' + str(len(driver.find_elements(By.CSS_SELECTOR, '#divResInfo > div.if_sc'))))
            temp_camp_info = {}
            camp_info_list = []
            indexing = ['camp_type', 'amenity', 'available', 'leisure']
            # 요약 정보 넣는 부분
            temp_camp_info['img'] = driver.find_element(By.CSS_SELECTOR, '#container > div > div.section.top > div.pic > div > ul > li > img').get_attribute('src')
            temp_camp_info['site_name'] = driver.find_element(By.CSS_SELECTOR, '#container > div > div.section.top > div.info.pT0 > h2').text
            temp_camp_info['addr'] = driver.find_element(By.CSS_SELECTOR, '#container > div > div.section.top > div.info.pT0 > p.address').text if driver.find_element(By.CSS_SELECTOR, '#container > div > div.section.top > div.info.pT0> p.address').get_attribute('class').find('address') != -1 else ''
            temp_camp_info['tel'] = driver.find_element(By.CSS_SELECTOR, '#container > div > div.section.top > div.info.pT0 > p.tel').text if driver.find_element(By.CSS_SELECTOR, '#container > div > div.section.top > div.info.pT0> p.tel').get_attribute('class').find('tel') != -1 else ''
            temp_camp_info['tema'] = driver.find_element(By.CSS_SELECTOR, '#container > div > div.section.top > div.info.pT0 > p.tema').text if driver.find_element(By.CSS_SELECTOR, '#container > div > div.section.top > div.info.pT0> p.tema').get_attribute('class').find('tema') != -1 else ''
            temp_camp_info['like'] = driver.find_element(By.CSS_SELECTOR, '#cntFav').text if driver.find_element(By.CSS_SELECTOR, '#cntFav').text != '' else ''
            temp_camp_info['update_dt'] = driver.find_element(By.CSS_SELECTOR, '#container > div > div.section.top > div.info.pT0 > p.look').text if driver.find_element(By.CSS_SELECTOR, '#container > div > div.section.top > div.info.pT0> p.look').get_attribute('class').find('look') != -1 else ''
            summary_data = OrderedDict()
            summary_data['summary'] = temp_camp_info
            # print(driver.find_element(By.CSS_SELECTOR, '#container > div > div.section.top').text.split('\n'))
            # camp_info_list.append(summary_data)
            camp_info_list.append({'summary' : temp_camp_info})

            first_table_meet = True
            for idx, camp_data in enumerate(driver.find_elements(By.CSS_SELECTOR, '#divResInfo > div')):
                temp_camp_info = {}
                if camp_data.get_attribute('class').find('info_Hd if_sc') != -1:
                    # 소개글이 있을때 처리
                    intro = OrderedDict()
                    intro['intro'] = camp_data.find_element(By.CSS_SELECTOR, 'div > p').text.replace('\n', ' ')
                    # camp_info_list.append(intro)
                    camp_info_list.append({'intro':temp_camp_info})
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
                                    if td.find_element(By.TAG_NAME, 'span').get_attribute('class').find('itemChk') != -1:
                                        value = '가능'
                                    else:
                                        value = '불가능'
                                    temp_camp_info[key] = value
                                except NoSuchElementException:
                                    print('익셉션 발생')
                                    continue
                    # data[indexing[idx - reindex]] = temp_camp_info
                    # camp_info_list.append(data)
                    camp_info_list.append({indexing[idx - reindex]:temp_camp_info})
                else:
                    if camp_data.find_element(By.CSS_SELECTOR, 'h4').text == '기타정보':
                        camp_info_list.append({'etc': camp_data.find_element(By.CSS_SELECTOR, 'div').text.replace('-', '').replace('\n', '')})
                    else:
                        # 일반 dl 정보들
                        dl = camp_data.find_element(By.CSS_SELECTOR, 'dl')
                        dt = dl.find_elements(By.TAG_NAME, 'dt')
                        dd = dl.find_elements(By.TAG_NAME, 'dd')
                        for idx in range(len(dt)):
                            if dt[idx].text.find('연락처') != -1 or dd[idx].text == '':
                                continue
                            temp_camp_info[dt[idx].text.replace('-', '').replace('\n', '').replace(':', '')] = dd[idx].text.replace('-', '').replace('\n', '')
                        if camp_data.find_element(By.CSS_SELECTOR, 'h4').text == '기본정보':
                            camp_info_list.append({'base' : temp_camp_info})
                            # camp_info_list.append(data)
                        elif camp_data.find_element(By.CSS_SELECTOR, 'h4').text == '요금정보':
                            camp_info_list.append({'fee' : temp_camp_info})
                            # camp_info_list.append(data)
                        elif camp_data.find_element(By.CSS_SELECTOR, 'h4').text == '예약정보':
                            camp_info_list.append({'reserve' : temp_camp_info})
                        # camp_info_list.append(data)
                    # camp_info_list.append(data)
                    # camp_info_list.append(temp_camp_info)

            json_data[url.split('cseq=')[1]] = camp_info_list
            print(json.dumps(json_data, ensure_ascii=False, indent='\t'))
