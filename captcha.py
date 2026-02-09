import asyncio
import re

import zendriver
from websockets import ConnectionClosedError


class TokiCaptcha:
    CAPTCHA_URL = "https://manatoki469.net/bbs/captcha.php"
    PAGE_LOAD_DELAY = 1.0

    def __init__(self, args):
        pass

    async def run(self):
        browser = await zendriver.start(
            headless=False
        )

        page = await browser.get(TokiCaptcha.CAPTCHA_URL)
        await self.wait_until_captcha_pass(page)

        await self.save_cookies(browser)
        await self.stop_browser(browser)

    async def wait_until_captcha_pass(self, page):
        while True:
            if self.is_browser_stopped(page.browser):
                break

            if self.is_captcha_passed(page):
                break

            await asyncio.sleep(TokiCaptcha.PAGE_LOAD_DELAY)

    def is_browser_stopped(self, browser):
        return browser.stopped

    def is_captcha_passed(self, page):
        return re.match(f"{TokiCaptcha.CAPTCHA_URL}.*", page.url) is None

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