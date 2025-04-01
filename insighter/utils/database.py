import sqlite3
import os
from pathlib import Path

def get_db_connection(db_path=None):

    if db_path is None:

        from insighter.config.settings import DATABASE_PATH
        db_path = DATABASE_PATH
    
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def execute_query(query, params=(), db_path=None, fetch_all=True):

    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    cursor.execute(query, params)
    
    if query.strip().upper().startswith(("SELECT", "PRAGMA")):

        if fetch_all:
            results = cursor.fetchall()

        else:
            results = cursor.fetchone()
            
    else:
        conn.commit()
        results = {"affected_rows": cursor.rowcount}
    
    conn.close()
    return results 