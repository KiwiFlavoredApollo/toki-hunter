import asyncio
import re
from pathlib import Path

import logging
import zendriver
from websockets import ConnectionClosedError


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setLevel(logging.INFO)
handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
logger.addHandler(handler)
logger.addHandler(handler)


class TokiDownloader:
    MANATOKI_URL = "https://manatoki469.net/comic"
    DOWNLOAD_PATH = Path.cwd() / "downloads"
    PAGE_LOAD_DELAY = 1.0
    IMAGE_DOWNLOAD_DELAY = 0.5

    def __init__(self, args):
        self.url = args.url

    async def run(self):
        browser = await zendriver.start(
            headless=False
        )

        await self.load_cookies(browser)
        page = await browser.get(self.url)
        await self.wait_until_page_load(page)
        title = await self.get_title(page)
        download_path = await self.get_download_path(title)

        if download_path.exists():
            logger.info(f"Skipped downloading {title}.")
            logger.warning(f"{title} already exists.")
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

            await asyncio.sleep(TokiDownloader.IMAGE_DOWNLOAD_DELAY)

        self.remove_non_png_file(download_path)
        await self.save_cookies(browser)
        await self.stop_browser(browser)

        logger.info(f"Downloaded {title}.")

    async def wait_until_page_load(self, page):
        while True:
            if self.is_browser_stopped(page.browser):
                break

            if self.is_page_loaded(page):
                break

            await asyncio.sleep(TokiDownloader.PAGE_LOAD_DELAY)

        await page.wait_for_ready_state("complete")

    def is_browser_stopped(self, browser):
        return browser.stopped

    def is_page_loaded(self, page):
        return re.match(f"{TokiDownloader.MANATOKI_URL}/\\d+", page.url) is not None

    async def get_title(self, page):
        title = await page.select('.toon-title')
        return title.attrs['title']

    async def get_download_path(self, title):
        return Path(TokiDownloader.DOWNLOAD_PATH / title)

    async def get_images(self, page):
        return await page.select_all(".view-padding div img")

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
