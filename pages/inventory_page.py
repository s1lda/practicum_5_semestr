class ProductsPage:
    def __init__(self, page):
        self.page = page
        self.username = page.locator('[data-test="username"]')
        self.password = page.locator('[data-test="password"]')
        self.login_button = page.locator('[data-test="login-button"]')
        self.add_to_cart_button_prefix = "[data-test='add-to-cart-"
        self.open_cart_button_prefix = "[data-test='inventory-item-name-"
        self.sort_container = "select.product_sort_container"
        self.button_shopping_cart = page.locator("[data-test='shopping-cart-link']")
        self.item_buttons = self.page.locator("button.btn_inventory")
        self.prices_elements = page.locator("[data-test='inventory-item-price']")
        self.cart_items = self.page.locator(".shopping_cart_badge")
        self.total_item = self.page.locator(".inventory_item")

    def click_button_add_to_cart(self, product_name: str):
        add_to_cart_locator = f"{self.add_to_cart_button_prefix}{product_name}']"
        self.page.click(add_to_cart_locator)

    def add_all_items_to_cart(self):
        for button in self.item_buttons.all():
            button.click()

    def click_button_shopping_cart(self):
        self.button_shopping_cart.click()

    def click_button_sort_by(self, sort_type: str):
        self.page.select_option(self.sort_container, sort_type)

    def get_prices_items(self):
        return [
            float(price.replace("$", ""))
            for price in self.prices_elements.all_text_contents()
        ]

    def get_cart_count(self):
        cart_count_text = self.cart_items.text_content()
        return int(cart_count_text) if cart_count_text else 0

    def get_total_item_count(self):
        return len(self.total_item.all())

    def get_total_items(self):
        total_items = self.total_item.all()
        item_names = [item.inner_text() for item in total_items]
        return item_names
