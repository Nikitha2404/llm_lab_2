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
        messages = [
            {"role": "system", "content": f"{systemQuery}"},
            {"role": "user", "content": "Which seller has delivered the most orders to customers in Rio de Janeiro?"}, 
            {"role": "assistant", "content": "SELECT s.seller_id, COUNT(*) AS order_count FROM orders o JOIN customers c ON o.customer_id = c.customer_id JOIN sellers s ON o.seller_id = s.seller_id WHERE c.customer_city = 'rio de janeiro' AND o.order_status = 'delivered' GROUP BY s.seller_id ORDER BY order_count DESC LIMIT 1;"},
            {"role": "user", "content": "What's the average review score for 'beleza_saude' products?"},
            {"role": "assistant", "content": "SELECT AVG(r.review_score) AS avg_score FROM order_reviews r JOIN order_items oi ON r.order_id = oi.order_id JOIN products p ON oi.product_id = p.product_id WHERE p.product_category_name = 'beleza_saude';"},
            {"role": "user", "content": f"{question}"}
        ]
        completion = client.beta.chat.completions.parse(
            model=azure_openai_model,
            messages=messages,
            response_format=SQLGenerationReasoning
        )
        return completion.choices[0].message.parsed
    except Exception as e:
        raise ConnectionError(e)

question4 = "Which product category has the highest rate of 5-star reviews? [string: category_name]"
print(getQueryOpenAI(question4))