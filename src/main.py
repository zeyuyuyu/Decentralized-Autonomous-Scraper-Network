import requests
import multiprocessing as mp
import time

class DistributedScraper:
    def __init__(self, urls, num_workers):
        self.urls = urls
        self.num_workers = num_workers
        self.results = []

    def scrape_url(self, url):
        response = requests.get(url)
        return response.text

    def worker(self, work_queue, result_queue):
        while True:
            try:
                url = work_queue.get(timeout=1)
            except:
                break
            content = self.scrape_url(url)
            result_queue.put(content)

    def run(self):
        work_queue = mp.Queue()
        result_queue = mp.Queue()

        for url in self.urls:
            work_queue.put(url)

        processes = []
        for _ in range(self.num_workers):
            p = mp.Process(target=self.worker, args=(work_queue, result_queue))
            p.start()
            processes.append(p)

        for _ in range(len(self.urls)):
            self.results.append(result_queue.get())

        for p in processes:
            p.terminate()

        return self.results

if __name__ == '__main__':
    urls = ['https://example.com', 'https://another-example.com', 'https://third-example.com']
    scraper = DistributedScraper(urls, num_workers=4)
    results = scraper.run()
    print(results)