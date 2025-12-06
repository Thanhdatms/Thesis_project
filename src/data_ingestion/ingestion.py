import csv
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from services.LLM_connector import to_vector
import os
import uuid
from dotenv import load_dotenv


# Load environment variables from .env file
load_dotenv()



def create_schema_documents(search_client, schemas_list: list):
    """
    Input:
        schemas_list: list of dicts, e.g.
        [
            {
                "schema_name": "...",
                "description": "...",
                "schema_info": "...",
            },
            ...
        ]

    Output:
        Uploads schema documents to Azure AI Search
    """
    documents = []

    for schema in schemas_list:
        doc_id = str(uuid.uuid4())
        desc_vector = to_vector(schema["description"])
        
        
        document = {
            "id": doc_id,
            "schema_name": schema["schema_name"],
            "description": schema["description"],
            "description_vector": desc_vector,
            "schema_info": schema["schema_info"],
        }

        documents.append(document)
    
    
    if documents:
        search_client.upload_documents(documents=documents)
        
        

def create_question_documents(search_client, questions_list: list):
    """
    Input:
        questions_list: list of dicts, e.g.
        [
            {
                "question": "...",
                "sql": "..."
            },
            ...
        ]

    Output:
        Uploads question documents to Azure AI Search
    """
    documents = []

    for question_item in questions_list:
        doc_id = str(uuid.uuid4())
        ques_vector = to_vector(question_item["question"])

        document = {
            "id": doc_id,
            "question": question_item["question"],
            "question_vector": ques_vector,
            "sql": question_item["sql"],
        }

        documents.append(document)

    if documents:
        search_client.upload_documents(documents=documents)

def load_data(schemas_path, questions_path):
    """
    Input:
        schemas_list: list of schema dicts
        questions_list: list of question dicts

    Output:
        Loads data into Azure AI Search
    """
    schemas_list = []
    questions_list = []
    schemas_path = os.path.abspath("public/schema.csv")
    with open(schemas_path, 'r', encoding='utf-8', newline='') as f:
        # logic loading data into format 
        reader = csv.DictReader(f)
        for row in reader:
            schemas_list.append({
                "schema_name": row["name"],
                "description": row["description"],
                "schema_info": row["info"],
            })

    with open(questions_path, 'r', encoding='utf-8', newline='') as f:
        # logic loading data into format
        reader = csv.DictReader(f)
        for row in reader:
            questions_list.append({
                "question": row["question"],
                "sql": row["sql"],
            })
    return schemas_list, questions_list


if __name__ == "__main__":
    # load data
    schema_path = os.path.abspath("public/schema.csv")
    questions_path = os.path.abspath("public/questions.csv")
    schemas_list, questions_list = load_data(
        schemas_path=schema_path, 
        questions_path=questions_path
    )
    # Initialize Azure AI Search client
    schemas_search_client = SearchClient(
        endpoint=os.getenv("AZURE_SEARCH_ENDPOINT"),
        index_name=os.getenv("AZURE_SEARCH_SCHEMAS_INDEX"),
        credential=AzureKeyCredential(os.getenv("AZURE_SEARCH_API_KEY"))
    )
    questions_search_client = SearchClient(
        endpoint=os.getenv("AZURE_SEARCH_ENDPOINT"),
        index_name=os.getenv("AZURE_SEARCH_QUESTIONS_INDEX"),
        credential=AzureKeyCredential(os.getenv("AZURE_SEARCH_API_KEY"))
    )

    # # Create and upload schema documents
    create_schema_documents(schemas_search_client, schemas_list)
    # # Create and upload question documents
    # create_question_documents(questions_search_client, questions_list)
