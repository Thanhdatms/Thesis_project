from services import LLM_connector
from azure.search.documents.models import VectorizedQuery
import re
import os
import random

class QuestionRetriever:
    def get_related_question(question):
        results = {}
        search_client = LLM_connector.AzureAISearchQuestionConnection.get_instance()
        vector_question = LLM_connector.to_vector(question)
        
        related_questions = search_client.search(
            None, top=1, vector_queries=[VectorizedQuery(vector=vector_question, fields="QuestionVector")]
        )

        for question_dict in related_questions:
            question_text = question_dict.get("question")
            query_text = question_dict.get("sql")
            
            if question_text and query_text:
                results[question_text] = query_text

        return results
    
class SchemaRetriever:
    def get_related_schemas(question):
        results = {}
        search_client = LLM_connector.AzureAISearchSchemaConnection.get_instance()
        vector_question = LLM_connector.to_vector(question)

        related_table = search_client.search(
            None, top=4, vector_queries=[VectorizedQuery(vector=vector_question, fields="DescriptionVector")]
        )

        for table in related_table:
            table_name = table.get("schema_name")
            table_info = table.get("schema_info")
            print(table_name)
            if table_name and table_info:
                results[table_name] = table_info

        return results
    