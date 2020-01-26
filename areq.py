#! py -3

"""Asynchronously get links embedded in multiple pages' HTML.

This is an example "application" using `asyncio`, `aiohttp`, and `aiofiles`.
"""

import asyncio
import logging
import pathlib
import re
import sys
from typing import IO
import urllib.error
import urllib.parse

import aiofiles
import aiohttp

# Configure logging format, level and output
logging.basicConfig(format="%(asctime)s %(levelname)s:%(name)s %(message)s",
                    level=logging.DEBUG,
                    stream=sys.stderr)

logger = logging.getLogger(__name__)

# Disable logging for the `chardet.charsetprober` package
logging.getLogger('chardet.charsetprober').disabled = True

# A regular expression for extract links from web page content
HREF_RE = re.compile(r'href="(.*?)"')


async def fetch_html(url: str, session: aiohttp.ClientSession, **kwargs) -> str:
    """Fetch the (HTML) resource from the specified URL (with options).

    Args:
        url: The (textual) URL of the request.
        session: The (asynchronous) session used to fetch responses.
        kwargs: Additional options passed unchanged to `session.request`.
    """

    logger.info(f'{url} Sent')
    response = await session.request(method='GET', url=url, **kwargs)
    logger.info(f'{url} Received [{response.status}]')

    # Raise an exception if the HTTP status code is not OK (200){
    response.raise_for_status()

    # Asynchronously get the response content
    logger.info(f'{url} Getting content')
    html = await response.text()
    logger.info(f'{url} Received content')
    return html


async def parse(url: str, session: aiohttp.ClientSession, **kwargs) -> set:
    """Find the HREFs in the HTML at url."""

    # Start with none found
    found = set()

    try:
        # Fetch the (HTML) response for `url`
        html = await fetch_html(url=url, session=session, **kwargs)
    except aiohttp.ClientError as e:
        # Log error and give up on any others
        logger.error(f'{url} aiohttp exception status={getattr(e, "status", None)},'
                     f' message={getattr(e, "message", None)}.')
        return found
    except Exception as e:
        # Log exception and give up on any others if an exception occurred
        logger.exception(f'{url} Non-aiohttp exception occurred: {getattr(e, "__dict__", {})}')
        return found
    else:
        # In all cases, process all the links in the page.
        # (I do not quite understand why this code is not in the `try` block.)
        for link in HREF_RE.findall(html):
            try:
                # Calculate the absolute link from the original URL
                absolute_link = urllib.parse.urljoin(url, link)
            except (urllib.error.URLError, ValueError):
                # Ignore any links that we cannot parse and continue processing
                logger.exception(f'{link} Error parsing. Ignoring.')
                pass
            else:
                found.add(absolute_link)
        logger.info(f'{url} Found {len(found)} links.')

        # Return all the links for this page
        return found


async def write_one(output_file_path: IO, url: str, session: aiohttp.ClientSession, **kwargs) -> None:
    """Write all HREFs found at URL to the specified output_file_path."""
    found_links = await parse(url=url, session=session, **kwargs)
    if not found_links:
        return None

    # Asynchronously write all links to output_file_path
    async with aiofiles.open(output_file_path, mode='a', encoding='utf-8') as f:
        for found_link in found_links:
            await f.write(f'{url}\t{found_link}\n')
        logger.info(f'{url} Wrote links.')


async def bulk_crawl_and_write(output_file_path: IO, urls: set, **kwargs) -> None:
    """Concurrently crawl all urls and write links found in responses to output_file_path."""

    async with aiohttp.ClientSession() as session:
        # Create a sequence of tasks (coroutines that are **not** executing on the event loop)
        tasks = [write_one(output_file_path=output_file_path, url=url, session=session, **kwargs) for url in urls]

        # Gather the result or running all these tasks on the event loop
        await asyncio.gather(*tasks)


if __name__ == '__main__':
    assert sys.version_info >= (3, 7), 'Script requires python 3.7+'

    # Calculate the parent (current) directory
    current_dir = pathlib.Path(__file__).parent

    # Synchronously read all the urls to find.
    with open(current_dir.joinpath('urls.txt')) as infile:
        urls = set(map(str.strip, infile))

    # Initialize the file containing the results
    output_file_path = current_dir.joinpath('found_urls.txt')
    with open(output_file_path, 'w') as outfile:
        outfile.write(f'Source URL\tFound link\n')

    # Asynchronously find all links at URLs and write them to the output file
    asyncio.run(bulk_crawl_and_write(output_file_path=output_file_path, urls=urls))
