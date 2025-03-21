from src.utils.azure_client import azure_openai_model,client
from src.utils.llm_stats import LLMStats
from pydantic import BaseModel,Field
import logging
from typing import Optional

llmstats = LLMStats(model_name=azure_openai_model)

class Steps(BaseModel):
    step1: str = Field(...,description="Identify the tables and join them based on their foreign keys")
    step2: str = Field(...,description="Apply filters and conditions given in the question")
    step3: Optional[str] = Field(..., description="Sort, group, or finalize the output if needed")
    step4: Optional[str] = Field(..., description="Use LIMIT 1 for questions asking about a single most or top item.")

class SQLGenerationReasoning(BaseModel):
    steps: Steps = Field(...,description="Short chain of thought reasoning explaining the logic")
    final_answer: str = Field(...,description="the final SQL query to answer the user request")

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

def trim_messages(messages: list[dict]):
    system_message = messages[0] # system promt
    chat_history = [m for m in messages if m["role"] in {"user", "assistant"}][-6:]  # Keep last 3 user-assistant pairs

    return [system_message] + chat_history

def build_chain_of_thought_messages(answer: str | None):
    global messages
    if answer != None:
        answer_dict = {"role":"assistant","content":answer}
    messages.append(answer_dict)
    messages = trim_messages(messages=messages)
    return messages

def build_messages(question: str|None):
    global messages
    if question!=None:
        question_dict={"role":"user","content":question}
    messages.append(question_dict)
    return messages

def get_query_azure_openai(question):
    global messages
    messages=build_messages(question)
    try:
        logging.info(messages)
        logging.info(question)
        completion = client.beta.chat.completions.parse(
            model=azure_openai_model,
            messages=messages,
            response_format=SQLGenerationReasoning
        )
        llmstats.record_usage(question, completion.usage)
        answer=evaluate_model(completion.choices[0].message.parsed)
        messages=build_chain_of_thought_messages(answer)
        return answer
    except Exception as e:
        raise ConnectionError(e)

def evaluate_model(model:SQLGenerationReasoning):
    logging.info("Steps invloved:")
    logging.info(f"Step 1: {model.steps.step1}")
    logging.info(f"Step 2: {model.steps.step2}")
    if model.steps.step3:
        logging.info(f"Step 3: {model.steps.step3}")
    if model.steps.step4:
        logging.info(f"Step 4: {model.steps.step4}")
    return model.final_answer