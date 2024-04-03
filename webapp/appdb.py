from enum import Enum
from datetime import datetime

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
    t1 = datetime.now()
    conn = getConnection(db)
    t2 = datetime.now()
    # Open a cursor to perform database operations
    cur = conn.cursor()
    t3 = datetime.now()
    cur.execute(qy, params)
    t4 = datetime.now()
    r = cur.fetchall()
    t5 = datetime.now()
    times = (("total", t5-t1), ("conn", t2-t1), ("curs", t3-t2))
    times += (("exec", t4-t3), ("fetch", t5-t4))
    return r,  times
