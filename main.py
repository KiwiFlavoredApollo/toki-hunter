import asyncio

import argparse

from captcha import TokiCaptcha
from downloader import TokiDownloader
from searcher import TokiSearcher

VERSION = "1.0.3"

async def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--version",
        action="version",
        version=VERSION
    )

    parser.add_argument(
        "--captcha",
        action="store_true",
        help="Open browser to solve CAPTCHA"
    )

    parser.add_argument(
        "--search",
        action="store_true",
        help="Search URLs from a title"
    )

    parser.add_argument(
        "--headless",
        action="store_true",
        help="Run in headless mode"
    )

    parser.add_argument(
        "url",
        type=str,
        nargs="?",
        help="URL to download or search URLs from"
    )

    args = parser.parse_args()

    await TokiCaptcha(args).run()
    await TokiDownloader(args).run()
    await TokiSearcher(args).run()

if __name__ == "__main__":
    asyncio.run(main())
