class CartPage:
    def __init__(self, page):
        self.page = page
        self.button_checkout = page.locator('[data-test="checkout"]')
        self.button_finish = page.locator('[data-test="finish"]')
        self.button_back_to_products = page.locator('[data-test="back-to-products"]')
        self.remove_button_prefix = "[data-test='remove-"
        self.cart_items = page.locator(".cart_item")
        self.remove_buttons = page.locator("button:has-text('Remove')")
    
    def click_button_checkout(self):
        self.button_checkout.click()

    def click_button_back_to_products(self):
        self.button_back_to_products.click()

    def remove_item(self, product_name):
        remove_button_locator = f"{self.remove_button_prefix}{product_name}']"
        self.page.click(remove_button_locator)

    def remove_all_items(self):
        total_items = self.cart_items.count()

        for _ in range(total_items):
            self.remove_buttons.nth(0).click()

    def get_cart_list(self):
        return self.cart_items.all_text_contents()
