from src.utils.azure_client import azure_openai_model,client
from pydantic import BaseModel,Field
import logging

class SQLGenerationReasoning(BaseModel):
    steps: list[str] = Field(...,description="Short chain of thought reasoning explaining the logic in 3 steps")
    final_answer: str = Field(...,description="the final SQL query to answer the user request")

def get_system_query():
    with open('/Users/nikitha.hebbar/Documents/llm_lab_week2/prompts/system.txt', 'r', encoding='utf-8') as file:
        systemQuery = file.read() 
    return systemQuery

def build_chain_of_thought_messages(messages: list[dict] | None, answer: str | None):
    if answer != None:
        answer_dict = {"role":"assistant","content":answer}
    messages.append(answer_dict)
    return messages

def build_messages(messages: list[dict] | None,question: str|None):
    if question!=None:
        question_dict={"role":"user","content":question}
    messages.append(question_dict)
    return messages

def get_query_azure_openai(messages,question):
    messages=build_messages(messages,question)
    try:
        logging.info(question)
        completion = client.beta.chat.completions.parse(
            model=azure_openai_model,
            messages=messages,
            response_format=SQLGenerationReasoning
        )
        answer=evaluate_model(completion.choices[0].message.parsed)
        messages=build_chain_of_thought_messages(messages,answer)
        return answer
    except Exception as e:
        raise ConnectionError(e)

def evaluate_model(model:SQLGenerationReasoning):
    logging.info("Steps invloved:")
    for steps in model.steps:
        logging.info(steps)
    return model.final_answer