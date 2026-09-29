import time

from playwright.sync_api import sync_playwright, expect

p = sync_playwright().start()
browser = p.chromium.launch(headless=False)
context = browser.new_context()
page = context.new_page()

page.goto("https://opensource-demo.orangehrmlive.com/web/index.php/auth/login")
expect(page).to_have_title("OrangeHRM")
user_field = page.get_by_role("textbox", name="username")

expect(user_field).to_have_attribute("placeholder", "Username")
expect(user_field).to_have_value("")


user_field.fill("admin")
page.get_by_role("textbox", name="password").fill("test1234")
page.get_by_role("button").click()

expect(page.get_by_role("alert")).to_be_visible()
expect(page.get_by_role("alert")).to_contain_text("Invalid")




time.sleep(5)
browser.close()

