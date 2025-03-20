import logging
from src.utils.logging import setup_logging
from src.pkg.sql import execute_query
from src.pkg.query import get_system_query,get_query_azure_openai

questions = [
    "Which seller has delivered the most orders to customers in Rio de Janeiro? [string: seller_id]",
    "What's the average review score for products in the 'beleza_saude' category? [float: score]",
    "How many sellers have completed orders worth more than 100,000 BRL in total? [integer: count]",
    "Which product category has the highest rate of 5-star reviews? [string: category_name]",
    "What's the most common payment installment count for orders over 1000 BRL? [integer: installments]",
    "Which city has the highest average freight value per order? [string: city_name]",
    "What's the most expensive product category based on average price? [string: category_name]",
    "Which product category has the shortest average delivery time? [string: category_name]",
    "How many orders have items from multiple sellers? [integer: count]",
    "What percentage of orders are delivered before the estimated delivery date? [float: percentage]",
]

messages =[
    {"role":"system","content":get_system_query()}
]

if __name__ == "__main__":
    setup_logging(output_dir="/Users/nikitha.hebbar/Documents/llm_lab_week2")
    for question in questions:
        print("-----------------------------------------------------------------\n")
        sql_query = get_query_azure_openai(messages,question)
        logging.info(messages)
        if sql_query:
            print(sql_query)
            query_result= execute_query(sql_query)
            print("\nQuery Result: ",query_result)

