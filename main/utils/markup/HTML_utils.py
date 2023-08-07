from pathlib import Path
from html2image import Html2Image
from resources.HTML_bank import HTMLBank
destination = Path(__file__).resolve().parent.parent.parent.parent

class HTMLUtils:
    @staticmethod
    def generate_HTML(competition_type, tournament_name, models_list):
        with open(f'{destination}/index.html', 'w', encoding='utf-8') as data:
            data.write(HTMLBank.get_HTML_from_template(competition_type, tournament_name, models_list))

    def HTML_to_jpg(size):
        hti = Html2Image(output_path=destination, size=tuple(size))
        hti.screenshot(url=f'{destination}/index.html', save_as='index.jpg')