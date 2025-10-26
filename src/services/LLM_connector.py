from openai import OpenAI
import os
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient

client = OpenAI()

def to_vector(text: str) -> list[float]:
    """
    Input:
        text: str

    Output:
        vector: list of floats
    """
    # Implementation to get vector from OpenAI
    model = "text-embedding-ada-002"
    response = client.embeddings.create(
        input=text,
        model=model
    )
    vector = response['data'][0]['embedding']
    return vector

def get_openai_response(prompt: str) -> str:
    """
    Input:
        prompt: str

    Output:
        response: str
    """
    model = "gpt-3.5-turbo"
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    return response['choices'][0]['message']['content']

def get_sql_response(prompt: str) -> str:
    """
    Input:
        prompt: str

    Output:
        response: str
    """
    model = "gpt-4o"
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    return response['choices'][0]['message']['content']

class AzureAISearchQuestionConnection:
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            from azure.search.documents import SearchClient
            endpoint = os.getenv("AZURE_SEARCH_QUESTION_ENDPOINT")
            index_name = os.getenv("AZURE_SEARCH_QUESTION_INDEX_NAME")
            api_key = os.getenv("AZURE_SEARCH_QUESTION_API_KEY")

            cls._instance = SearchClient(
                endpoint=endpoint,
                index_name=index_name,
                credential=api_key
            )
        return cls._instance   

class AzureAISearchSchemaConnection:
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            from azure.search.documents import SearchClient
            endpoint = os.getenv("AZURE_SEARCH_SCHEMA_ENDPOINT")
            index_name = os.getenv("AZURE_SEARCH_SCHEMA_INDEX_NAME")
            api_key = os.getenv("AZURE_SEARCH_SCHEMA_API_KEY")

            cls._instance = SearchClient(
                endpoint=endpoint,
                index_name=index_name,
                credential=api_key
            )
        return cls._instance