import csv
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException


class BookScraper:
    def __init__(self):
        options = Options()
        options.headless = True
        self.driver = webdriver.Chrome(options=options)
        self.wait = WebDriverWait(self.driver, 20)
        self.initialize_csv()

    def initialize_csv(self):
        # Initialize the CSV file and write headers
        with open('output.csv', 'w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=[
                'cover', 'title', 'author', 'binding', 'list_price', 'price',
                'stock', 'isbn', 'publisher', 'publication_date', 'size', 'categories'
            ])
            writer.writeheader()

    def scrape_books(self):
        self.driver.get("https://www.bookdepot.com/Store/Browse?Nc=31&Ns=1393&size=96&sort=relevance_1")
        while True:
            self.wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.grid-item')))
            books = [book.get_attribute('href') for book in
                     self.driver.find_elements(By.CSS_SELECTOR, 'div.grid-item h2 a')]
            for book_link in books:
                self.scrape_book_details_and_save(book_link)

            # 尝试找到并点击下一页按钮
            try:
                next_button = self.wait.until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, 'li a[aria-label="Next"]:not(.disabled)')))
                if next_button:
                    next_button.click()
                    time.sleep(3)  # 等待页面完全加载
                else:
                    print("Reached the last page.")
                    break
            except TimeoutException:
                print("Timeout waiting for the next page button.")
                break
            except Exception as e:
                print(f"An error occurred while trying to navigate to the next page: {e}")
                break

    def scrape_book_details_and_save(self, url):
        self.driver.get(url)
        self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div#book-cover img')))
        time.sleep(2)  # Additional time to ensure stability of page load

        # 处理打折的价格：
        try:  # 尝试获取折扣价
            price = self.driver.find_element(By.CSS_SELECTOR,
                    'span[itemprop="price"] span:nth-of-type(2)').text.replace('$', '')
        except:  # 如果没有折扣价，则获取bookdepot.com的原价
            price = self.driver.find_element(By.CSS_SELECTOR,
                    'span[itemprop="price"]').text.replace('$', '')
        try:
            book_info = {
                'cover': self.driver.find_element(By.CSS_SELECTOR, 'div#book-cover img').get_attribute('src'),
                'title': self.driver.find_element(By.CSS_SELECTOR, 'h4[itemprop="name"]').text,
                'author': self.driver.find_element(By.CSS_SELECTOR, 'span[itemprop="author"]').text,
                'binding': self.driver.find_element(By.CSS_SELECTOR, 'span[itemprop="bookFormat"]').text,
                'list_price': self.driver.find_element(By.CSS_SELECTOR,
                                'table.tbl-biblio tr:nth-of-type(3) td:nth-of-type(2)').text,
                'price': price,     # 从前面获取 折后价格
                'stock': self.driver.find_element(By.CSS_SELECTOR,
                                'table.tbl-biblio tr:nth-of-type(5) td:nth-of-type(2)').text,
                'isbn': self.driver.find_element(By.CSS_SELECTOR, 'span[itemprop="isbn"]').text,
                'publisher': self.driver.find_element(By.CSS_SELECTOR, 'span[itemprop="publisher"]').text,
                'publication_date': self.driver.find_element(By.CSS_SELECTOR,
                                'table.tbl-biblio tr:nth-of-type(7) td:nth-of-type(2)').text,
                'size': self.driver.find_element(By.CSS_SELECTOR,
                                'table.tbl-biblio tr:nth-child(6) td:nth-child(2)').text,
                'categories': [e.text for e in self.driver.find_elements(By.CSS_SELECTOR,
                                'span[itemprop="genre"]')]
            }
            self.save_data(book_info)
        except NoSuchElementException as e:
            print(f"Error fetching details for {url}: {e}")

    def save_data(self, data):
        # Save each book's data immediately to CSV
        with open('output.csv', 'a', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=data.keys())
            writer.writerow(data)

    def close(self):
        self.driver.quit()

def main():
    scraper = BookScraper()
    try:
        scraper.scrape_books()
    finally:
        scraper.close()

if __name__ == "__main__":
    main()
