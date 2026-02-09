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
        help="URL to download"
    )

    args = parser.parse_args()

    if args.captcha:
        await TokiCaptcha(args).run()
        await TokiDownloader(args).run()

    else:
        await TokiDownloader(args).run()

if __name__ == "__main__":
    asyncio.run(main())
