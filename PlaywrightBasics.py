
from playwright.sync_api import Page, expect, sync_playwright


def test_example():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto("https://opensource-demo.orangehrmlive.com/web/index.php/auth/login")
        page.get_by_role("textbox", name="Username").click()
        page.get_by_role("textbox", name="Username").click()
        page.get_by_role("textbox", name="Username").fill("Admin")
        page.get_by_role("textbox", name="Password").click()
        page.get_by_role("textbox", name="Password").fill("admin123")
        page.get_by_role("textbox", name="Password").press("Enter")
        page.get_by_role("link", name="Admin").click()
        page.get_by_role("button", name=" Add").click()
        page.get_by_text("-- Select --").first.click()
        page.get_by_role("textbox", name="Type for hints...").click()
        page.pause()
        page.get_by_role("textbox", name="Type for hints...").fill("Test")
        page.pause()
        page.get_by_text("-- Select --").click()
        page.get_by_role("textbox").nth(2).click()
        page.get_by_role("textbox").nth(2).fill("Test12345")  #hard coded
        page.get_by_role("textbox").nth(3).click()
        page.get_by_role("textbox").nth(3).fill("Test@12345")
        page.get_by_role("textbox").nth(4).click()
        page.get_by_role("textbox").nth(4).fill("Test@12345")
        page.get_by_role("button", name="Save").click()
        page.locator("span").filter(has_text="Rohan Hiremath").click()
        page.get_by_role("menuitem", name="Logout").click()
