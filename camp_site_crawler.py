import asyncio
import time
from selenium import webdriver
from selenium.webdriver.common.by import By

result = []


class CampSiteCrawler:

    async def camp_site_info(self, param):
        url = param
        driver = webdriver.Chrome('chromedriver.exe')
        driver.implicitly_wait(3)
        driver.get(url)

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
            print(aa.text)

    async def gether_sub_region(self, siteList):
        tmpList = []
        for url in siteList:
            tmpList.append(self.camp_site_info(url))

        await asyncio.wait(tmpList)
