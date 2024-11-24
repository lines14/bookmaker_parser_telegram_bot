import sqlite3 as sq
from pathlib import Path
from bot.config import DB_PATH
path = Path(__file__).resolve().parent.parent.parent.parent

class DatabaseUtils:
    @staticmethod
    def sql_start():
        global base, cur
        base = sq.connect(f'{path}{DB_PATH}')
        cur = base.cursor()
        if base:
            print('[ОК] - База данных подключена!')
        base.execute("CREATE TABLE IF NOT EXISTS names_mapping(original_name TEXT PRIMARY KEY, short_name TEXT);")
        base.commit()

    @staticmethod
    def sql_add_original_name(name):
        cur.execute("INSERT INTO names_mapping (original_name) VALUES (?);", (name,))
        base.commit()

    @staticmethod
    def sql_check_original_name(name):
        return cur.execute("SELECT EXISTS(SELECT 1 FROM names_mapping WHERE original_name = (?));", (name,)).fetchall()
    
    @staticmethod
    def sql_get_short_name(name):
        return cur.execute("SELECT short_name FROM names_mapping WHERE original_name = (?);", (name,)).fetchall()
    
    @staticmethod
    def sql_add_short_name(original_name, short_name):
        cur.execute("UPDATE names_mapping SET short_name = (?) WHERE original_name = (?);", (short_name, original_name))
        base.commit()