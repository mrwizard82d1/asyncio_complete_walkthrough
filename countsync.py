#! py -3

"""A synchronous implementation of 'Hello World' of async IO.

This code si taken from https://realpython.com/async-io-python/.
"""

import time


def count():
    # Prints a "report" to `stdout` before waiting for other "work."
    print("One")

    # This call **synchronously** waits for 1 second. This wait simulates real work. Importantly, it allows **no**
    # other work to run while we wait.
    time.sleep(1)

    # Print a "report" to `stdout` when "work" finished.
    print("Two")

    # The call to `sleep` results in each "task" printing "One" to `stdout` and then **blocking** while the "other"
    # work completes, and it then prints "Two" to `stdout`. Consequently, this script prints **both** messages to
    # `stdout` before any other "task" runs.


# Any function containing an "awaitable" must be marked as `async`
def main():
    unused_side_effect = (count(), count(), count())


if __name__ == '__main__':
    # Start a performance counter
    start = time.perf_counter()

    # Invoke all the "work" of this "application."
    main()

    # Calculate and report the elapsed time. Should be ~3.0 second because each of the previous sleeps occur
    # **synchronously**.
    elapsed = time.perf_counter() - start
    print(f'{__file__} executed in {elapsed:0.2f} seconds.')
