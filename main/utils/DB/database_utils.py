import sqlite3 as sq
from pathlib import Path
destination = Path(__file__).resolve().parent.parent.parent.parent

class DatabaseUtils:
    @staticmethod
    def sql_start():
        global base, cur
        base = sq.connect(f'{destination}/resources/database.db')
        cur = base.cursor()
        if base:
            print('[ОК] - База данных подключена!')
        base.execute("CREATE TABLE IF NOT EXISTS names_mapping(original_name TEXT PRIMARY KEY, short_name TEXT)")
        base.commit()

    def sql_add_original_name(name):
        cur.execute("INSERT OR REPLACE INTO names_mapping (original_name) VALUES (?)", (name,))
        base.commit()     