from pages.login_page import LoginPage
from pages.inventory_page import ProductsPage
from pages.cart_page import CartPage
def test_delete_all_products(page):
    login_page = LoginPage(page)
    login_page.navigate()  
    login_page.login("standard_user", "secret_sauce")
    products=ProductsPage(page)  
    products.click_button_add_to_cart("sauce-labs-backpack")
    products.click_button_shopping_cart()    
    cart_page = CartPage(page)
    cart_page.remove_all_items()
    assert cart_page.cart_items.count() == 0
