import os
import requests
from concurrent.futures import ThreadPoolExecutor
from redis import Redis

# Configure Redis connection
REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = os.getenv('REDIS_PORT', 6379)
redis = Redis(host=REDIS_HOST, port=REDIS_PORT)

# Define a function to scrape a URL and cache the result
def scrape_url(url):
    # Check if the URL is cached in Redis
    cached_result = redis.get(url)
    if cached_result:
        return cached_result.decode('utf-8')
    
    # Scrape the URL
    response = requests.get(url)
    html = response.text
    
    # Cache the result in Redis
    redis.set(url, html)
    
    return html

# Define a function to scrape multiple URLs in parallel
def scrape_urls(urls):
    with ThreadPoolExecutor() as executor:
        results = list(executor.map(scrape_url, urls))
    return results

# Example usage
urls = ['https://www.example.com', 'https://www.google.com', 'https://www.github.com']
scraped_data = scrape_urls(urls)
print(scraped_data)