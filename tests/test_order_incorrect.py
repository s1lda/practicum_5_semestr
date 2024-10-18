from pages.login_page import LoginPage
from pages.inventory_page import ProductsPage
from pages.cart_page import CartPage
from pages.checkout_page import CheckoutPage
def test_order_incorrect(page):
    login_page = LoginPage(page)
    login_page.navigate()  
    login_page.login("standard_user", "secret_sauce")
    products=ProductsPage(page)  
    products.click_button_add_to_cart("sauce-labs-backpack")
    products.click_button_shopping_cart()    
    cart_page = CartPage(page)
    cart_page.click_button_checkout()
    checkout_page=CheckoutPage(page)
    checkout_page.fill_checkout_info("","","")
    checkout_page.click_button_continue()
    assert checkout_page.error_msg.inner_text() == "Error: First Name is required"

