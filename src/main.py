import requests
from bs4 import BeautifulSoup
import hashlib
import time
import random
import json

class DecentralizedScraper:
    def __init__(self):
        self.nodes = []
        self.tasks = []
        self.results = {}

    def add_node(self, node_url):
        self.nodes.append(node_url)

    def add_task(self, url, selector):
        task_id = hashlib.sha256(f'{url}:{selector}'.encode()).hexdigest()
        self.tasks.append({
            'id': task_id,
            'url': url,
            'selector': selector
        })
        return task_id

    def execute_task(self, task_id):
        task = next((t for t in self.tasks if t['id'] == task_id), None)
        if task:
            node_url = random.choice(self.nodes)
            response = requests.post(f'{node_url}/scrape', json={
                'url': task['url'],
                'selector': task['selector']
            })
            if response.status_code == 200:
                self.results[task_id] = response.json()
            else:
                self.results[task_id] = {'error': 'Failed to scrape'}
        else:
            self.results[task_id] = {'error': 'Task not found'}

    def get_result(self, task_id):
        return self.results.get(task_id, None)

if __name__ == '__main__':
    scraper = DecentralizedScraper()
    scraper.add_node('http://node1.example.com')
    scraper.add_node('http://node2.example.com')
    scraper.add_node('http://node3.example.com')

    task_id = scraper.add_task('https://www.example.com', 'h1')
    scraper.execute_task(task_id)
    result = scraper.get_result(task_id)
    print(result)