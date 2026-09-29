import re

from playwright.sync_api import sync_playwright, expect

# The public demo site can be slow, so allow up to 15 seconds for every assertion
expect.set_options(timeout=15_000)


# Each test is fully independent: it launches its own browser, logs in, creates its
# own employee (precondition), runs the complete flow with hard coded data, cleans up
# the data it created and logs out.
# Note: OrangeHRM open source has only two roles (Admin / ESS), so "role creation"
# is covered by creating system users and assigning them a role.


def test_adm_01_create_user_with_admin_role():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        # ---------- Login ----------
        page.goto("https://opensource-demo.orangehrmlive.com/web/index.php/auth/login")
        expect(page.get_by_placeholder("Username")).to_be_visible()
        page.get_by_placeholder("Username").fill("Admin")
        page.get_by_placeholder("Password").fill("admin123")
        page.get_by_role("button", name="Login").click()
        expect(page.get_by_role("heading", name="Dashboard")).to_be_visible()

        # ---------- Precondition: create employee Ravi Adminqa (QA2001) ----------
        page.get_by_role("link", name="PIM").click()
        page.get_by_role("button", name="Add").click()
        expect(page.get_by_role("heading", name="Add Employee")).to_be_visible()
        page.locator("input[name='firstName']").fill("Ravi")
        page.locator("input[name='lastName']").fill("Adminqa")
        page.locator("//label[text()='Employee Id']/../following-sibling::div/input").fill("QA2001")
        page.get_by_role("button", name="Save").click()
        expect(page.locator(".oxd-toast")).to_contain_text("Successfully Saved")
        expect(page.get_by_role("heading", name="Personal Details")).to_be_visible()

        # ---------- Navigate to Admin > Add User ----------
        page.get_by_role("link", name="Admin").click()
        expect(page.get_by_role("heading", name="System Users")).to_be_visible()
        page.get_by_role("button", name="Add").click()
        expect(page.get_by_role("heading", name="Add User")).to_be_visible()

        # ---------- Fill the form ----------
        page.locator("//label[text()='User Role']/../following-sibling::div//div[contains(@class,'oxd-select-text-input')]").click()
        page.get_by_role("option", name="Admin").click()

        page.get_by_placeholder("Type for hints...").fill("Ravi Adminqa")
        page.get_by_role("option", name="Ravi Adminqa").click()

        page.locator("//label[text()='Status']/../following-sibling::div//div[contains(@class,'oxd-select-text-input')]").click()
        page.get_by_role("option", name="Enabled").click()

        page.locator("//label[text()='Username']/../following-sibling::div/input").fill("ravi.admin01")
        page.locator("//label[text()='Password']/../following-sibling::div/input").fill("Admin@123")
        expect(page.locator(".orangehrm-password-chip")).to_be_visible()
        page.locator("//label[text()='Confirm Password']/../following-sibling::div/input").fill("Admin@123")

        page.get_by_role("button", name="Save").click()

        # ---------- Verify saved ----------
        expect(page.locator(".oxd-toast")).to_contain_text("Successfully Saved")
        expect(page).to_have_url(re.compile("admin/viewSystemUsers"))

        page.locator("//label[text()='Username']/../following-sibling::div/input").fill("ravi.admin01")
        page.get_by_role("button", name="Search").click()
        rows = page.locator(".oxd-table-card")
        expect(rows).to_have_count(1)
        cells = rows.first.locator(".oxd-table-cell")
        expect(cells.nth(1)).to_have_text("ravi.admin01")
        expect(cells.nth(2)).to_have_text("Admin")
        expect(cells.nth(3)).to_have_text("Ravi Adminqa")
        expect(cells.nth(4)).to_have_text("Enabled")

        # ---------- Logout Admin, login as new Admin user ----------
        page.locator(".oxd-userdropdown-tab").click()
        page.get_by_role("menuitem", name="Logout").click()
        expect(page).to_have_url(re.compile("auth/login"))

        page.get_by_placeholder("Username").fill("ravi.admin01")
        page.get_by_placeholder("Password").fill("Admin@123")
        page.get_by_role("button", name="Login").click()
        # The app may reopen the last visited page instead of the Dashboard after a re-login
        expect(page.locator(".oxd-userdropdown-name")).to_be_visible()
        expect(page).not_to_have_url(re.compile("auth/login"))
        expect(page.locator(".oxd-userdropdown-name")).to_contain_text("Ravi Adminqa")
        expect(page.get_by_role("link", name="Admin")).to_be_visible()
        expect(page.get_by_role("link", name="PIM")).to_be_visible()

        page.locator(".oxd-userdropdown-tab").click()
        page.get_by_role("menuitem", name="Logout").click()
        expect(page).to_have_url(re.compile("auth/login"))

        # ---------- Cleanup: login as Admin, delete user and employee ----------
        page.get_by_placeholder("Username").fill("Admin")
        page.get_by_placeholder("Password").fill("admin123")
        page.get_by_role("button", name="Login").click()
        # The app may reopen the last visited page instead of the Dashboard after a re-login
        expect(page.locator(".oxd-userdropdown-name")).to_be_visible()
        expect(page).not_to_have_url(re.compile("auth/login"))

        page.get_by_role("link", name="Admin").click()
        page.locator("//label[text()='Username']/../following-sibling::div/input").fill("ravi.admin01")
        page.get_by_role("button", name="Search").click()
        expect(page.locator(".oxd-table-card")).to_have_count(1)
        page.locator(".oxd-table-card").first.locator("i.bi-trash").click()
        page.get_by_role("button", name="Yes, Delete").click()
        expect(page.locator(".oxd-toast")).to_contain_text("Successfully Deleted")

        page.get_by_role("link", name="PIM").click()
        page.locator("//label[text()='Employee Id']/../following-sibling::div/input").fill("QA2001")
        page.get_by_role("button", name="Search").click()
        expect(page.locator(".oxd-table-card")).to_have_count(1)
        page.locator(".oxd-table-card").first.locator("i.bi-trash").click()
        page.get_by_role("button", name="Yes, Delete").click()
        expect(page.locator(".oxd-toast").last).to_contain_text("Successfully Deleted")

        # ---------- Logout ----------
        page.locator(".oxd-userdropdown-tab").click()
        page.get_by_role("menuitem", name="Logout").click()
        expect(page).to_have_url(re.compile("auth/login"))
        expect(page.get_by_placeholder("Username")).to_be_visible()

        context.close()
        browser.close()


def test_adm_02_create_user_with_ess_role_and_verify_access():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        # ---------- Login ----------
        page.goto("https://opensource-demo.orangehrmlive.com/web/index.php/auth/login")
        expect(page.get_by_placeholder("Username")).to_be_visible()
        page.get_by_placeholder("Username").fill("Admin")
        page.get_by_placeholder("Password").fill("admin123")
        page.get_by_role("button", name="Login").click()
        expect(page.get_by_role("heading", name="Dashboard")).to_be_visible()

        # ---------- Precondition: create employee Ravi Essqa (QA2002) ----------
        page.get_by_role("link", name="PIM").click()
        page.get_by_role("button", name="Add").click()
        expect(page.get_by_role("heading", name="Add Employee")).to_be_visible()
        page.locator("input[name='firstName']").fill("Ravi")
        page.locator("input[name='lastName']").fill("Essqa")
        page.locator("//label[text()='Employee Id']/../following-sibling::div/input").fill("QA2002")
        page.get_by_role("button", name="Save").click()
        expect(page.locator(".oxd-toast")).to_contain_text("Successfully Saved")
        expect(page.get_by_role("heading", name="Personal Details")).to_be_visible()

        # ---------- Navigate to Admin > Add User ----------
        page.get_by_role("link", name="Admin").click()
        expect(page.get_by_role("heading", name="System Users")).to_be_visible()
        page.get_by_role("button", name="Add").click()
        expect(page.get_by_role("heading", name="Add User")).to_be_visible()

        # ---------- Fill the form with ESS role ----------
        page.locator("//label[text()='User Role']/../following-sibling::div//div[contains(@class,'oxd-select-text-input')]").click()
        page.get_by_role("option", name="ESS").click()

        page.get_by_placeholder("Type for hints...").fill("Ravi Essqa")
        page.get_by_role("option", name="Ravi Essqa").click()

        page.locator("//label[text()='Status']/../following-sibling::div//div[contains(@class,'oxd-select-text-input')]").click()
        page.get_by_role("option", name="Enabled").click()

        page.locator("//label[text()='Username']/../following-sibling::div/input").fill("ravi.ess01")
        page.locator("//label[text()='Password']/../following-sibling::div/input").fill("Ess@12345")
        page.locator("//label[text()='Confirm Password']/../following-sibling::div/input").fill("Ess@12345")

        page.get_by_role("button", name="Save").click()
        expect(page.locator(".oxd-toast")).to_contain_text("Successfully Saved")
        expect(page).to_have_url(re.compile("admin/viewSystemUsers"))

        # ---------- Search with User Role filter = ESS ----------
        page.locator("//label[text()='Username']/../following-sibling::div/input").fill("ravi.ess01")
        page.locator("//label[text()='User Role']/../following-sibling::div//div[contains(@class,'oxd-select-text-input')]").click()
        page.get_by_role("option", name="ESS").click()
        page.get_by_role("button", name="Search").click()
        rows = page.locator(".oxd-table-card")
        expect(rows).to_have_count(1)
        cells = rows.first.locator(".oxd-table-cell")
        expect(cells.nth(1)).to_have_text("ravi.ess01")
        expect(cells.nth(2)).to_have_text("ESS")
        expect(cells.nth(3)).to_have_text("Ravi Essqa")
        expect(cells.nth(4)).to_have_text("Enabled")

        # ---------- Logout Admin, login as ESS user ----------
        page.locator(".oxd-userdropdown-tab").click()
        page.get_by_role("menuitem", name="Logout").click()
        expect(page).to_have_url(re.compile("auth/login"))

        page.get_by_placeholder("Username").fill("ravi.ess01")
        page.get_by_placeholder("Password").fill("Ess@12345")
        page.get_by_role("button", name="Login").click()
        # The app may reopen the last visited page instead of the Dashboard after a re-login
        expect(page.locator(".oxd-userdropdown-name")).to_be_visible()
        expect(page).not_to_have_url(re.compile("auth/login"))

        # ---------- Verify limited ESS access ----------
        expect(page.get_by_role("link", name="Admin")).to_have_count(0)
        expect(page.get_by_role("link", name="PIM")).to_have_count(0)
        expect(page.get_by_role("link", name="Leave")).to_be_visible()
        expect(page.get_by_role("link", name="Time")).to_be_visible()
        expect(page.get_by_role("link", name="My Info")).to_be_visible()
        expect(page.get_by_role("link", name="Directory")).to_be_visible()

        # ---------- Direct URL to Admin page must be blocked ----------
        page.goto("https://opensource-demo.orangehrmlive.com/web/index.php/admin/viewSystemUsers")
        expect(page.get_by_role("heading", name="System Users")).to_have_count(0)
        expect(page.get_by_text("Credential Required")).to_be_visible()

        # ---------- Logout ESS user ----------
        page.goto("https://opensource-demo.orangehrmlive.com/web/index.php/dashboard/index")
        expect(page.get_by_role("heading", name="Dashboard")).to_be_visible()
        page.locator(".oxd-userdropdown-tab").click()
        page.get_by_role("menuitem", name="Logout").click()
        expect(page).to_have_url(re.compile("auth/login"))

        # ---------- Cleanup: login as Admin, delete user and employee ----------
        page.get_by_placeholder("Username").fill("Admin")
        page.get_by_placeholder("Password").fill("admin123")
        page.get_by_role("button", name="Login").click()
        # The app may reopen the last visited page instead of the Dashboard after a re-login
        expect(page.locator(".oxd-userdropdown-name")).to_be_visible()
        expect(page).not_to_have_url(re.compile("auth/login"))

        page.get_by_role("link", name="Admin").click()
        page.locator("//label[text()='Username']/../following-sibling::div/input").fill("ravi.ess01")
        page.get_by_role("button", name="Search").click()
        expect(page.locator(".oxd-table-card")).to_have_count(1)
        page.locator(".oxd-table-card").first.locator("i.bi-trash").click()
        page.get_by_role("button", name="Yes, Delete").click()
        expect(page.locator(".oxd-toast")).to_contain_text("Successfully Deleted")

        page.get_by_role("link", name="PIM").click()
        page.locator("//label[text()='Employee Id']/../following-sibling::div/input").fill("QA2002")
        page.get_by_role("button", name="Search").click()
        expect(page.locator(".oxd-table-card")).to_have_count(1)
        page.locator(".oxd-table-card").first.locator("i.bi-trash").click()
        page.get_by_role("button", name="Yes, Delete").click()
        expect(page.locator(".oxd-toast").last).to_contain_text("Successfully Deleted")

        # ---------- Logout ----------
        page.locator(".oxd-userdropdown-tab").click()
        page.get_by_role("menuitem", name="Logout").click()
        expect(page).to_have_url(re.compile("auth/login"))
        expect(page.get_by_placeholder("Username")).to_be_visible()

        context.close()
        browser.close()


def test_adm_03_mandatory_fields_and_invalid_employee():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        # ---------- Login ----------
        page.goto("https://opensource-demo.orangehrmlive.com/web/index.php/auth/login")
        expect(page.get_by_placeholder("Username")).to_be_visible()
        page.get_by_placeholder("Username").fill("Admin")
        page.get_by_placeholder("Password").fill("admin123")
        page.get_by_role("button", name="Login").click()
        expect(page.get_by_role("heading", name="Dashboard")).to_be_visible()

        # ---------- Navigate to Admin > Add User ----------
        page.get_by_role("link", name="Admin").click()
        expect(page.get_by_role("heading", name="System Users")).to_be_visible()
        page.get_by_role("button", name="Add").click()
        expect(page.get_by_role("heading", name="Add User")).to_be_visible()

        user_role_error = page.locator("//label[text()='User Role']/../following-sibling::span")
        employee_error = page.locator("//label[text()='Employee Name']/../following-sibling::span")
        status_error = page.locator("//label[text()='Status']/../following-sibling::span")
        username_error = page.locator("//label[text()='Username']/../following-sibling::span")
        password_error = page.locator("//label[text()='Password']/../following-sibling::span")

        # ---------- Save with all fields empty ----------
        page.get_by_role("button", name="Save").click()
        expect(user_role_error).to_have_text("Required")
        expect(employee_error).to_have_text("Required")
        expect(status_error).to_have_text("Required")
        expect(username_error).to_have_text("Required")
        expect(password_error).to_have_text("Required")
        expect(page).to_have_url(re.compile("admin/saveSystemUser"))

        # ---------- Employee that does not exist ----------
        page.get_by_placeholder("Type for hints...").fill("XyzNotExist")
        expect(page.get_by_role("listbox")).to_contain_text("No Records Found")

        # ---------- Other fields valid ----------
        page.locator("//label[text()='User Role']/../following-sibling::div//div[contains(@class,'oxd-select-text-input')]").click()
        page.get_by_role("option", name="ESS").click()
        page.locator("//label[text()='Status']/../following-sibling::div//div[contains(@class,'oxd-select-text-input')]").click()
        page.get_by_role("option", name="Enabled").click()
        page.locator("//label[text()='Username']/../following-sibling::div/input").fill("test.user01")
        page.locator("//label[text()='Password']/../following-sibling::div/input").fill("Test@1234")
        page.locator("//label[text()='Confirm Password']/../following-sibling::div/input").fill("Test@1234")

        page.get_by_role("button", name="Save").click()
        expect(employee_error).to_have_text("Invalid")
        expect(page).to_have_url(re.compile("admin/saveSystemUser"))

        # ---------- Cancel and verify no user created ----------
        page.get_by_role("button", name="Cancel").click()
        expect(page.get_by_role("heading", name="System Users")).to_be_visible()
        page.locator("//label[text()='Username']/../following-sibling::div/input").fill("test.user01")
        page.get_by_role("button", name="Search").click()
        expect(page.locator(".orangehrm-horizontal-padding span")).to_have_text("No Records Found")

        # ---------- Logout ----------
        page.locator(".oxd-userdropdown-tab").click()
        page.get_by_role("menuitem", name="Logout").click()
        expect(page).to_have_url(re.compile("auth/login"))
        expect(page.get_by_placeholder("Username")).to_be_visible()

        context.close()
        browser.close()


def test_adm_04_duplicate_username_password_rules_and_disabled_user():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        # ---------- Login ----------
        page.goto("https://opensource-demo.orangehrmlive.com/web/index.php/auth/login")
        expect(page.get_by_placeholder("Username")).to_be_visible()
        page.get_by_placeholder("Username").fill("Admin")
        page.get_by_placeholder("Password").fill("admin123")
        page.get_by_role("button", name="Login").click()
        expect(page.get_by_role("heading", name="Dashboard")).to_be_visible()

        # ---------- Precondition: employee Ravi Dupqa (QA2004) with login ravi.dup04 ----------
        page.get_by_role("link", name="PIM").click()
        page.get_by_role("button", name="Add").click()
        expect(page.get_by_role("heading", name="Add Employee")).to_be_visible()
        page.locator("input[name='firstName']").fill("Ravi")
        page.locator("input[name='lastName']").fill("Dupqa")
        page.locator("//label[text()='Employee Id']/../following-sibling::div/input").fill("QA2004")
        page.locator(".oxd-switch-input").click()
        page.locator("//label[text()='Username']/../following-sibling::div/input").fill("ravi.dup04")
        page.locator("//label[text()='Password']/../following-sibling::div/input").fill("Test@1234")
        page.locator("//label[text()='Confirm Password']/../following-sibling::div/input").fill("Test@1234")
        page.get_by_role("button", name="Save").click()
        expect(page.locator(".oxd-toast")).to_contain_text("Successfully Saved")
        expect(page.get_by_role("heading", name="Personal Details")).to_be_visible()

        # ---------- Navigate to Admin > Add User ----------
        page.get_by_role("link", name="Admin").click()
        expect(page.get_by_role("heading", name="System Users")).to_be_visible()
        page.get_by_role("button", name="Add").click()
        expect(page.get_by_role("heading", name="Add User")).to_be_visible()

        page.locator("//label[text()='User Role']/../following-sibling::div//div[contains(@class,'oxd-select-text-input')]").click()
        page.get_by_role("option", name="ESS").click()
        page.get_by_placeholder("Type for hints...").fill("Ravi Dupqa")
        page.get_by_role("option", name="Ravi Dupqa").click()
        page.locator("//label[text()='Status']/../following-sibling::div//div[contains(@class,'oxd-select-text-input')]").click()
        page.get_by_role("option", name="Disabled").click()

        username_field = page.locator("//label[text()='Username']/../following-sibling::div/input")
        username_error = page.locator("//label[text()='Username']/../following-sibling::span")
        password_field = page.locator("//label[text()='Password']/../following-sibling::div/input")
        password_error = page.locator("//label[text()='Password']/../following-sibling::span")
        confirm_field = page.locator("//label[text()='Confirm Password']/../following-sibling::div/input")
        confirm_error = page.locator("//label[text()='Confirm Password']/../following-sibling::span")

        # ---------- Duplicate username ----------
        username_field.fill("ravi.dup04")
        expect(username_error).to_have_text("Already exists")

        # ---------- Username 4 characters (below boundary) ----------
        username_field.fill("abcdq")
        username_field.fill("abcd")
        expect(username_error).to_have_text("Should be at least 5 characters")

        # ---------- Username 5 characters (boundary, accepted) ----------
        username_field.fill("qadis")
        expect(username_error).to_have_count(0)

        # ---------- Password 6 characters ----------
        password_field.fill("abc123")
        expect(password_error).to_have_text("Should have at least 7 characters")

        # ---------- Password without a number ----------
        password_field.fill("abcdefgh")
        expect(password_error).to_have_text("Your password must contain minimum 1 number")

        # ---------- Password mismatch ----------
        password_field.fill("Test@1234")
        confirm_field.fill("Test@4321")
        expect(confirm_error).to_have_text("Passwords do not match")

        # ---------- Fix and save ----------
        confirm_field.fill("Test@1234")
        expect(confirm_error).to_have_count(0)
        page.get_by_role("button", name="Save").click()
        expect(page.locator(".oxd-toast")).to_contain_text("Successfully Saved")
        expect(page).to_have_url(re.compile("admin/viewSystemUsers"))

        page.locator("//label[text()='Username']/../following-sibling::div/input").fill("qadis")
        page.get_by_role("button", name="Search").click()
        rows = page.locator(".oxd-table-card")
        expect(rows).to_have_count(1)
        expect(rows.first.locator(".oxd-table-cell").nth(4)).to_have_text("Disabled")

        # ---------- Logout Admin, try to login as disabled user ----------
        page.locator(".oxd-userdropdown-tab").click()
        page.get_by_role("menuitem", name="Logout").click()
        expect(page).to_have_url(re.compile("auth/login"))

        page.get_by_placeholder("Username").fill("qadis")
        page.get_by_placeholder("Password").fill("Test@1234")
        page.get_by_role("button", name="Login").click()
        expect(page.get_by_role("alert")).to_contain_text("Account disabled")
        expect(page).to_have_url(re.compile("auth/login"))

        # ---------- Cleanup: login as Admin, delete user and employee ----------
        page.get_by_placeholder("Username").fill("Admin")
        page.get_by_placeholder("Password").fill("admin123")
        page.get_by_role("button", name="Login").click()
        # The app may reopen the last visited page instead of the Dashboard after a re-login
        expect(page.locator(".oxd-userdropdown-name")).to_be_visible()
        expect(page).not_to_have_url(re.compile("auth/login"))

        page.get_by_role("link", name="Admin").click()
        page.locator("//label[text()='Username']/../following-sibling::div/input").fill("qadis")
        page.get_by_role("button", name="Search").click()
        expect(page.locator(".oxd-table-card")).to_have_count(1)
        page.locator(".oxd-table-card").first.locator("i.bi-trash").click()
        page.get_by_role("button", name="Yes, Delete").click()
        expect(page.locator(".oxd-toast")).to_contain_text("Successfully Deleted")

        page.get_by_role("link", name="PIM").click()
        page.locator("//label[text()='Employee Id']/../following-sibling::div/input").fill("QA2004")
        page.get_by_role("button", name="Search").click()
        expect(page.locator(".oxd-table-card")).to_have_count(1)
        page.locator(".oxd-table-card").first.locator("i.bi-trash").click()
        page.get_by_role("button", name="Yes, Delete").click()
        expect(page.locator(".oxd-toast").last).to_contain_text("Successfully Deleted")

        # ---------- Logout ----------
        page.locator(".oxd-userdropdown-tab").click()
        page.get_by_role("menuitem", name="Logout").click()
        expect(page).to_have_url(re.compile("auth/login"))
        expect(page.get_by_placeholder("Username")).to_be_visible()

        context.close()
        browser.close()
