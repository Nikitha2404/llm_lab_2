import sys
import os

sys.path.append(os.path.abspath(os.path.dirname(__file__) + "/.."))
from pydantic import BaseModel,Field
from src.utils.azure_client import client,azure_openai_model

class TermExpansion(BaseModel):
    original_term: str = Field(..., description="The original search term")
    synonyms: list[str] = Field(..., description="Direct synonyms and alternative phrasings")
    related_concepts: list[str] = Field(..., description="Related concepts and terminology")
    specific_examples: list[str] = Field(..., description="Specific examples or instances of this concept")

search_term = "profitability metrics"
response = client.beta.chat.completions.parse(
    model=azure_openai_model,
    messages=[
        {"role": "system", "content": "You are a financial terminology expert. Expand the given term with related financial concepts."},
        {"role": "user", "content": f"Expand this financial term: '{search_term}'"}
    ],
    response_format=TermExpansion,
)
expansion = response.choices[0].message.parsed

print(f"Original term: {expansion.original_term}")
print(f"Synonyms: {expansion.synonyms}")
print(f"Related concepts: {expansion.related_concepts}")
print(f"Specific examples: {expansion.specific_examples}")

# Available database columns (simulated)
financial_columns = ["gross_profit_margin", "net_income", "ebitda_ratio", "return_on_equity", 
                    "profit_percentage", "revenue_growth", "operating_expenses"]

# Find matching columns across all expanded terms
all_terms = expansion.synonyms + expansion.related_concepts + expansion.specific_examples
matching_columns = []

for term in all_terms:
    for column in financial_columns:
        if any(word.lower() in column.lower() for word in term.split()):
            matching_columns.append(column)

# Remove duplicates
matching_columns = list(set(matching_columns))

print(f"\nMatching database columns: {matching_columns}")

sql_query = f"""
SELECT 
    {', '.join(matching_columns)} 
FROM financial_reports 
WHERE report_date BETWEEN '2023-01-01' AND '2023-12-31'
"""

print("\nGenerated SQL:")
print(sql_query)