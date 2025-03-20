import sqlite3
import pandas as pd

def dbInit():
    conn = sqlite3.connect("/Users/nikitha.hebbar/Downloads/olist.sqlite")
    return conn

def execute_query(query):
    try:
        conn = dbInit()
        df = pd.read_sql_query(query, conn)
        conn.close()
        result = parse_dataframe(df)
        return result
    except sqlite3.Error as e:
        raise ConnectionError(e)

def parse_dataframe(df):
    for col in df.select_dtypes(include=['object']).columns:
        df[col] = df[col].str.lower()
    return df
