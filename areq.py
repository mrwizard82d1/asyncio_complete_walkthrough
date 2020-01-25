#! py -3

"""Asynchronously get links embedded in multiple pages' HTML.

This is an example "application" using `asyncio`, `aiohttp`, and `aiofiles`.
"""

import asyncio
import logging
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

    logger.info('Send request')
    response = await session.request(method='GET', url=url, **kwargs)
    logger.info(f'Got response [{response.status}] for URL, {url}]')

    # Raise an exception if the HTTP status code is not OK (200)
    response.raise_for_status()

    # Asynchronously get the response content
    logger.info('Start getting response content')
    html = await response.text()
    logger.info('End getting response content')
    return html


async def main():
    async with aiohttp.ClientSession() as session:
        url = 'http://www.foxnews.com'
        html = await fetch_html(url, session)
        logger.info(f'Read html: {html[:256]}')


if __name__ == '__main__':
    asyncio.run(main())
