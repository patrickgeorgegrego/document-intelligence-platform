import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager

# We will import the model lazily if needed, but since it'll be run from django context, this is fine.
from .models import Book

class BookScraper:
    def __init__(self):
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        self.driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
        self.base_url = "http://books.toscrape.com/"

    def scrape_books(self, num_books=10):
        print("Starting scraper...")
        self.driver.get(self.base_url)
        time.sleep(2)
        
        books_data = []
        
        try:
            # Get book links from the front page
            book_elements = self.driver.find_elements(By.CSS_SELECTOR, 'article.product_pod h3 a')
            book_links = [elem.get_attribute('href') for elem in book_elements][:num_books]
            
            for link in book_links:
                self.driver.get(link)
                time.sleep(1)
                
                try:
                    title = self.driver.find_element(By.CSS_SELECTOR, '.product_main h1').text
                    # Author is not explicitly on books.toscrape, so we assign a placeholder
                    author = "Unknown Author" 
                    
                    # Rating extraction
                    rating_element = self.driver.find_element(By.CSS_SELECTOR, 'p.star-rating')
                    rating_class = rating_element.get_attribute('class').replace('star-rating', '').strip()
                    rating_map = {'One': 1, 'Two': 2, 'Three': 3, 'Four': 4, 'Five': 5}
                    rating = rating_map.get(rating_class, 0.0)
                    
                    # Description extraction
                    try:
                        description = self.driver.find_element(By.XPATH, '//div[@id="product_description"]/following-sibling::p').text
                    except:
                        description = "No description available."
                        
                    # Genre extraction
                    try:
                        breadcrumb = self.driver.find_elements(By.CSS_SELECTOR, '.breadcrumb li a')
                        # index 2 corresponds to the genre, index 0 is Home, index 1 is Books
                        genre = breadcrumb[2].text if len(breadcrumb) >= 3 else "General"
                    except:
                        genre = "General"
                    
                    data = {
                        'title': title,
                        'author': author,
                        'description': description,
                        'rating': float(rating),
                        'url': link,
                        'genre': genre
                    }
                    books_data.append(data)
                    print(f"Successfully scraped: {title}")
                except Exception as e:
                    print(f"Error scraping individual book {link}: {e}")
                    
        except Exception as e:
            print(f"Error extracting front page links: {e}")
            
        finally:
            self.driver.quit()
            
        return books_data
        
    def save_books_to_db(self, books_data):
        """Saves the scraped data to the MySQL DB."""
        saved_count = 0
        for data in books_data:
            book, created = Book.objects.get_or_create(url=data['url'], defaults=data)
            if created:
                saved_count += 1
                print(f"Saved to DB: {book.title}")
            else:
                print(f"Already exists in DB: {book.title}")
        return saved_count
