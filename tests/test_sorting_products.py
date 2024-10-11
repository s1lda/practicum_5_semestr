from pages.login_page import LoginPage
from pages.inventory_page import ProductsPage

def test_sorting_products(page):
    login_page = LoginPage(page)
    login_page.navigate()
    login_page.login("standard_user", "secret_sauce")
    products_page = ProductsPage(page)
    prices = products_page.get_prices_items()
    products_page.click_button_sort_by(sort_type="lohi")
    prices_sorting = products_page.get_prices_items()
    assert prices_sorting == sorted(prices)