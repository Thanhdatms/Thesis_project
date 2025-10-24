from Chatbot.infrastructure.llm import LLM_connector
from azure.search.documents.models import VectorizedQuery
import re
import os
import random

class QuestionRetriever:
    def get_related_question(question):
        results = {}
        search_client = LLM_connector.AzureAISearchQuestionConnection.get_instance()
        vector_question = LLM_connector.get_openai_vector(question)
        
        related_questions = search_client.search(
            None, top=1, vector_queries=[VectorizedQuery(vector=vector_question, fields="QuestionVector")]
        )

        for question_dict in related_questions:
            question_text = question_dict.get("Question")
            query_text = question_dict.get("Query")
            
            if question_text and query_text:
                results[question_text] = query_text

        return results
    
class TableRetriever:
    def get_related_table(question):
        results = {}
        search_client = LLM_connector.AzureAISearchTableConnection.get_instance()
        vector_question = LLM_connector.get_openai_vector(question)

        related_table = search_client.search(
            None, top=4, vector_queries=[VectorizedQuery(vector=vector_question, fields="DescriptionVector")]
        )

        for table in related_table:
            table_name = table.get("TableName")
            table_info = table.get("TableInfo")
            print(table_name)
            if table_name and table_info:
                results[table_name] = table_info

        return results
    
class SQLHandler:
    def extract_sql_response(text):
        select_statements = re.findall(r'\bselect\b.*?(?:;|\Z)', text, flags=re.IGNORECASE | re.DOTALL)
        
        cleaned_statements = [re.sub(r'\s+', ' ', stmt.replace('\n', ' ')).strip() for stmt in select_statements]
        
        longest_statement = max(cleaned_statements, key=len) if cleaned_statements else None
        
        if longest_statement and not longest_statement.endswith(';'):
            longest_statement += ';'
        
        return longest_statement
    
    def execute_query(query):
        conn = LLM_connector.AzureSQLConnection.get_instance()
        try:
            with conn.cursor() as cursor:
                cursor.execute(query)
                rows = cursor.fetchall()
                return rows
        except Exception as e:
            conn.rollback()
            print(f"Error executing query: {e}")
            return None
        
def convert_to_vector(text):
    return [random.randint(0, 100) for _ in range(10)]