from scrapers.crawlers import get_crawler
from scrapers.workers import WorkQueue, Extractor, Collector
from scrapers.utility.data import get_field_names
from scrapers.utility.data import filter_processed, split_data

import os
import csv

website = "imdb"
NUM_CRAWLERS = 4
FIELD_NAMES = get_field_names(website)


# Write callback
def save_to_file(entry: dict):
    with open(
        f"./database/{website}/movie_entries.csv", "a", encoding="utf-8"
    ) as writefile:
        writer = csv.DictWriter(writefile, fieldnames=FIELD_NAMES)
        writer.writerow(entry)


def main():
    print(f"Crawling with {NUM_CRAWLERS} crawlers.")
    if not os.path.isfile(f"./database/{website}/movie_entries.csv"):
        with open("./database/movie_entries.csv", "w") as writefile:
            writer = csv.DictWriter(writefile, fieldnames=FIELD_NAMES)
            writer.writeheader()

    to_process = filter_processed(website)
    to_process_count = len(to_process)
    batches = split_data(to_process, NUM_CRAWLERS)

    work_queue = WorkQueue()

    for i in range(NUM_CRAWLERS):
        crawler = get_crawler(website)
        worker = Extractor(work_queue, crawler)
        worker.process(batches[i])

    collector = Collector(
        work_queue,
        worker_count=NUM_CRAWLERS,
        item_count=to_process_count,
        callback=save_to_file,
    )
    collector.process()
    print("Finished!")


if __name__ == "__main__":
    main()
