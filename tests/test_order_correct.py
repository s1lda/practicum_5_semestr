from pages.login_page import LoginPage
from pages.inventory_page import ProductsPage
from pages.cart_page import CartPage
from pages.checkout_page import CheckoutPage
from pages.checkout_finish_page import CheckoutFinishPage
def test_order_correct(page):
    login_page = LoginPage(page)
    login_page.navigate()  
    login_page.login("standard_user", "secret_sauce")
    products=ProductsPage(page)  
    products.click_button_add_to_cart("sauce-labs-backpack")
    products.click_button_shopping_cart()    
    cart_page = CartPage(page)
    cart_page.click_button_checkout()
    checkout_page=CheckoutPage(page)
    checkout_page.fill_checkout_info("Damir","Sagalbaev","09.09.2004")
    checkout_finish_page=CheckoutFinishPage(page)
    checkout_finish_page.click_button_finish()
    assert  checkout_finish_page.correct_finish.is_visible()
