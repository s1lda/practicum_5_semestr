from pages.login_page import LoginPage
from playwright.sync_api import expect
from pages.inventory_page import ProductsPage
def test_add_to_cart(page):
    login_page = LoginPage(page)
    login_page.navigate()  
    login_page.login("standard_user", "secret_sauce")
    products=ProductsPage(page)  
    products.click_button_add_to_cart("sauce-labs-backpack")
    products.click_button_shopping_cart()    
    assert products.inventory_item_name_locator.is_visible()