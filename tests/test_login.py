from pages.login_page import LoginPage
from playwright.sync_api import expect

def test_login(page):
    login_page = LoginPage(page)
    login_page.navigate()  
    login_page.login("standard_user", "secret_sauce")  
    assert page.url =="https://www.saucedemo.com/inventory.html"