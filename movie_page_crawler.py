from scrapers.crawlers import get_crawler
from scrapers.workers import WorkQueue, Extractor, Collector
from scrapers.utility.data import get_field_names
from scrapers.utility.data import filter_processed, split_data

import os
import sys
import csv
import pickle
import time
import math

website = "tmdb"
NUM_CRAWLERS = 5
BATCH_SIZE = 200
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
        for _, path in enumerate(os.listdir(TEMP)):
            path = os.path.join(TEMP, path)
            with open(path, "rb") as file:
                entry = pickle.load(file)
            writer.writerow(entry)
            os.remove(path)


def main():
    if not os.path.isdir(TEMP):
        os.makedirs(TEMP)
    if not os.path.isfile(TARGET):
        with open(TARGET, "w") as writefile:
            writer = csv.DictWriter(writefile, fieldnames=FIELD_NAMES)
            writer.writeheader()

    to_process = filter_processed(website).iloc[:200]
    batch_count = math.ceil(len(to_process) / BATCH_SIZE)

    work_queue = WorkQueue()
    print(f"Crawling with {NUM_CRAWLERS} crawlers, to process: {len(to_process)}.")
    for batch_idx in range(batch_count):
        print(f"Batch: {batch_idx + 1}/{batch_count}")
        curent_idx = batch_idx * BATCH_SIZE
        to_process = filter_processed(website).iloc[
            curent_idx : curent_idx + BATCH_SIZE
        ]
        to_process_count = len(to_process)
        batches = split_data(to_process, NUM_CRAWLERS)

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

        while collect_thread.is_alive():
            time.sleep(60)
            dump_to_database()
        else:
            dump_to_database()
    print("\nFinished!")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nTerminating...")
        print("Dumping to Database")
        dump_to_database()
        sys.exit()
