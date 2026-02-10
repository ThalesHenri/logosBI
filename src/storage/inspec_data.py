import sqlite3
from config import DB_PATH

class InspectData:
    def __init__(self):
        self.conn = None
        self.cursor = None
    
    def connect(self):
        self.conn = sqlite3.connect(DB_PATH)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
    
    def close(self):
        self.conn.close()
    
    def _row_to_dict(self, row):
        return dict(row)
    
    def inpsect_db(self):
        print("\n📦 Tabelas no banco:")
        self.cursor.execute("""
        SELECT name FROM sqlite_master
        WHERE type='table'
        ORDER BY name;
        """)

        tables = self.cursor.fetchall()
        for table in tables:
            print(f" - {table[0]}")

        for table, in tables:
            print(f"\n📊 Estrutura da tabela: {table}")
            self.cursor.execute(f"PRAGMA table_info({table});")
            for col in self.cursor.fetchall():
                print(self._row_to_dict(col))

        print(f"\n🧾 Primeiros registros de {table}:")
        self.cursor.execute(f"SELECT * FROM {table} LIMIT 5;")
        rows = self.cursor.fetchall()
        for row in rows:
            print(self._row_to_dict(row))

