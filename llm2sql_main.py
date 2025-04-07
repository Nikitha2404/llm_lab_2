from src.utils.logging import setup_logging
from src.pkg.sql import execute_query
from src.pkg.llm2sql_query import get_query_azure_openai,llmstats,fix_failed_query

if __name__ == "__main__":
    questions = [
        "Which seller has delivered the most orders to customers in rio de janeiro? [string: seller_id]",
        "What's the average review score for products in the 'beleza_saude' category? [float: score]",
        # "How many sellers have completed orders worth more than 100,000 BRL in total? [integer: count]",
        # "Which product category has the highest rate of 5-star reviews? [string: category_name]",
        # "What's the most common payment installment count for orders over 1000 BRL? [integer: installments]",
        # "Which city has the highest average freight value per order? [string: city_name]",
        # "What's the most expensive product category based on average price? [string: category_name]",
        # "Which product category has the shortest average delivery time? [string: category_name]",
        # "How many orders have items from multiple sellers? [integer: count]",
        # "What percentage of orders are delivered before the estimated delivery date? [float: percentage]",
        # "I want cheap electronics and kitchen items with good reviews",
    ]
    setup_logging(output_dir="/Users/nikitha.hebbar/Documents/llm_lab_week2")
    for question in questions:
        sql_query = get_query_azure_openai(question)
        if sql_query:
            print(sql_query)
            try:
                query_result= execute_query(sql_query)
                if not isinstance(query_result, set):
                    print("Query execution failed: ", query_result)
            except ValueError as e:
                sql_query= fix_failed_query(question,sql_query,str(e))
                print(sql_query)
                query_result= execute_query(sql_query)
            print("\nQuery Result: ",query_result)
        print("-----------------------------------------------------------------\n")
    llmstats.log_summary()