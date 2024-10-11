from pages.login_page import LoginPage
from playwright.sync_api import expect

def test_error_login(page):
    login_page = LoginPage(page)
    login_page.navigate()  
    login_page.login("standard_user", "wrong_password")  
    error_message = page.locator("h3").inner_text()
    assert error_message == "Epic sadface: Username and password do not match any user in this service"