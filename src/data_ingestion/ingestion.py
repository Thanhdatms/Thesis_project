from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from services.LLM_connector import to_vector
import os
import uuid

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

def load_data(schemas_list, questions_list):
    """
    Input:
        schemas_list: list of schema dicts
        questions_list: list of question dicts

    Output:
        Loads data into Azure AI Search
    """

    # logic loadingdata into format 
    return schemas_list, questions_list


if __name__ == "__main__":
    # load data
    schemas_list, questions_list = load_data(...)

    # Initialize Azure AI Search client
    schemas_search_client = SearchClient(
        endpoint=os.getenv("AZURE_SEARCH_SCHEMA_ENDPOINT"),
        index_name=os.getenv("AZURE_SEARCH_SCHEMAS_INDEX"),
        credential=AzureKeyCredential(os.getenv("AZURE_SEARCH_SCHEMA_API_KEY"))
    )
    questions_search_client = SearchClient(
        endpoint=os.getenv("AZURE_SEARCH_QUESTION_ENDPOINT"),
        index_name=os.getenv("AZURE_SEARCH_QUESTIONS_INDEX"),
        credential=AzureKeyCredential(os.getenv("AZURE_SEARCH_QUESTION_API_KEY"))
    )

    # Create and upload schema documents
    create_schema_documents(schemas_search_client, schemas_list)
    # Create and upload question documents
    create_question_documents(questions_search_client, questions_list)
