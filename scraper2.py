import csv
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager


class BookScraper:
    def __init__(self):
        options = Options()
        options.headless = True
        self.driver = webdriver.Chrome(options=options)
        self.wait = WebDriverWait(self.driver, 10)

    def scrape_books(self):
        self.driver.get("https://www.bookdepot.com/Store/Browse?Nc=31&Ns=1393&size=96&sort=relevance_1")
        book_data = []
        self.wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.grid-item')))
        while True:
            # 找到当前页上的所有书（96个）。在每次循环开始时重新获取书籍元素列表以避免陈旧的元素引用。
            books = self.driver.find_elements(By.CSS_SELECTOR, 'div.grid-item')  # hopefully, len(books) == 96
            for book in books:
                book_details_link = book.find_element(By.CSS_SELECTOR, 'h2 a').get_attribute('href')
                print(book_details_link)
                book_data.append(self.scrape_book_details(book_details_link))
            print('length of pages traversed: ', len(book_data))
            next_button = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'li a[aria-label="Next"]')))
            if 'disabled' in next_button.get_attribute('class'):
                break
            else:
                next_button.click()
        return book_data

    # def scrape_books(self):
    #     self.driver.get("https://www.bookdepot.com/Store/Browse?Nc=31&Ns=1393&size=96&sort=relevance_1")
    #     book_data = []
    #
    #     while True:
    #         # 等待至少一个grid-item元素出现
    #         self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.grid-item')))
    #         # 然后尝试获取所有grid-item元素
    #         books = self.driver.find_elements(By.CSS_SELECTOR, 'div.grid-item')
    #         for book in books:
    #             book_details_link = book.find_element(By.CSS_SELECTOR, 'h2 a').get_attribute('href')
    #             book_data.append(self.scrape_book_details(book_details_link))
    #
    #         next_button = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'li a[aria-label="Next"]')))
    #         if 'disabled' in next_button.get_attribute('class'):
    #             break
    #         else:
    #             next_button.click()
    #
    #     return book_data

    def scrape_book_details(self, url) -> dict:
        self.driver.get(url)
        self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div#book-cover img')))
        print('you are here...')
        time.sleep(2)

        book_info = {
            'cover': self.driver.find_element(By.CSS_SELECTOR, 'div#book-cover img').get_attribute('src'),
            'title': self.driver.find_element(By.CSS_SELECTOR, 'h4[itemprop="name"]').text,
            'author': self.driver.find_element(By.CSS_SELECTOR, 'span[itemprop="author"]').text,
            'binding': self.driver.find_element(By.CSS_SELECTOR, 'span[itemprop="bookFormat"]').text,

            # list price
            'list_price': self.driver.find_element(By.CSS_SELECTOR,
                            'table.tbl-biblio:nth-of-type(1) tr:nth-of-type(3) td:nth-of-type(2)').text,

            'price': self.driver.find_element(By.CSS_SELECTOR, 'span[itemprop="price"] span:nth-of-type(2)').text,

            # stock quantity
            'stock': self.driver.find_element(By.CSS_SELECTOR,
                            'table.tbl-biblio:nth-of-type(1) tr:nth-of-type(5) td:nth-of-type(2)').text,

            'isbn': self.driver.find_element(By.CSS_SELECTOR, 'span[itemprop="isbn"]').text,
            'publisher': self.driver.find_element(By.CSS_SELECTOR, 'span[itemprop="publisher"]').text,

            # publication date
            'publication_date': self.driver.find_element(By.CSS_SELECTOR,
                            'table.tbl-biblio tr:nth-of-type(7) td:nth-of-type(2)').text,

            # book size
            'size': self.driver.find_element(By.CSS_SELECTOR,
                            'table.tbl-biblio tr:nth-child(6) td:nth-child(2)').text,
            'categories': [e.text for e in self.driver.find_elements(By.CSS_SELECTOR, 'span[itemprop="genre"]')]
        }

        return book_info

    def save_data(self, data):
        with open('output.csv', 'w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)

    def close(self):
        self.driver.quit()


def main():
    scraper = BookScraper()
    try:
        book_data = scraper.scrape_books()
        scraper.save_data(book_data)
    finally:
        scraper.close()


if __name__ == "__main__":
    main()
