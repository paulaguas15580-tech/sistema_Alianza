import psycopg2
from psycopg2 import pool, OperationalError
import psycopg2.extras
import sqlite3
import os

class CursorProxy:
    """Proxy para el cursor que normaliza consultas entre PostgreSQL y SQLite"""
    def __init__(self, cursor, mode):
        self.cursor = cursor
        self.mode = mode
    def execute(self, query, params=None):
        if self.mode == "SQLITE":
            query = query.replace("%s", "?")
        if params is not None:
            return self.cursor.execute(query, params)
        return self.cursor.execute(query)
    def __getattr__(self, name):
        return getattr(self.cursor, name)
    def __iter__(self):
        return iter(self.cursor)

class DatabaseManager:
    """
    Clase centralizada para la gestión de conexiones PostgreSQL con Pooling.
    Incluye fallback automático a SQLite si el servidor no está disponible.
    """
    def __init__(self, host, database, user, password, port="5432", min_conn=1, max_conn=20):
        self.config = {
            "host": host,
            "database": database,
            "user": user,
            "password": password,
            "port": port
        }
        self.connection_pool = None
        self.mode = "POSTGRES"
        self.db_local = "Alianza_Backup_Local.db"
        self._initialize_pool(min_conn, max_conn)

    def _initialize_pool(self, min_conn, max_conn):
        try:
            self.connection_pool = pool.ThreadedConnectionPool(
                min_conn, max_conn, **self.config
            )
            print("PostgreSQL Connection Pool inicializado correctamente.")
        except (OperationalError, Exception) as e:
            print(f"PostgreSQL no disponible ({e}). Activando modo LOCAL (SQLite).")
            self.mode = "SQLITE"

    def get_connection(self):
        """Obtiene una conexión."""
        if self.mode == "SQLITE":
            conn = sqlite3.connect(self.db_local)
            conn.row_factory = sqlite3.Row
            return conn
        
        if not self.connection_pool:
            raise ConnectionError("No hay conexión con el servidor y el pool no está inicializado.")
        return self.connection_pool.getconn()

    def get_cursor(self, conn):
        """Retorna un cursor normalizado (CursorProxy)."""
        if self.mode == "SQLITE":
            return CursorProxy(conn.cursor(), "SQLITE")
        return CursorProxy(conn.cursor(cursor_factory=psycopg2.extras.DictCursor), "POSTGRES")

    def release_connection(self, conn):
        """Libera o cierra una conexión."""
        if self.mode == "SQLITE":
            conn.close()
            return
            
        if self.connection_pool:
            self.connection_pool.putconn(conn)

    def sql_type(self, type_str):
        """Normaliza tipos de datos según el motor activo."""
        if self.mode == "SQLITE":
            if "SERIAL PRIMARY KEY" in type_str:
                return type_str.replace("SERIAL PRIMARY KEY", "INTEGER PRIMARY KEY AUTOINCREMENT")
        return type_str

    def get_column_names(self, cursor, table_name):
        """Retorna lista de nombres de columnas."""
        if self.mode == "SQLITE":
            cursor.execute(f"PRAGMA table_info({table_name})")
            return [info[1] for info in cursor.fetchall()]
        else:
            cursor.execute(f"SELECT column_name FROM information_schema.columns WHERE table_name = '{table_name.lower()}'")
            return [row[0] for row in cursor.fetchall()]

    def check_table_exists(self, cursor, table_name):
        """Verifica si una tabla existe."""
        if self.mode == "SQLITE":
            cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
        else:
            cursor.execute(f"SELECT table_name FROM information_schema.tables WHERE table_name = '{table_name.lower()}'")
        return cursor.fetchone() is not None

    def close_all_connections(self):
        """Cierra todas las conexiones al salir."""
        if self.mode == "POSTGRES" and self.connection_pool:
            self.connection_pool.closeall()
