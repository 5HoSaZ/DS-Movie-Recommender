from ..utility.wrapper import threaded
from ..crawlers import PageCrawler
from ..utility.data import MovieLinkGenerator

from threading import Thread
from typing import Callable
from queue import Queue as WorkQueue
import time


class Extractor:

    def __init__(self, work_queue: WorkQueue, crawler: PageCrawler):
        self.crawler = crawler
        self.queue = work_queue

    def finish(self):
        self.crawler.terminate()
        self.queue.put_nowait(None)

    @threaded
    def process(self, items: MovieLinkGenerator) -> Thread:
        for item in items:
            success = False
            attempt = 0
            while not success:
                try:
                    entry = self.crawler.get_entry(item.Link, item.Name)
                    success = True
                except Exception:
                    attempt += 1
                    time.sleep(attempt)
                    if attempt > 10:
                        self.crawler.restart()
                        attempt = 0
            self.queue.put_nowait(entry)
        self.finish()


class Collector:

    def __init__(
        self,
        work_queue: WorkQueue,
        worker_count: int,
        item_count: int,
        callback: Callable,
    ):
        self.queue = work_queue
        self.unfinished = worker_count
        self.item_count = item_count
        self.callback = callback

    @threaded
    def process(self) -> Thread:
        count = 0
        while self.unfinished:
            entry = self.queue.get()
            if entry is None:
                self.unfinished -= 1
            else:
                self.callback(count, entry)
                count += 1
                print(
                    f"Processed {count}/{self.item_count} - {(count / self.item_count):.2%}",
                    end="\r",
                )
        print()
