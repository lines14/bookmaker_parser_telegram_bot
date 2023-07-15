from datetime import datetime
from main.utils.data.config_manager import ConfigManager
time_list = []
log_list = []

class Logger:
    @staticmethod
    def log(step):
        if (ConfigManager.get_config_data().is_logger):
            print(step)
        log_list.append(f' {step}\n')
        time_list.append(f'{datetime.now()}')

    @staticmethod
    def log_to_file():
        summary_list = list(zip(time_list, log_list))
        with open('../../../test/log.txt', 'w', encoding='utf-8') as data:
            data.write(summary_list)

    @staticmethod
    def get_timings():
        return [*time_list]