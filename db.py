import os
import sqlite3

DATABASE_URL = os.environ.get("DATABASE_URL", "").strip()

def get_connection():
    # Si tenemos DATABASE_URL, usamos PostgreSQL
    if DATABASE_URL:
        if DATABASE_URL.startswith("postgres://"):
            # Render a veces usa "postgres://" en vez de "postgresql://"
            DATABASE_URL_PG = DATABASE_URL.replace("postgres://", "postgresql://", 1)
        else:
            DATABASE_URL_PG = DATABASE_URL

        try:
            import psycopg2
        except ImportError:
            raise RuntimeError("psycopg2 no está instalado. Instálalo con: pip install psycopg2-binary")

        return psycopg2.connect(DATABASE_URL_PG)
    else:
        # Modo local con SQLite
        conn = sqlite3.connect("database.db")
        conn.row_factory = sqlite3.Row
        return conn


def init_db():
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS registros (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre_completo TEXT NOT NULL,
                nombre_comun TEXT NOT NULL,
                nombre_cientifico TEXT NOT NULL,
                comentario TEXT,
                imagen TEXT,
                estado TEXT DEFAULT 'pendiente'
            )
        """)
        conn.commit()