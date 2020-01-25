#! py -3

"""Demonstrates an asynchronous queue to communicate between asynchronouse producers and consumers."""

import argparse
import asyncio
import itertools
import os
import random
import time


async def make_work_item(size: int = 5) -> str:
    """Make a random item of the specified size."""

    return os.urandom(size).hex()


async def simulate_work(a: int = 1, b: int = 5, caller=None) -> None:
    # The random "length" of the work
    to_sleep_sec = random.randint(0, 10)

    if caller:
        print(f'{caller} working for {to_sleep_sec} seconds.')

    await asyncio.sleep(to_sleep_sec)


async def produce(name: int, q: asyncio.Queue) -> None:
    """Takes random time to produce work items and places them on a queue for consumption."""

    # Number of items to produce before done
    n = random.randint(0, 10)
    print(f'Producer {name} created to produce {n} work items.')

    # Synchronous loop for **each** producer.
    # Note: because the value `n` may be 0 (zero), any producer could produce **no** work.
    for _ in itertools.repeat(None, n):
        await simulate_work(caller=f'Producer {name}')
        work_item = await make_work_item()
        insert_time = time.perf_counter()
        await q.put((work_item, insert_time))
        print(f'Producer {name} added <{work_item}> to queue.')


async def consume(name: int, q: asyncio.Queue) -> None:
    """Consumes work items form a queue and take random time to process them."""
    while True:
        await simulate_work(caller=f'Consumer {name}')
        work_item, insert_time = await q.get()
        extract_time = time.perf_counter()
        print(f'Consumer {name} got work item <{work_item}> in {(extract_time - insert_time):0.5f} seconds.')

        # Informs queue that this work item is finished.
        q.task_done()


async def main(producer_count: int, consumer_count: int):
    q = asyncio.Queue()

    # Create sequence of producer tasks
    producers = [asyncio.create_task(produce(n, q)) for n in range(producer_count)]

    # Creates sequence of consumer tasks
    consumers = [asyncio.create_task(consume(n, q)) for n in range(consumer_count)]

    # Awaits for all producers to finish producing work items
    await asyncio.gather(*producers)

    # Blocks until all items in the queue have been received and consumed
    await q.join()  # Implicitly awaits consumers, too

    # Consumers are still awaiting additional work items. Shut the down.
    for c in consumers:
        c.cancel()


if __name__ == '__main__':
    # Enable repeatable runs
    random.seed(444)

    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--producer-count', type=int, default=5)
    parser.add_argument('-c', '--consumer-count', type=int, default=10)
    args = parser.parse_args()

    start = time.perf_counter()
    asyncio.run(main(**args.__dict__))
    finished = time.perf_counter()
    elapsed = finished - start
    print(f'Program completed in {elapsed:0.5f} seconds.')
