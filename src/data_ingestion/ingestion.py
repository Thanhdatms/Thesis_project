from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from services.vector_service import convert_to_vector
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
        desc_vector = convert_to_vector(schema["description"])

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
        ques_vector = convert_to_vector(question_item["question"])

        document = {
            "id": doc_id,
            "question": question_item["question"],
            "question_vector": ques_vector,
            "sql": question_item["sql"],
        }

        documents.append(document)

    if documents:
        search_client.upload_documents(documents=documents)
