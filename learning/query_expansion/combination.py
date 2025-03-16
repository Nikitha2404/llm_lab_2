import sys
import os
from typing import Dict
sys.path.append(os.path.abspath(os.path.dirname(__file__) + "/.."))
from pydantic import BaseModel,Field
from src.utils.azure_client import client,azure_openai_model

class QueryProcessor(BaseModel):
    original_query: str = Field(..., description="The original user query")
    extracted_terms: Dict[str, str] = Field(..., description="Key terms extracted from the query with their type (category, price, condition, etc.)")
    expanded_categories: list[str] = Field(..., description="Expanded category terms in Portuguese")
    generated_sql: str = Field(..., description="The final SQL query based on all expansions")
    
user_query = "I want cheap electronics and kitchen items with good reviews"

response = client.beta.chat.completions.parse(
    model=azure_openai_model,
    messages=[
        {"role": "system", "content": "You process e-commerce queries for the Olist database. Available Portuguese categories: beleza_saude, eletronicos, telefonia, utilidades_domesticas, moveis_decoracao.Database columns: product_id, product_category_name, price, review_score.Extract key terms, map to Portuguese categories, and generate SQL."},
        {"role": "user", "content": user_query}
    ],
    response_format=QueryProcessor,
)

result = response.choices[0].message.parsed

print(f"Original query: {result.original_query}")
print(f"Extracted terms: {result.extracted_terms}")
print(f"Expanded categories: {result.expanded_categories}")
print("\nGenerated SQL:")
print(result.generated_sql)