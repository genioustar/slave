import asyncio
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup

class CampSiteCrawler:

    async def camp_site_info(self, param, result):
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
            tmpList.append(self.camp_site_info(url, result))
            # break

        await asyncio.wait(tmpList)
        print(len(result))
        print(result)
        return result
