import asyncio
import re
from pathlib import Path

import zendriver
from websockets import ConnectionClosedError


class TokiSearcher:
    MANATOKI_URL = "https://manatoki469.net/comic"
    CAPTCHA_URL = "https://manatoki469.net/bbs/captcha.php"
    SEARCH_PATH = Path.cwd() / "searches"
    PAGE_LOAD_DELAY = 1.0
    IMAGE_DOWNLOAD_DELAY = 0.5

    def __init__(self, args):
        self.url = args.url
        self.search = args.search

    async def run(self):
        if not self.url:
            return

        if not self.search:
            return

        browser = await zendriver.start(
            headless=False
        )

        await self.load_cookies(browser)
        page = await browser.get(self.url)
        await self.wait_until_page_load(page)

        urls = list()
        for url in await self.get_urls(page):
            urls.append(re.sub("&spage=1$", "", url.attrs["href"]))

        if not TokiSearcher.SEARCH_PATH.exists():
            TokiSearcher.SEARCH_PATH.mkdir(parents=True, exist_ok=True)

        title = await self.get_title(page)
        search_path = Path(TokiSearcher.SEARCH_PATH / f"{title}.txt")

        with open(search_path, "w", encoding="utf-8") as f:
            for url in urls:
                f.write(url + "\n")

        await self.save_cookies(browser)
        await self.stop_browser(browser)

    async def load_cookies(self, browser):
        try:
            await browser.cookies.load()

        except FileNotFoundError:
            pass

    async def save_cookies(self, browser):
        try:
            await browser.cookies.save()

        except ConnectionClosedError:
            pass

    async def stop_browser(self, browser):
        try:
            await browser.stop()

        except ConnectionClosedError:
            pass

    async def wait_until_page_load(self, page):
        while True:
            if self.is_browser_stopped(page):
                break

            if not self.is_captcha_passed(page):
                continue

            if self.is_page_loaded(page):
                break

            await asyncio.sleep(TokiSearcher.PAGE_LOAD_DELAY)

    def is_browser_stopped(self, page):
        return page.browser.stopped

    def is_captcha_passed(self, page):
        return re.match(f"{TokiSearcher.CAPTCHA_URL}.*", page.url) is None

    def is_page_loaded(self, page):
        return re.match(f"{TokiSearcher.MANATOKI_URL}/\\d+", page.url) is not None

    async def get_urls(self, page):
        return await page.select_all(".list-item div a")

    async def get_title(self, page):
        return (await page.select('.view-title .view-content span b')).text.strip()
