from openai import AzureOpenAI
import sqlite3
import logging
from tabulate import tabulate
from dotenv import load_dotenv
import re
import os

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
azure_openai_model = os.getenv("AZURE_OPENAI_DEPLOYMENT")
client = AzureOpenAI(
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("OPENAI_API_KEY"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION")
)


def dbInit():
    conn = sqlite3.connect("/Users/nikitha.hebbar/Downloads/olist.sqlite")
    return conn

def formatQueryResult(cursor, result):
    column_names = [desc[0] for desc in cursor.description]  
    formatted_result = tabulate(result, headers=column_names, tablefmt="grid") 
    return formatted_result

def isQuerySafe(sqlQuery):
    harmful_patterns = [
        r"\bDROP\s+TABLE\b",  # DROP TABLE command
        r"\bDELETE\s+FROM\b(?!.*\bWHERE\b)",  # DELETE without WHERE
        r"\bTRUNCATE\b",  # Truncate command
        r"\bALTER\s+TABLE\b",  # Alter table command
        r"\bSELECT\s+\*\s+FROM\b(?!.*\bLIMIT\b)",  # SELECT * without LIMIT
        r"\bINSERT\s+INTO\b.*\bVALUES\s*\(.*SELECT\b",  # INSERT using SELECT
    ]

    for pattern in harmful_patterns:
        if re.search(pattern, sqlQuery, re.IGNORECASE):
            print("query is unsafe")
            return False  
    return True

def executeQuery(query):
    try:
        conn = dbInit()
        cursor = conn.cursor()
        cursor.execute(query)
        results = cursor.fetchall()
        formattedResults = formatQueryResult(cursor, results)
        conn.close()
        logging.info(f"query result: {results}")
        return formattedResults
    except sqlite3.Error as e:
        logging.error(f"Database error: {e}")
        return None

def getQueryOpenAI(question):
    try:
        with open('prompts/system.txt', 'r', encoding='utf-8') as file:
            systemQuery = file.read() 
        completion = client.chat.completions.create(
            model=azure_openai_model,
            messages=[
                {'role':'system', 'content':systemQuery},
                {'role':'user', 'content':question}
            ],
            temperature=1,
            max_completion_tokens=1024,
            top_p=1,
            stream=False,
            stop=None,
        )
        return completion.choices[0].message.content
    except Exception as e:
        raise ConnectionError(e)

def getResponseOpenAI(question,data):
    try:
        with open('prompts/response.txt', 'r', encoding='utf-8') as file:
            responsePrompt = file.read() 
        userPrompt = "###Question\n" + question + "###Data\n" + data
        completion = client.chat.completions.create(
            model=azure_openai_model,
            messages=[
                {'role':'system','content':responsePrompt},
                {'role':'user','content':userPrompt}
            ],
            temperature=1,
            max_completion_tokens=1024,
            top_p=1,
            stream=False,
            stop=None,
        )
        return completion.choices[0].message.content
    except Exception as e:
        raise ConnectionError(e)