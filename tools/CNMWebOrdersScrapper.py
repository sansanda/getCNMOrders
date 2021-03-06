from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager

import time
import datetime

class CNMWebOrdersScrapper():

    def __init__(self, driver, login_url, orders_url, user, password, first_count_year, startYear, lastYear, cnmOrdersFilePath):
        self.driver = driver
        self.login_url = login_url
        self.orders_url = orders_url
        self.user = user
        self.password = password
        self.firstCountYear = first_count_year
        self.startYear = startYear
        self.lastYear = lastYear
        self.cnmOrdersFilePath = cnmOrdersFilePath
        self.actualYear = datetime.datetime.now().year

    def doLogin(self):
        self.driver.get(self.login_url)

        login_user = self.driver.find_element_by_id('login_user')
        login_password = self.driver.find_element_by_id('login_password')
        login_btn = self.driver.find_element_by_id('login_btn')
        login_user.send_keys(self.user)
        login_password.send_keys(self.password)
        login_btn.click()

        # volvemos a pedir la pagina, esta vez ya logeados
        self.driver.get(self.login_url)
        # print(self.driver.page_source)

    def goToPage(self, url):
        self.driver.get(url)

    def goToYear(self, step):

        if step >= self.actualYear:
            return

        for step in range(self.actualYear, step, -1):
            time.sleep(1)
            self.driver.execute_script('purchase.prevRequests();')

    def goAheadNYears(self, nYears):
        for step in range(0, nYears):
            time.sleep(2)
            self.driver.execute_script('purchase.nextRequests();')

    def getActualYearOrdersCodes(self):
        ordersCodes = list()
        baseTable = self.driver.find_element_by_id("theList")
        tableRows = baseTable.find_elements_by_tag_name("tr")
        for row in tableRows[1:]: #skip header
            print(row.text)
            cols = row.find_elements_by_tag_name("td")
            #ordersCodes.append(int(cols[0].text))
        return ordersCodes

    def test(self):
        self.driver.execute_script('purchase.listRequests(2020,1,Tot);')

