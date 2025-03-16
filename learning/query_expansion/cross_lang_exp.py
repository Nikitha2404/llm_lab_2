import sys
import os

sys.path.append(os.path.abspath(os.path.dirname(__file__) + "/.."))
from pydantic import BaseModel,Field
from src.utils.azure_client import client,azure_openai_model

class CategoryMapping(BaseModel):
    original_term: str = Field(..., description="The original English search term")
    mapped_categories: list[str] = Field(..., description="Matching Portuguese categories from the available list")
    explanation: str = Field(..., description="Brief explanation of why these categories match")

categories = ["beleza_saude", "eletronicos", "telefonia", "utilidades_domesticas", 
              "moveis_decoracao", "esporte_lazer", "informatica"]

mapping_prompt = f"""
You are a translator for e-commerce product categories between English and Portuguese.
Available Portuguese categories in the database: {', '.join(categories)}

Map the user's search term to the most appropriate Portuguese category or categories.
Only return categories from the available list.
"""

user_query = "electronics under 100 BRL"
english_category = "electronics" 
response = client.beta.chat.completions.parse(
    model=azure_openai_model,
    messages=[
        {"role": "system", "content": mapping_prompt},
        {"role": "user", "content": f"Map this English term: '{english_category}'"}
    ],
    response_format=CategoryMapping,
)

mapping = response.choices[0].message.parsed

print(f"Original term: {mapping.original_term}")
print(f"Mapped categories: {mapping.mapped_categories}")
print(f"Explanation: {mapping.explanation}")

mapped_categories = mapping.mapped_categories
price_limit = 100  # Extracted from "under 100 BRL"

# Construct the SQL with mapped categories
category_conditions = " OR ".join([f"product_category_name = '{cat}'" for cat in mapped_categories])
sql_query = f"""
SELECT * FROM products 
WHERE ({category_conditions}) AND price < {price_limit}
ORDER BY price DESC
"""

print("\nGenerated SQL:")
print(sql_query)