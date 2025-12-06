import os
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from dotenv import load_dotenv
from openai import AzureOpenAI

load_dotenv()


def to_vector(text: str) -> list[float]:
    """
    Input:
        text: str

    Output:
        vector: list of floats
    """
    # Implementation to get vector from OpenAI
    
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    api_key = os.getenv("AZURE_OPENAI_API_KEY")
    api_version = os.getenv("AZURE_OPENAI_API_VERSION")

    client = AzureOpenAI(
        azure_endpoint=endpoint,
        api_key=api_key,
        api_version=api_version
    )

    model = "text-embedding-ada-002"
    response = client.embeddings.create(
        input=text,
        model=model
    )
    vector = response.data[0].embedding
    return vector

def get_openai_response(prompt: str) -> str:
    """
    Input:
        prompt: str

    Output:
        response: str
    """
        
    client = AzureOpenAI(
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT_CHAT"),
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        api_version=os.getenv("AZURE_OPENAI_API_VERSION_CHAT")
    )
    
    model = "Llama-4-Maverick-17B-128E-Instruct-FP8"

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    
    return response.choices[0].message.content

def get_sql_response(prompt: str) -> str:
    """
    Input:
        prompt: str

    Output:
        response: str
    """
    
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    api_key = os.getenv("AZURE_OPENAI_API_KEY")
    api_version = os.getenv("AZURE_OPENAI_API_VERSION")

    client = AzureOpenAI(
        azure_endpoint=endpoint,
        api_key=api_key,
        api_version=api_version
    )

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
            endpoint = os.getenv("AZURE_SEARCH_ENDPOINT")
            index_name = os.getenv("AZURE_SEARCH_QUESTIONS_INDEX")
            api_key = os.getenv("AZURE_SEARCH_API_KEY")


            credential = AzureKeyCredential(api_key)
            cls._instance = SearchClient(
                endpoint=endpoint,
                index_name=index_name,
                credential=credential
            )
        return cls._instance   

class AzureAISearchSchemaConnection:
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            from azure.search.documents import SearchClient
            endpoint = os.getenv("AZURE_SEARCH_ENDPOINT")
            index_name = os.getenv("AZURE_SEARCH_SCHEMAS_INDEX")
            api_key = os.getenv("AZURE_SEARCH_API_KEY")

            credential = AzureKeyCredential(api_key)
            
            cls._instance = SearchClient(
                endpoint=endpoint,
                index_name=index_name,
                credential=credential
            )
        return cls._instance