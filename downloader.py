import asyncio
import re
from operator import truediv

from pathlib import Path
import zendriver
from websockets import ConnectionClosedError, ConnectionClosed
from zendriver.core.cloudflare import cf_is_interactive_challenge_present


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
        download_path = await self.get_download_path(page)

        if download_path.exists():
            await self.save_cookies(browser)
            await browser.stop()
            return

        await page.set_download_path(download_path)

        for index, image in enumerate(await self.get_images(page)):
            try:
                filename = f"{await self.get_title(page)} - {index:04d}.png"
                await page.download_file(self.get_image_url(image), filename)

            except IndexError:
                pass

            await asyncio.sleep(TokiDownloader.IMAGE_DOWNLOAD_DELAY)

        self.remove_non_png_file(download_path)
        await self.save_cookies(browser)
        await browser.stop()

    async def load_cookies(self, browser):
        try:
            await browser.cookies.load()

        except FileNotFoundError:
            pass

    async def save_cookies(self, browser):
        try:
            await browser.cookies.save()

        except ConnectionClosed:
            pass

    async def wait_until_page_load(self, page):
        while True:
            if await cf_is_interactive_challenge_present(page):
                continue

            if self.is_page_loaded(page):
                break

            await asyncio.sleep(TokiDownloader.PAGE_LOAD_DELAY)

        await page.wait_for_ready_state("complete")

    async def get_title(self, page):
        title = await page.select('.toon-title')
        return title.attrs['title']

    async def get_download_path(self, page):
        title = await self.get_title(page)
        return Path(TokiDownloader.DOWNLOAD_PATH / title)

    async def get_images(self, page):
        return await page.select_all(".view-padding div img")

    def get_image_url(self, image):
        return image.attributes[3]

    def remove_non_png_file(self, download_path):
        for file in download_path.iterdir():
            if file.is_file() and file.suffix.lower() != ".png":
                file.unlink()

    def is_page_loaded(self, page):
        return re.match(f"{TokiDownloader.MANATOKI_URL}/\\d+", page.url) is not None
