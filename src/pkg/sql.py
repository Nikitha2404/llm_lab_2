import sqlite3
import pandas as pd

def dbInit():
    conn = sqlite3.connect("/Users/nikitha.hebbar/Downloads/olist.sqlite")
    return conn

def execute_query(query):
    try:
        for keyword in ["DROP", "DELETE", "ALTER", "UPDATE"]:
            if keyword in query.upper():
                return"⚠️ Potentially destructive SQL detected!"
        conn = dbInit()
        df = pd.read_sql_query(query, conn)
        conn.close()
        result = parse_dataframe(df)
        return result
    except sqlite3.Error as e:
        raise ValueError(e)

def parse_dataframe(df):
    if df.empty or df.shape[1] == 0:
        return set()
    return set(df.iloc[:, 0].astype(str))
