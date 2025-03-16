import json
import sys
import os
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor

sys.path.append(os.path.abspath(os.path.dirname(__file__) + "/.."))
from src.utils.azure_client import client,azure_openai_model
from pydantic import BaseModel, Field

# SQL query generation output format
class SQLGeneration(BaseModel):
   sql_query: str = Field(..., description="The final SQL query (PostgreSQL syntax)")

# Set up telemetry
HTTPXClientInstrumentor().instrument(
   request_hook=lambda span, request: print(json.dumps(json.loads(b''.join(chunk for chunk in request.stream).decode('utf-8')), indent=2))
)

# Create client after instrumentation
messages = [
   {"role": "system", "content": "You are a SQL expert for the Olist e-commerce database."},
   {"role": "user", "content": "What's the average review score for 'beleza_saude' products?"},
   {"role": "assistant", "content": "SELECT AVG(r.review_score) AS avg_score FROM order_reviews r JOIN order_items oi ON r.order_id = oi.order_id JOIN products p ON oi.product_id = p.product_id WHERE p.product_category_name = 'beleza_saude';"},
   {"role": "user", "content": "Which product category has the highest rate of 5-star reviews?"}
]

# Generate SQL
completion = client.beta.chat.completions.parse(
   model=azure_openai_model,
   response_format=SQLGeneration,
   messages=messages
)

print(completion.choices[0].message.parsed.sql_query)