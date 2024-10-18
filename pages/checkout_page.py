class CheckoutPage:
    def __init__(self, page):
        self.page = page
        self.first_name = page.locator('[data-test="firstName"]')
        self.last_name = page.locator('[data-test="lastName"]')
        self.postal_code = page.locator('[data-test="postalCode"]')
        self.button_cancel = page.locator('[data-test="cancel"]')
        self.button_continue = page.locator('[data-test="continue"]')
        self.button_back_to_products = page.locator('[data-test="back-to-products"]')
        self.error_msg = page.locator('[data-test="error"]')    
    def fill_checkout_info(
        self, first_name, last_name, postal_code):
        self.first_name.fill(first_name)
        self.last_name.fill(last_name)
        self.postal_code.fill(postal_code)
        self.button_continue.click()


    def click_button_cancel(self):
        self.button_cancel.click()
    
    def click_button_continue(self):
        self.button_continue.click()

    def click_button_back_to_products(self):
        self.button_back_to_products.click()

    def is_error_visible(self):
        return self.page.is_visible(self.error_msg)

