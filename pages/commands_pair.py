import re
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
        self.logo = Label('//i[contains(@class, "ev-team__logo--")]', 'logo')

    def get_date_time_rates(self):
        rates_list = self.rates_rows.parse_elements_for_text()
        rates_list.reverse()
        summary_list = rates_list.pop().split('\n')
        if summary_list == 4:
            summary_list.insert(2, None)
            summary_list.insert(2, None)
        
        summary_list.append(parse(self.date.get_text()).strftime('%d %B'))
        summary_list.append(self.time.get_text())
        logo_list = self.logo.parse_elements_for_attr('style')
        for logo_link in logo_list:
            if 'background-image' in logo_link:
                summary_list.extend(logo_link[25:-3])
            else:
                summary_list.append(None)

        print(summary_list)
        return summary_list
    








    # https://www.fonbet.kz/sports/boxing/66232/41387197/