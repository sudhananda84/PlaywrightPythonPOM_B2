import re

from playwright.sync_api import sync_playwright, expect

# The public demo site can be slow, so allow up to 15 seconds for every assertion
expect.set_options(timeout=15_000)


# Each test is fully independent: it launches its own browser, logs in, runs the
# complete flow with hard coded data, cleans up the data it created and logs out.


def test_pim_01_create_employee_with_mandatory_fields_only():
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

        # ---------- Navigate to PIM > Add Employee ----------
        page.get_by_role("link", name="PIM").click()
        expect(page.get_by_role("heading", name="Employee Information")).to_be_visible()
        page.get_by_role("button", name="Add").click()
        expect(page.get_by_role("heading", name="Add Employee")).to_be_visible()

        # ---------- Fill mandatory fields only ----------
        page.locator("input[name='firstName']").fill("Ravi")
        expect(page.locator("input[name='middleName']")).to_have_value("")
        page.locator("input[name='lastName']").fill("Kumarpim")

        employee_id_field = page.locator("//label[text()='Employee Id']/../following-sibling::div/input")
        expect(employee_id_field).not_to_have_value("")
        employee_id = employee_id_field.input_value()
        print("Auto generated Employee Id:", employee_id)

        # Create Login Details toggle stays OFF
        expect(page.locator("//label[text()='Username']")).to_have_count(0)

        page.get_by_role("button", name="Save").click()

        # ---------- Verify saved ----------
        expect(page.locator(".oxd-toast")).to_contain_text("Successfully Saved")
        expect(page).to_have_url(re.compile("pim/viewPersonalDetails"))
        expect(page.get_by_role("heading", name="Personal Details")).to_be_visible()
        expect(page.locator("input[name='firstName']")).to_have_value("Ravi")
        expect(page.locator("input[name='lastName']")).to_have_value("Kumarpim")

        # ---------- Search in Employee List ----------
        page.get_by_role("link", name="Employee List").click()
        expect(page.get_by_role("heading", name="Employee Information")).to_be_visible()
        page.locator("//label[text()='Employee Id']/../following-sibling::div/input").fill(employee_id)
        page.get_by_role("button", name="Search").click()
        rows = page.locator(".oxd-table-card")
        expect(rows).to_have_count(1)
        expect(rows.first).to_contain_text(employee_id)
        expect(rows.first).to_contain_text("Ravi")
        expect(rows.first).to_contain_text("Kumarpim")

        # ---------- Cleanup: delete the employee ----------
        rows.first.locator("i.bi-trash").click()
        page.get_by_role("button", name="Yes, Delete").click()
        expect(page.locator(".oxd-toast")).to_contain_text("Successfully Deleted")

        # ---------- Logout ----------
        page.locator(".oxd-userdropdown-tab").click()
        page.get_by_role("menuitem", name="Logout").click()
        expect(page).to_have_url(re.compile("auth/login"))
        expect(page.get_by_placeholder("Username")).to_be_visible()
        page.go_back()
        expect(page).to_have_url(re.compile("auth/login"))

        context.close()
        browser.close()


def test_pim_02_create_employee_with_all_fields_and_login_details():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        # ---------- Login as Admin ----------
        page.goto("https://opensource-demo.orangehrmlive.com/web/index.php/auth/login")
        expect(page.get_by_placeholder("Username")).to_be_visible()
        page.get_by_placeholder("Username").fill("Admin")
        page.get_by_placeholder("Password").fill("admin123")
        page.get_by_role("button", name="Login").click()
        expect(page.get_by_role("heading", name="Dashboard")).to_be_visible()

        # ---------- Navigate to PIM > Add Employee ----------
        page.get_by_role("link", name="PIM").click()
        page.get_by_role("button", name="Add").click()
        expect(page.get_by_role("heading", name="Add Employee")).to_be_visible()

        # ---------- Fill all fields ----------
        page.locator("input[name='firstName']").fill("Arjun")
        page.locator("input[name='middleName']").fill("K")
        page.locator("input[name='lastName']").fill("Reddypim")
        employee_id_field = page.locator("//label[text()='Employee Id']/../following-sibling::div/input")
        employee_id_field.fill("")
        employee_id_field.fill("QA1003")
        expect(page.get_by_text("Employee Id already exists")).to_have_count(0)

        # Build a 200x200 jpg in memory (no files on disk needed) and upload it
        photo_page = context.new_page()
        photo_page.set_viewport_size({"width": 200, "height": 200})
        photo_page.set_content("<body style='margin:0;background:#ff7b1d'></body>")
        photo_bytes = photo_page.screenshot(type="jpeg")
        photo_page.close()
        page.locator("input[type='file']").set_input_files(
            {"name": "arjun.jpg", "mimeType": "image/jpeg", "buffer": photo_bytes}
        )
        expect(page.locator("img.employee-image")).to_have_attribute("src", re.compile("^data:image"))

        page.locator(".oxd-switch-input").click()
        expect(page.locator("//label[text()='Username']")).to_be_visible()

        page.locator("//label[text()='Username']/../following-sibling::div/input").fill("arjun.qa1003")
        page.locator("//label[normalize-space()='Enabled']").click()
        page.locator("//label[text()='Password']/../following-sibling::div/input").fill("Test@1234")
        page.locator("//label[text()='Confirm Password']/../following-sibling::div/input").fill("Test@1234")
        expect(page.get_by_text("Username already exists")).to_have_count(0)

        page.get_by_role("button", name="Save").click()

        # ---------- Verify saved ----------
        expect(page.locator(".oxd-toast")).to_contain_text("Successfully Saved")
        expect(page.get_by_role("heading", name="Personal Details")).to_be_visible()
        expect(page.locator("input[name='firstName']")).to_have_value("Arjun")
        expect(page.locator("input[name='middleName']")).to_have_value("K")
        expect(page.locator("input[name='lastName']")).to_have_value("Reddypim")
        expect(page.locator("img.employee-image")).to_be_visible()

        # ---------- Logout Admin ----------
        page.locator(".oxd-userdropdown-tab").click()
        page.get_by_role("menuitem", name="Logout").click()
        expect(page).to_have_url(re.compile("auth/login"))

        # ---------- Login as the newly created employee ----------
        page.get_by_placeholder("Username").fill("arjun.qa1003")
        page.get_by_placeholder("Password").fill("Test@1234")
        page.get_by_role("button", name="Login").click()
        # After login the app may open the Dashboard or the last visited page (Arjun's own
        # Personal Details), so verify the logged in user instead of a specific page
        expect(page.locator(".oxd-userdropdown-name")).to_contain_text("Arjun")
        expect(page).not_to_have_url(re.compile("auth/login"))
        expect(page.get_by_role("link", name="My Info")).to_be_visible()
        expect(page.get_by_role("link", name="Admin")).to_have_count(0)
        expect(page.get_by_role("link", name="PIM")).to_have_count(0)

        # ---------- Logout employee ----------
        page.locator(".oxd-userdropdown-tab").click()
        page.get_by_role("menuitem", name="Logout").click()
        expect(page).to_have_url(re.compile("auth/login"))

        # ---------- Cleanup: login as Admin and delete the employee ----------
        page.get_by_placeholder("Username").fill("Admin")
        page.get_by_placeholder("Password").fill("admin123")
        page.get_by_role("button", name="Login").click()
        # The app may reopen the last visited page instead of the Dashboard after a re-login
        expect(page.locator(".oxd-userdropdown-name")).to_be_visible()
        expect(page).not_to_have_url(re.compile("auth/login"))
        page.get_by_role("link", name="PIM").click()
        page.locator("//label[text()='Employee Id']/../following-sibling::div/input").fill("QA1003")
        page.get_by_role("button", name="Search").click()
        rows = page.locator(".oxd-table-card")
        expect(rows).to_have_count(1)
        rows.first.locator("i.bi-trash").click()
        page.get_by_role("button", name="Yes, Delete").click()
        expect(page.locator(".oxd-toast")).to_contain_text("Successfully Deleted")

        # ---------- Logout ----------
        page.locator(".oxd-userdropdown-tab").click()
        page.get_by_role("menuitem", name="Logout").click()
        expect(page).to_have_url(re.compile("auth/login"))
        expect(page.get_by_placeholder("Username")).to_be_visible()

        context.close()
        browser.close()


def test_pim_03_mandatory_field_validation():
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

        # ---------- Navigate to PIM > Add Employee ----------
        page.get_by_role("link", name="PIM").click()
        page.get_by_role("button", name="Add").click()
        expect(page.get_by_role("heading", name="Add Employee")).to_be_visible()

        first_name_error = page.locator("input[name='firstName']").locator("xpath=../following-sibling::span")
        last_name_error = page.locator("input[name='lastName']").locator("xpath=../following-sibling::span")

        # ---------- Case a: all fields empty ----------
        page.get_by_role("button", name="Save").click()
        expect(first_name_error).to_have_text("Required")
        expect(last_name_error).to_have_text("Required")
        expect(page).to_have_url(re.compile("pim/addEmployee"))

        # ---------- Case b: only First Name entered ----------
        page.locator("input[name='firstName']").fill("Johnval")
        page.get_by_role("button", name="Save").click()
        expect(first_name_error).to_have_count(0)
        expect(last_name_error).to_have_text("Required")
        expect(page).to_have_url(re.compile("pim/addEmployee"))

        # ---------- Case c: login details toggle ON, login fields empty ----------
        page.locator("input[name='lastName']").fill("Doeval")
        page.locator(".oxd-switch-input").click()
        page.get_by_role("button", name="Save").click()
        username_error = page.locator("//label[text()='Username']/../following-sibling::span")
        password_error = page.locator("//label[text()='Password']/../following-sibling::span")
        expect(username_error).to_have_text("Required")
        expect(password_error).to_have_text("Required")
        expect(page).to_have_url(re.compile("pim/addEmployee"))

        # ---------- Verify no record was created ----------
        page.get_by_role("link", name="PIM").click()
        expect(page.get_by_role("heading", name="Employee Information")).to_be_visible()
        page.locator("//label[text()='Employee Name']/../following-sibling::div//input").fill("Johnval Doeval")
        page.get_by_role("button", name="Search").click()
        expect(page.locator(".orangehrm-horizontal-padding span")).to_have_text("No Records Found")

        # ---------- Logout ----------
        page.locator(".oxd-userdropdown-tab").click()
        page.get_by_role("menuitem", name="Logout").click()
        expect(page).to_have_url(re.compile("auth/login"))
        expect(page.get_by_placeholder("Username")).to_be_visible()

        context.close()
        browser.close()


def test_pim_04_duplicate_employee_id_username_and_weak_password():
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

        # ---------- Precondition: create employee QA1101 with username anita.qa1101 ----------
        page.get_by_role("link", name="PIM").click()
        page.get_by_role("button", name="Add").click()
        expect(page.get_by_role("heading", name="Add Employee")).to_be_visible()
        page.locator("input[name='firstName']").fill("Anita")
        page.locator("input[name='lastName']").fill("Sharmadup")
        page.locator("//label[text()='Employee Id']/../following-sibling::div/input").fill("QA1101")
        page.locator(".oxd-switch-input").click()
        page.locator("//label[text()='Username']/../following-sibling::div/input").fill("anita.qa1101")
        page.locator("//label[text()='Password']/../following-sibling::div/input").fill("Test@1234")
        page.locator("//label[text()='Confirm Password']/../following-sibling::div/input").fill("Test@1234")
        page.get_by_role("button", name="Save").click()
        expect(page.locator(".oxd-toast")).to_contain_text("Successfully Saved")
        expect(page.get_by_role("heading", name="Personal Details")).to_be_visible()

        # ---------- Open Add Employee for the new employee ----------
        page.get_by_role("link", name="Add Employee").click()
        expect(page.get_by_role("heading", name="Add Employee")).to_be_visible()
        page.locator("input[name='firstName']").fill("Mohan")
        page.locator("input[name='lastName']").fill("Daspim")

        employee_id_field = page.locator("//label[text()='Employee Id']/../following-sibling::div/input")
        employee_id_error = page.locator("//label[text()='Employee Id']/../following-sibling::span")
        username_field = page.locator("//label[text()='Username']/../following-sibling::div/input")
        username_error = page.locator("//label[text()='Username']/../following-sibling::span")
        password_field = page.locator("//label[text()='Password']/../following-sibling::div/input")
        password_error = page.locator("//label[text()='Password']/../following-sibling::span")
        confirm_field = page.locator("//label[text()='Confirm Password']/../following-sibling::div/input")
        confirm_error = page.locator("//label[text()='Confirm Password']/../following-sibling::span")

        # ---------- Duplicate Employee Id ----------
        employee_id_field.fill("QA1101")
        expect(employee_id_error).to_have_text("Employee Id already exists")

        employee_id_field.fill("QA1102")
        expect(employee_id_error).to_have_count(0)

        # ---------- Duplicate Username ----------
        page.locator(".oxd-switch-input").click()
        username_field.fill("anita.qa1101")
        expect(username_error).to_have_text("Username already exists")

        # ---------- Username shorter than 5 characters ----------
        username_field.fill("abc")
        expect(username_error).to_have_text("Should be at least 5 characters")

        username_field.fill("mohan.qa1102")
        expect(username_error).to_have_count(0)

        # ---------- Password shorter than 7 characters ----------
        password_field.fill("abc1")
        expect(password_error).to_have_text("Should have at least 7 characters")

        # ---------- Password without a number ----------
        password_field.fill("abcdefg")
        expect(password_error).to_have_text("Your password must contain minimum 1 number")

        # ---------- Password mismatch ----------
        password_field.fill("Test@1234")
        confirm_field.fill("Test@9999")
        expect(confirm_error).to_have_text("Passwords do not match")

        # ---------- All valid -> Save ----------
        confirm_field.fill("Test@1234")
        expect(confirm_error).to_have_count(0)
        page.get_by_role("button", name="Save").click()
        expect(page.locator(".oxd-toast")).to_contain_text("Successfully Saved")
        expect(page.get_by_role("heading", name="Personal Details")).to_be_visible()

        # ---------- Cleanup: delete both employees ----------
        page.get_by_role("link", name="Employee List").click()
        page.locator("//label[text()='Employee Id']/../following-sibling::div/input").fill("QA1101")
        page.get_by_role("button", name="Search").click()
        expect(page.locator(".oxd-table-card")).to_have_count(1)
        page.locator(".oxd-table-card").first.locator("i.bi-trash").click()
        page.get_by_role("button", name="Yes, Delete").click()
        expect(page.locator(".oxd-toast")).to_contain_text("Successfully Deleted")

        page.locator("//label[text()='Employee Id']/../following-sibling::div/input").fill("QA1102")
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
