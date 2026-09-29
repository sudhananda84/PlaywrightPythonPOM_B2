import re
from playwright.sync_api import Page, expect


def test_example(page: Page) -> None:
    page.goto("https://opensource-demo.orangehrmlive.com/web/index.php/auth/login")
    page.get_by_text("Forgot your password?").click()
    page.get_by_role("button", name="Cancel").click()
