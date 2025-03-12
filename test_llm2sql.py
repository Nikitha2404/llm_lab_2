import pytest
from questions import executeLLM2SQL  

# execute: pytest test_llm2sql.py -v
@pytest.mark.parametrize("question, expectedResponse", [
    ("Which seller has delivered the most orders to customers in Rio de Janeiro? [string: seller_id]",
     "4a3ca9315b744ce9f8e9374361493884"),

    ("What's the average review score for products in the 'beleza_saude' category? [float: score]",
     "4.14"),

    ("How many sellers have completed orders worth more than 100,000 BRL in total? [integer: count]",
     "17"),

    ("Which product category has the highest rate of 5-star reviews? [string: category_name]",
     "livros_interesse_geral"),

    ("What's the most common payment installment count for orders over 1000 BRL? [integer: installments]",
     "10"),

    ("Which city has the highest average freight value per order? [string: city_name]",
     "campina grande"),

    ("What's the most expensive product category based on average price? [string: category_name]",
     "pcs"),

    ("Which product category has the shortest average delivery time? [string: category_name]",
     "alimentos"),

    ("How many orders have items from multiple sellers? [integer: count]",
     "1278"),

    ("What percentage of orders are delivered before the estimated delivery date? [float: percentage]",
     "91.88"),
])

def test_execute_llm2sql(question, expectedResponse):
    """
    Test executeLLM2SQL for various predefined questions.
    """
    actualResponse = executeLLM2SQL(question)
    assert actualResponse == expectedResponse
