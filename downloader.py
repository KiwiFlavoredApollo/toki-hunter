import asyncio
import logging
import random
import re
from pathlib import Path

import zendriver
from websockets import ConnectionClosedError


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setLevel(logging.INFO)
handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
logger.addHandler(handler)


class TokiDownloader:
    MANATOKI_URL = "https://manatoki469.net/comic"
    CAPTCHA_URL = "https://manatoki469.net/bbs/captcha.php"
    DOWNLOAD_PATH = Path.cwd() / "downloads"
    PAGE_LOAD_DELAY = 1.0
    IMAGE_DOWNLOAD_DELAY = 1.0

    def __init__(self, args):
        self.url = args.url
        self.search = args.search
        self.headless = args.headless

    async def run(self):
        if not self.url:
            return

        if self.search:
            return

        browser = await zendriver.start(
            headless=self.headless
        )

        await self.load_cookies(browser)
        page = await browser.get(self.url)
        await self.wait_until_page_load(page)
        title = await self.get_title(page)
        download_path = await self.get_download_path(title)

        if download_path.exists():
            logger.warning(f"{title} already exists.")
            logger.info(f"Skipped downloading {title}.")
            await self.save_cookies(browser)
            await self.stop_browser(browser)
            return

        await page.set_download_path(download_path)

        for index, image in enumerate(await self.get_images(page)):
            try:
                filename = f"{title} - {index:04d}.png"
                await page.download_file(self.get_image_url(image), filename)

            except IndexError:
                pass

            except ConnectionClosedError:
                break

            await asyncio.sleep(self.get_image_download_delay())

        await self.save_cookies(browser)
        await self.stop_browser(browser)
        self.remove_non_png_file(download_path)

        logger.info(f"Downloaded {title}.")

    async def wait_until_page_load(self, page):
        while True:
            if self.is_browser_stopped(page):
                break

            if not self.is_captcha_passed(page):
                continue

            if self.is_page_loaded(page):
                break

            await asyncio.sleep(TokiDownloader.PAGE_LOAD_DELAY)

        await asyncio.sleep(TokiDownloader.PAGE_LOAD_DELAY)

    def is_browser_stopped(self, page):
        return page.browser.stopped

    def is_captcha_passed(self, page):
        return re.match(f"{TokiDownloader.CAPTCHA_URL}.*", page.url) is None

    def is_page_loaded(self, page):
        return re.match(f"{TokiDownloader.MANATOKI_URL}/\\d+", page.url) is not None

    async def get_title(self, page):
        return (await page.select('.toon-title')).attrs['title']

    async def get_download_path(self, title):
        return Path(TokiDownloader.DOWNLOAD_PATH / title)

    async def get_images(self, page):
        return list(filter(lambda image: image.attributes[3] != "", await page.select_all(".view-padding div img")))

    def get_image_url(self, image):
        return image.attributes[3]

    def remove_non_png_file(self, download_path):
        for file in download_path.iterdir():
            if file.is_file() and file.suffix.lower() != ".png":
                file.unlink()

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

    def get_image_download_delay(self):
        minimum = TokiDownloader.IMAGE_DOWNLOAD_DELAY * 0.5
        maximum = TokiDownloader.IMAGE_DOWNLOAD_DELAY * 1.5
        return random.uniform(minimum, maximum)
