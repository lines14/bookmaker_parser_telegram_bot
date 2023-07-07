import locale
locale.setlocale(locale.LC_TIME, 'ru_RU.UTF-8')
from rutimeparser import parse
from main.base_form import BaseForm
from main.elements.base_element_children.label import Label

class CommandsPair(BaseForm):
    def __init__(self):
        super().__init__('//div[contains(@class, "tab--") and contains(text(), "1-й")]', 'match page')
        self.rates_rows = Label('//div[contains(@class, "row-common--")]', 'rates rows')
        self.date = Label('//span[contains(@class, "ev-line-time__day--")]', 'date')
        self.time = Label('//span[contains(@class, "ev-line-time__time--")]', 'time')

    def get_date_time_rates(self):
        rates_list = self.rates_rows.parse_elements_for_text()
        rates_list.reverse()
        summary_list = rates_list.pop().split('\n')
        summary_list.append(parse(self.date.get_text()).strftime('%d %B'))
        summary_list.append(self.time.get_text())
        
        return summary_list