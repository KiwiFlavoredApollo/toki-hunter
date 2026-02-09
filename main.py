import asyncio

import argparse

from captcha import TokiCaptcha
from downloader import TokiDownloader

VERSION = "1.0.0"

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
        "url",
        type=str,
        nargs="?",
        help="URL to download"
    )

    args = parser.parse_args()

    await TokiCaptcha(args).run()
    await TokiDownloader(args).run()

if __name__ == "__main__":
    asyncio.run(main())
