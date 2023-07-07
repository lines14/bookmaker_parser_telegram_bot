from main.elements.base_element import BaseElement

class Label(BaseElement):
    def __init__(self, locator, name):
        super().__init__(locator, name)