import sys
import os
import json

sys.path.append(os.path.abspath(os.path.dirname(__file__) + "/.."))
from pydantic import BaseModel,Field
from src.utils.azure_client import client,azure_openai_model

class SQLGenerationReasoning(BaseModel):
    steps: list[str] = Field(...,description="Short chain of thought reasoning explaining the logic")
    final_answer: str = Field(...,description="the final SQL query to answer the user request")


# Define our structured output format
class SQLGeneration(BaseModel):
    reasoning: list[str] = Field(..., description="Short reasoning steps explaining the approach")
    sql_query: str = Field(..., description="The final SQL query (PostgreSQL syntax)")

# Function to evaluate SQL quality
def evaluate_sql(generated_sql, correct_sql, query_description):
    """Evaluate the generated SQL against the correct SQL using an LLM"""
    eval_prompt = f"""
    As a SQL expert, evaluate the generated SQL query against the correct SQL query.
    
    Query task: {query_description}
    
    Generated SQL: {generated_sql}
    
    Correct SQL: {correct_sql}
    
    Provide a JSON response with the following fields:
    - "is_correct": boolean (true if functionally equivalent, false otherwise)
    - "errors": list of string errors if any (empty list if correct)
    - "correction": string with corrected SQL if needed (empty string if correct)
    - "explanation": string explaining what was wrong and how it was fixed
    """
    
    response = client.chat.completions.create(
        model=azure_openai_model,
        messages=[{"role": "system", "content": "You are a SQL expert evaluator."},
                 {"role": "user", "content": eval_prompt}],
        response_format={"type": "json_object"}
    )
    
    result = json.loads(response.choices[0].message.content)
    return result

# Maintaining a growing conversation with feedback
def build_conversation_with_feedback(test_queries, correct_sql_map, system_prompt):
    """Build a conversation history with automatic feedback for improvement"""
    
    conversation = [{"role": "system", "content": system_prompt}]
    
    for query_desc, query in test_queries.items():
        # Add the user question
        conversation.append({"role": "user", "content": query})
        
        # Get model response
        response = client.beta.chat.completions.parse(
            model=azure_openai_model,
            messages=conversation,
            response_format=SQLGeneration
        )
        
        generated_sql = response.choices[0].message.parsed.sql_query
        correct_sql = correct_sql_map[query_desc]
        
        # Evaluate the SQL
        evaluation = evaluate_sql(generated_sql, correct_sql, query_desc)
        
        # Add model's response to history
        conversation.append({
            "role": "assistant", 
            "content": generated_sql
        })
        
        # If SQL was incorrect, add feedback to improve future responses
        if not evaluation["is_correct"]:
            feedback = f"""
            Your SQL query has some issues:
            {evaluation["explanation"]}
            
            Corrected SQL:
            {evaluation["correction"]}
            """
            
            conversation.append({"role": "user", "content": feedback})
            conversation.append({"role": "assistant", "content": evaluation["correction"]})
    return conversation

def getQueryOpenAI(question,systemQuery):
    try:
        messages = [
            {"role": "system", "content": f"{systemQuery}"},
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

question = "Which product category has the highest rate of 5-star reviews? [string: category_name]"
correct_sql_map = {
    "Which product category has the highest rate of 5-star reviews? [string: category_name]":"SELECT p.product_category_name FROM products p \
                                                                                            JOIN order_items oi ON p.product_id = oi.product_id \
                                                                                            JOIN order_reviews r ON oi.order_id = r.order_id \
                                                                                            GROUP BY p.product_category_name \
                                                                                            HAVING COUNT(*) > 100 \
                                                                                            ORDER BY (COUNT(CASE WHEN r.review_score = 5 THEN 1 END) * 100.0 / COUNT(*)) DESC \
                                                                                            LIMIT 1;",
}
with open('/Users/nikitha.hebbar/Documents/llm_lab_week2/prompts/system.txt', 'r', encoding='utf-8') as file:
    systemQuery = file.read() 
sql_model = getQueryOpenAI(question,systemQuery)
test_queries = {
    question:sql_model.final_answer
}
print(build_conversation_with_feedback(test_queries,correct_sql_map,systemQuery)[-1])