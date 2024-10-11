class CartPage:
    def __init__(self, page):
        self.page = page
        self.first_name = page.locator('[data-test="firstName"]')
        self.last_name = page.locator('[data-test="lastName"]')
        self.postal_code = page.locator('[data-test="postalCode"]')
        self.button_checkout = page.locator('[data-test="checkout"]')
        self.button_cancel = page.locator('[data-test="cancel"]')
        self.button_continue = page.locator('[data-test="continue"]')
        self.button_finish = page.locator('[data-test="finish"]')
        self.button_back_to_products = page.locator('[data-test="back-to-products"]')
        self.remove_button_prefix = "[data-test='remove-"
        self.error_msg = page.locator('[data-test="error"]')
        self.cart_items = page.locator(".cart_item")
        self.remove_buttons = page.locator("button:has-text('Remove')")

    def fill_checkout_info(
        self, first_name, last_name, postal_code):
        self.first_name.fill(first_name)
        self.last_name.fill(last_name)
        self.postal_code.fill(postal_code)
        self.button_continue.click()

    def click_button_checkout(self):
        self.button_checkout.click()

    def click_button_cancel(self):
        self.button_cancel.click()

    def click_button_finish(self):
        self.button_finish.click()
    
    def click_button_continue(self):
        self.button_continue.click()

    def click_button_back_to_products(self):
        self.button_back_to_products.click()

    def is_error_visible(self):
        return self.page.is_visible(self.error_msg)

    def remove_item(self, product_name):
        remove_button_locator = f"{self.remove_button_prefix}{product_name}']"
        self.page.click(remove_button_locator)

    def remove_all_items(self):
        total_items = self.cart_items.count()

        for _ in range(total_items):
            self.remove_buttons.nth(0).click()

    def get_cart_list(self):
        return self.cart_items.all_text_contents()
