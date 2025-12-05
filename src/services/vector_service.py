import re

import asyncpg
from fastapi import FastAPI
from services import LLM_connector
from azure.search.documents.models import VectorizedQuery

from services.database import Database


class QuestionRetriever:
    @staticmethod
    def get_related_question(question):
        results = {}
        search_client = LLM_connector.AzureAISearchQuestionConnection.get_instance()
        vector_question = LLM_connector.to_vector(question)
        
        related_questions = search_client.search(
            None, top=1, vector_queries=[VectorizedQuery(vector=vector_question, fields="question_vector")]
        )
        
        for question_dict in related_questions:
            question_text = question_dict.get("question")
            query_text = question_dict.get("sql")
            
            if question_text and query_text:
                results[question_text] = query_text

        return results
    
class SchemaRetriever:
    @staticmethod
    def get_related_schemas(question):
        results = {}
        search_client = LLM_connector.AzureAISearchSchemaConnection.get_instance()
        vector_question = LLM_connector.to_vector(question)

        related_table = search_client.search(
            None, top=4, vector_queries=[VectorizedQuery(vector=vector_question, fields="description_vector")]
        )

        for table in related_table:
            table_name = table.get("schema_name")
            table_info = table.get("schema_info")

            if table_name and table_info:
                results[table_name] = table_info

        return results
    
    
class SQLHandler:
    @staticmethod
    def extract_sql_response(text):
        """
        Extracts the longest SQL SELECT statement from the provided text.
        Args:
            text (str): The text containing SQL statements. 
            
            Returns:
            str: The longest SQL SELECT statement found in the text.
        """
        select_statements = re.findall(r'\bselect\b.*?(?:;|\Z)', text, flags=re.IGNORECASE | re.DOTALL)
        
        cleaned_statements = [re.sub(r'\s+', ' ', stmt.replace('\n', ' ')).strip() for stmt in select_statements]
        
        longest_statement = max(cleaned_statements, key=len) if cleaned_statements else None
        
        if longest_statement and not longest_statement.endswith(';'):
            longest_statement += ';'
        
        return longest_statement
    
    @staticmethod
    async def execute_query(query: str):
        """
        Executes SQL asynchronously using the FastAPI app's connection pool.
        """
        result = await Database.fetch(query)
        if isinstance(result, list):
            return [dict(r) for r in result]
        elif result is not None:
            return dict(result)
        return None