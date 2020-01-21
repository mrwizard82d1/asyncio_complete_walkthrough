#! py -3

import asyncio
import random

# ANSI (escape) colors
COLORS = (
    '\033[0m',  # End of colored output
    '\033[36m',  # Cyan
    '\033[91m',  # Red
    '\033[35m',  # Magenta
)
END_COLOR = 0


async def make_random(ndx: int, threshold: int = 6) -> int:
    print(f'{COLORS[ndx + 1]}Initiated make_random({ndx}).')
    candidate = random.randint(0, 10)
    while candidate < threshold:
        print(f'{COLORS[ndx + 1]}make_random({ndx})={candidate} too low. Retrying.')
        # Emulate doing real work; `await` allows other co-routines to run.
        await asyncio.sleep(ndx + 1)
        candidate = random.randint(0, 10)
    print(f'{COLORS[ndx + 1]}---> Finished: make_random({ndx})={candidate}{COLORS[END_COLOR]}')
    return candidate


async def main():
    results = await asyncio.gather(*(make_random(i, 10 - 1 - 1) for i in range(3)))
    return results


if __name__ == '__main__':
    random.seed(444)
    r1, r2, r3 = asyncio.run(main())
    print()
    print(f'r1={r1}, r2={r2}, r3={r3}')
