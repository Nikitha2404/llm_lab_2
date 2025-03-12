import sys
import os

sys.path.append(os.path.abspath(os.path.dirname(__file__) + "/.."))
from pydantic import BaseModel,Field
from azure_client import client,azure_openai_model

class SQLGenerationReasoning(BaseModel):
    steps: list[str] = Field(...,description="Short chain of thought reasoning explaining the logic")
    final_answer: str = Field(...,description="the final SQL query to answer the user request")

def getQueryOpenAI(question):
    try:
        with open('/Users/nikitha.hebbar/Documents/llm_lab_week2/prompts/system.txt', 'r', encoding='utf-8') as file:
            systemQuery = file.read() 
        completion = client.beta.chat.completions.parse(
            model=azure_openai_model,
            messages=[
                {'role':'system', 'content':systemQuery},
                {'role':'user', 'content':question}
            ],
            response_format=SQLGenerationReasoning
        )
        return completion.choices[0].message.parsed
    except Exception as e:
        raise ConnectionError(e)

question1 = "Which seller has delivered the most orders to customers in Rio de Janeiro? [string: seller_id]"
print(getQueryOpenAI(question1))