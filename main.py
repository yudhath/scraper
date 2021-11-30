from pprint import pprint
from array import *
from product import Product
from productWrapper import ProductWrapper

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from collections import defaultdict

import time
import csv


class Scrapper:
    def __init__(self):
        self.driver = webdriver.Chrome('path-to-web-driver')
        self.wait = WebDriverWait(self.driver, 10)

    def open_new_tab(self, url, tabNumber):
        self.driver.execute_script('window.open("' + url + '", "_blank");')
        self.driver.switch_to.window(self.driver.window_handles[tabNumber])
        
        return

    def process_data(self, max_products_count):
        productNameList = self.driver.find_elements_by_xpath("//div[@data-testid='lstCL2ProductList']/child::div/child::a/div[@data-testid='divProductWrapper']/div[@class='css-11s9vse']/span[@class='css-1bjwylw']")
        priceList = self.driver.find_elements_by_xpath("//div[@data-testid='lstCL2ProductList']/child::div/child::a/div[@data-testid='divProductWrapper']/div[@class='css-11s9vse']/div/div[@class='css-4u82jy']/span[@class='css-o5uqvq']")
        storeNameList = self.driver.find_elements_by_xpath("//div[@data-testid='lstCL2ProductList']/child::div/child::a/div[@data-testid='divProductWrapper']/div[@class='css-11s9vse']/div[@class='css-tpww51']/div[@class='css-vbihp9']/child::span[2]")
        imageList = self.driver.find_elements_by_xpath("//div[@data-testid='lstCL2ProductList']/child::div/child::a/div[@data-testid='divProductWrapper']/div[@class='css-79elbk']/div[@class='css-1c0vu8l']/div[@class='css-t8frx0']/img")
        starRatingList = self.driver.find_elements_by_xpath("//div[@data-testid='lstCL2ProductList']/child::div/child::a/div[@data-testid='divProductWrapper']/div[@class='css-11s9vse']/div[@class='css-153qjw7']")
        rating = []
        for starRating in starRatingList:
            starCount = starRating.find_elements_by_css_selector(".css-177n1u3")
            rating.append(len(starCount))

        i=0
        result = []
        while i < len(productNameList):
            if max_products_count == 0:
                break
            product = Product(
                productNameList[i].text,
                "no desc",
                imageList[i].get_attribute("src"),
                priceList[i].text,
                str(rating[i]) if i < len(rating) else "" ,
                storeNameList[i].text
            )
            result.append(product)
            i+=1
            max_products_count-=1

        return ProductWrapper(result, max_products_count)

    def scroll_handler(self):
        scrollCount = 1
        startScrollHeight = 0
        nextScrollHeight = 1000
        scrollHeight = 1000
        while scrollCount < 10:
            scriptString = "window.scrollTo(" + str(startScrollHeight) + ", " + str(nextScrollHeight) + " );"
            time.sleep(1)
            self.driver.execute_script(scriptString)
            startScrollHeight=nextScrollHeight
            nextScrollHeight=scrollHeight*scrollCount
            scrollCount += 1
        
        self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "div.css-1q668u-unf-pagination-items")))

    def save_to_csv(self, productList):
        with open('scrapper_result.csv', 'w') as new_file:
            fieldnames = ['name', 'desc', 'image url', 'price', 'rating', 'store name']

            csv_writer = csv.DictWriter(new_file, fieldnames=fieldnames)

            csv_writer.writeheader()

            for product in productList:
                result = {
                    'name': product.name,
                    'desc': product.desc,
                    'image url': product.image_url,
                    'price': product.price,
                    'rating': product.rating,
                    'store name': product.store_name
                }
                csv_writer.writerow(result)

    def scrape(self, max_products_count=100):
        self.driver.get('https://www.tokopedia.com/p/handphone-tablet/handphone?page=1')
        self.scroll_handler()

        result = []
        productWrapper = self.process_data(max_products_count)
        result += productWrapper.result
        max_products_count = productWrapper.max_products_count

        self.open_new_tab('https://www.tokopedia.com/p/handphone-tablet/handphone?page=2',1)
        self.scroll_handler()
        productWrapper = self.process_data(max_products_count)
        result += productWrapper.result
        max_products_count = productWrapper.max_products_count
        
        self.driver.quit()
        return result

if __name__ == '__main__':
    scraper = Scrapper()

    scraping_result = scraper.scrape(100)
    scraper.save_to_csv(scraping_result)