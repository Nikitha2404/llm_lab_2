from functions import getQueryOpenAI,getResponseOpenAI,isQuerySafe,logging,executeQuery

def cleanSqlQuery(sqlQuery:str):
    formattedSqlQuery = sqlQuery.replace("```sql\n","")
    formattedSqlQuery = formattedSqlQuery.replace("\n```","")
    formattedSqlQuery = formattedSqlQuery.replace("\n"," ")
    return formattedSqlQuery

def executeLLM2SQL(question):
    try:
        sqlQuery = getQueryOpenAI(question)
        if sqlQuery:
            formattedSqlQuery = cleanSqlQuery(sqlQuery)
            if isQuerySafe(formattedSqlQuery):
                logging.info(f"sql query generated: {formattedSqlQuery}")
                result = executeQuery(formattedSqlQuery)
                try:
                    response = getResponseOpenAI(question=question, data=result)
                    if response:
                        return response
                except Exception as e:
                    logging.error(f"error: {e}")
                    return None
            else:
                return None
    except Exception as e:
        logging.error(f"error: {e}")
        return None
        
# question1 = "Which seller has delivered the most orders to customers in Rio de Janeiro? [string: seller_id]"
# print(executeLLM2SQL(question1))
# print("---------------------------------------------------------------------------------------------------------\n")
# question2 = "What's the average review score for products in the 'beleza_saude' category? [float: score]"
# print(executeLLM2SQL(question2))
# print("---------------------------------------------------------------------------------------------------------\n")
# question3 = "How many sellers have completed orders worth more than 100,000 BRL in total? [integer: count]"
# print(executeLLM2SQL(question3)) # giving wrong
# print("---------------------------------------------------------------------------------------------------------\n")
# question4 = "Which product category has the highest rate of 5-star reviews? [string: category_name]"
# print(executeLLM2SQL(question4))
# print("---------------------------------------------------------------------------------------------------------\n")
# question5 = "What's the most common payment installment count for orders over 1000 BRL? [integer: installments]"
# print(executeLLM2SQL(question5))
# print("---------------------------------------------------------------------------------------------------------\n")
# question6 = "Which city has the highest average freight value per order? [string: city_name]"
# print(executeLLM2SQL(question6))
# print("---------------------------------------------------------------------------------------------------------\n")
# question7 = "What's the most expensive product category based on average price? [string: category_name]"
# print(executeLLM2SQL(question7))
# print("---------------------------------------------------------------------------------------------------------\n")
# question8 = "Which product category has the shortest average delivery time? [string: category_name]"
# print(executeLLM2SQL(question8))
# print("---------------------------------------------------------------------------------------------------------\n")
# question9 = "How many orders have items from multiple sellers? [integer: count]"
# print(executeLLM2SQL(question9)) # giving wrong
# print("---------------------------------------------------------------------------------------------------------\n")
# question10 = "What percentage of orders are delivered before the estimated delivery date? [float: percentage]"
# print(executeLLM2SQL(question10))
