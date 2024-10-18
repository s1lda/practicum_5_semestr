from pages.login_page import LoginPage
from playwright.sync_api import expect

def test_empty_login(page):
    login_page = LoginPage(page)
    login_page.navigate()  
    login_page.login("", "")  
    error_message = page.locator("h3").inner_text()
    assert error_message == "Epic sadface: Username is required"