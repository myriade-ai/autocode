import io

from PIL import Image
from playwright.sync_api import sync_playwright


def render_url_and_return_screenshot(url: str):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url)
        page.wait_for_timeout(1000)
        screenshot_bytes = page.screenshot(path="./screenshot.png")
        browser.close()
        return Image.open(io.BytesIO(screenshot_bytes))
