from src.utils.azure_client import azure_openai_model,client
from src.utils.llm_stats import LLMStats
from pydantic import BaseModel,Field
import logging

llmstats = LLMStats(model_name=azure_openai_model)

class SQLGenerationReasoning(BaseModel):
    steps: list[str] = Field(...,description="Short chain of thought reasoning explaining the logic in 3-4 steps")
    final_answer: str = Field(...,description="the final SQL query to answer the user request")

class QueryProcessor(BaseModel):
    original_question: str = Field(..., description="The original user query")
    expanded_question: str = Field(..., description="The final SQL query based on all expansions")

system_query = None
def get_system_query():
    # singleton
    global system_query
    if system_query is None:  
        with open('/Users/nikitha.hebbar/Documents/llm_lab_week2/prompts/system.txt', 'r', encoding='utf-8') as file:
            system_query = file.read()
    return system_query

messages =[
    {"role":"system","content":get_system_query()}
]

def expand_query_llm(question: str) -> str:
    expansion_prompt = """
    You are an expert SQL assistant. Your task is to refine user queries by:
    - Expanding broad terms like "cheap" into specific price ranges.
    - Translating English product categories into Portuguese equivalents. 
    - Available Portuguese categories: beleza_saude, eletronicos, telefonia, utilidades_domesticas, moveis_decoracao.
    - Adding structured conditions (e.g., "good reviews" → "review_score > 4.0").
    - Keeping the core intent of the question unchanged.
    - Dont provide an SQL statement and if the question does not need expansion return the original question back

    Example:
    User: "I want cheap electronics and kitchen items with good reviews"
    Expanded Query: "I want eletrônicos where price < 50 BRL and review_score > 4.0"

    """

    messages = [
        {"role": "system", "content": expansion_prompt},
        {"role": "user", "content": question},
    ]

    try:
        response = client.beta.chat.completions.parse(
            model=azure_openai_model,
            messages=messages,
            response_format=QueryProcessor
        )
        llmstats.record_usage(question,response.usage)
        model = response.choices[0].message.parsed
        logging.info("Query Expansion result:")
        logging.info(f"original question: {model.original_question}")
        logging.info(f"expanded question: {model.expanded_question}")
        return model.expanded_question
    except Exception as e:
        logging.error(f"Query expansion failed: {e}")
    return question  

def trim_messages(messages: list[dict]):
    system_message = messages[0] # system promt
    chat_history = [m for m in messages if m["role"] in {"user", "assistant"}][-6:]  # Keep last 3 user-assistant pairs

    return [system_message] + chat_history

def build_chat_history(answer: str | None):
    global messages
    if answer != None:
        answer_dict = {"role":"assistant","content":answer}
    messages.append(answer_dict)
    #messages = trim_messages(messages=messages)
    return messages

def build_messages(question: str|None):
    global messages
    if question!=None:
        question_dict={"role":"user","content":question}
    messages.append(question_dict)
    return messages

def get_query_azure_openai(question):
    global messages
    try:
        question = expand_query_llm(question=question)
        messages=build_messages(question)
        logging.info(messages)
        logging.info(question)
        completion = client.beta.chat.completions.parse(
            model=azure_openai_model,
            messages=messages,
            response_format=SQLGenerationReasoning
        )
        llmstats.record_usage(question, completion.usage)
        answer=evaluate_model(completion.choices[0].message.parsed)
        messages=build_chat_history(answer)
        return answer
    except Exception as e:
        raise ConnectionError(e)

def evaluate_model(model:SQLGenerationReasoning):
    logging.info("Steps invloved:")
    for step in model.steps:
        logging.info(step)
    return model.final_answer

def fix_failed_query(question,sql_query,error):
    """Evaluate the generated SQL against the correct SQL using an LLM"""
    eval_prompt = f"""
    As a SQL expert, evaluate the generated SQL query with respect to the error provided
    
    Query task: {question}
    
    Generated SQL: {sql_query}

    error received: {error}
    
    Provide a right SQL statement resolving the error that its throwing
    """
    response = client.beta.chat.completions.parse(
        model=azure_openai_model,
        messages=[{"role": "system", "content": get_system_query()},
                 {"role": "user", "content": eval_prompt}],
        response_format=SQLGenerationReasoning
    )
    llmstats.record_usage(question,response.usage)
    answer=evaluate_model(response.choices[0].message.parsed)
    return answer