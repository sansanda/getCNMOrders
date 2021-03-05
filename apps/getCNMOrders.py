
import os
import time
import sys

from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager

from tools.CNMWebOrdersScrapper import CNMWebOrdersScrapper


def main():

    argumentsList = sys.argv[1:]

    print(argumentsList)

    login_url = argumentsList[0]
    orders_url = argumentsList[1]
    user = argumentsList[2]
    password = argumentsList[3]
    first_count_year = int(argumentsList[4])
    from_year = int(argumentsList[5])
    to_year = int(argumentsList[6])
    savingFilePath = argumentsList[7]

    driver = webdriver.Chrome(ChromeDriverManager().install())

    cnmWebOrdersScrapper = CNMWebOrdersScrapper(driver, login_url, orders_url, user, password, first_count_year, from_year, to_year, savingFilePath)
    cnmWebOrdersScrapper.doLogin()
    cnmWebOrdersScrapper.goToPage(orders_url)
    cnmWebOrdersScrapper.goToYear(2017)
    print(cnmWebOrdersScrapper.getActualYearOrdersCodes())



if __name__ == "__main__":
    main()
