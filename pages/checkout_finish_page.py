class CheckoutFinishPage:
    def __init__(self,page):
        self.page=page
        self.button_cancel = page.locator('[data-test="cancel"]')
        self.button_finish = page.locator('[data-test="finish"]')
        self.correct_finish= page.locator("h2.complete-header")
    def click_button_cancel(self):
        self.button_cancel.click()
    def click_button_finish(self):
        self.button_finish.click()
    