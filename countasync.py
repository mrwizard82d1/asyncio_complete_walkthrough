#! py -3

"""'Hello World' of async IO.

This code si taken from https://realpython.com/async-io-python/.
"""

import asyncio
import time


async def count():
    # Prints a "report" to `stdout` before waiting for other "work."
    print("One")

    # This call asynchronously waits for 1 second. This asynchronous wait simulates real work. More importantly,
    # it allows other work to run while we wait.
    await asyncio.sleep(1)

    # Print a "report" to `stdout` when "work" finished.
    print("Two")

    # The call to `sleep` results in each "task" printing "One" to `stdout` before any other task printing "Two."
    # Contrast this behavior with `countsync.py` in which each "task" prints **both** messages to `stdout` before
    # returning and allowing other "tasks" to run.


# Any function containing an "awaitable" must be marked as `async`
async def main():
    # Pauses this function until **all** child asynchronous work has completed
    await asyncio.gather(count(), count(), count())


if __name__ == '__main__':
    # Start a performance counter
    start = time.perf_counter()

    # Begin the `asyncio` event-loop executing the top-level asynchronous function.
    asyncio.run(main())

    # Calculate and report the elapsed time. Should be ~1.0 second because all the previous sleeps occur
    # **concurrently**.
    elapsed = time.perf_counter() - start
    print(f'{__file__} executed in {elapsed:0.2f} seconds.')
