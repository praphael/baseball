from enum import Enum

class DB(Enum):
    sqlite = 1
    postgres = 2

supportedDBs = { "sqlite" : DB.sqlite, "postgres" : DB.postgres }

def getConnection(db):
    if db == DB.sqlite:
        import sqlite3
        conn = sqlite3.connect("..\\baseball.db")
    elif db == DB.postgres:
        import psycopg
        conn = psycopg.connect("host=127.0.0.1 port=5432 dbname=postgres user=postgres")
    else:
        raise Exception(f"unsupported database '{db}'")
    
    return conn

def executeQuery(db, qy, params):
    conn = getConnection(db)

    # Open a cursor to perform database operations
    cur = conn.cursor()
    cur.execute(qy, params)
    return cur.fetchall()
