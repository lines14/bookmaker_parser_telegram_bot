import imgkit
from pathlib import Path
from resources.HTML_bank import HTMLBank
destination = Path(__file__).resolve().parent.parent.parent.parent

class HTMLUtils:
    @staticmethod
    def generate_HTML(models_list):
        with open(f'{destination}/index.html', 'w', encoding='utf-8') as data:
            data.write(HTMLBank.get_HTML_from_template(models_list))

    def HTML_to_jpg():
        options = {
            'enable-local-file-access': None
        }

        imgkit.from_file(f'{destination}/index.html', f'{destination}/index.jpg', options=options)