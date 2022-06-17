from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from time import sleep
import requests
import csv


class BaseParser:

    def __init__(self, url: str):
        self.URL = url
        self.HOST = "https://www.carrefour.ke"
        self.HEADERS = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:91.0) Gecko/20100101 Firefox/91.0"
        }

    def get_product_urls(self):
        browser = webdriver.Chrome(ChromeDriverManager().install())
        browser.get(self.URL)

        products=browser.find_element(by=By.CLASS_NAME, value="css-lzsise")
        product_urls = products.find_elements(by=By.TAG_NAME, value="a")
        i = 0
        a = 0
        urls = []
        for a in range(30):
            for product in product_urls:
                i += 1
                product = product.get_attribute("href")
                if product not in urls:
                    urls.append(product)
            print(f"Scraping the urls")
        return urls

class SectionParser(BaseParser):

    def get_section_products(self, urls):
        print("Getting Products")
        for url in urls:
            response = requests.get(url, headers=self.HEADERS)
            html = response.text
            soup = BeautifulSoup(html, "html.parser")
            sections = soup.find("main", class_="css-xidbcq")
            images = []
            for section in sections:
                title = section.find("h1", class_="css-106scfp")
                try:
                    pack_size = section.find("div", class_="css-1kxxv3q").get_text(strip=True).replace("Pack size : ", "")
                except:
                    pack_size = "Not mentioned"
                price = section.find("h2", class_="css-17ctnp")
                try:
                    left = section.find("div", class_="css-g4iap9").get_text().replace("Only ", "").replace("left!", "")
                except:
                    left = "Empty"
                try:
                    description = section.find("div", class_="css-16lm0vc").get_text()
                except:
                    description = "No Description"
                link_images = section.find_all("img", class_="swiper-lazy")
                for img in link_images:
                    image = img.get("src")
                    images.append(image)
            
            title = title.get_text(strip=True)
            pack_size = pack_size
            price = price.get_text().replace("(Inc. VAT)", "")
            product_field = ["Product Name", "Price", "Pack Size", "Inventory Left", "Description", "All images url"]
            products = [{
                "Product Name": title,
                "Price": price,
                "Pack Size": pack_size,
                "Inventory Left": left,
                "Description": description,
                "All images url": images,
            }]

            with open('result.csv', 'a', encoding="UTF-8") as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames = product_field)
                writer.writeheader()
                writer.writerows(products)
            
        print("Success")
            

url = "https://www.carrefour.ke/mafken/en/c/FKEN1500000?currentPage=16&filter=&nextPageOffset=1&pageSize=60&sortBy=relevance"

get_urls = BaseParser(url).get_product_urls()
get_products = SectionParser(url).get_section_products(get_urls)

