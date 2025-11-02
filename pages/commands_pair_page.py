from main.base_form import BaseForm
from main.elements.base_element_children.label import Label

class CommandsPairPage(BaseForm):
    def __init__(self):
        super().__init__('//span[contains(text(), "1-й")]', 'match page')
        self.rates_rows = Label('//div[contains(@class, "normal-row--")]', 'rates rows')
        self.date = Label('//span[contains(@class, "scoreboard-compact__main__time--")]//span[1]', 'date')
        self.time = Label('//span[contains(@class, "scoreboard-compact__main__time--")]//span[2]', 'time')
        self.logo = Label('//span[contains(@class, "team-icon--")]', 'logo')

    def get_date_time_rates(self):
        rates_list = self.rates_rows.parse_elements_for_text()
        rates_list.reverse()
        summary_list = rates_list.pop().split('\n')
        if len(summary_list) == 4:
            summary_list.insert(2, None)
            summary_list.insert(2, None)
        
        summary_list.append(self.date.get_text())
        summary_list.append(self.time.get_text())
        logo_list = self.logo.parse_elements_for_attr('style')
        for logo_link in logo_list:
            if 'background-image' in logo_link:
                summary_list.append(logo_link[25:-3])
            else:
                summary_list.append(None)

        return summary_list