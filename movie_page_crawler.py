from scrapers.crawlers import get_crawler
from scrapers.workers import WorkQueue, Extractor, Collector
from scrapers.utility.data import get_field_names
from scrapers.utility.data import filter_processed, split_data

import os
import csv
import pickle

website = "imdb"
NUM_CRAWLERS = 3
FIELD_NAMES = get_field_names(website)
TEMP = "./tmp"
TARGET = f"./database/{website}/movie_entries.csv"


# Write callback
def save_to_file(count: int, entry: dict):
    with open(os.path.join(TEMP, f"{count}.pkl"), "wb") as file:
        pickle.dump(entry, file)


def dump_to_database():
    with open(TARGET, "a", encoding="utf-8") as writefile:
        writer = csv.DictWriter(writefile, fieldnames=FIELD_NAMES)
        for i, path in enumerate(os.listdir(TEMP)):
            path = os.path.join(TEMP, path)
            with open(path, "rb") as file:
                entry = pickle.load(file)
            print(f"Dumping to {TARGET}: {i + 1} done", end="\r")
            writer.writerow(entry)
            os.remove(path)
    print("\nFinished!")


def main():
    print(f"Crawling with {NUM_CRAWLERS} crawlers.")
    if not os.path.isdir(TEMP):
        os.makedirs(TEMP)
    if not os.path.isfile(TARGET):
        with open(TARGET, "w") as writefile:
            writer = csv.DictWriter(writefile, fieldnames=FIELD_NAMES)
            writer.writeheader()

    to_process = filter_processed(website)
    to_process_count = len(to_process)
    batches = split_data(to_process, NUM_CRAWLERS)

    work_queue = WorkQueue()

    for i in range(NUM_CRAWLERS):
        crawler = get_crawler(website)
        worker = Extractor(work_queue, crawler)
        worker.process(batches[i]).start()

    collector = Collector(
        work_queue,
        worker_count=NUM_CRAWLERS,
        item_count=to_process_count,
        callback=save_to_file,
    )
    collect_thread = collector.process()
    collect_thread.start()
    collect_thread.join()
    dump_to_database()


if __name__ == "__main__":
    main()
