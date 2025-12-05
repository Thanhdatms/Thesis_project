from rest_framework import serializers
from django.http import JsonResponse
from Chatbot.core.services.vector_service import SQLHandler

def sql_response_serializer(retriever_response):
    try: 
        response_content = retriever_response.choices[0].message.content
        extracted_response = SQLHandler.extract_sql_response(response_content)
        
        model = retriever_response.model
        prompt_tokens = retriever_response.usage.prompt_tokens
        completion_tokens = retriever_response.usage.completion_tokens
        total_tokens = retriever_response.usage.total_tokens

        return {
            'response': response_content,
            'extracted_response': extracted_response,
            'model': model,
            'prompt_tokens': prompt_tokens,
            'completion_tokens': completion_tokens,
            'total_tokens': total_tokens
        }

    except AttributeError as e:
        return JsonResponse({'error': 'Invalid response format', 'details': str(e)}, status=500)
    
def final_response(retriever_response):
    try:
        response_content = retriever_response.choices[0].message.content
        model = retriever_response.model
        prompt_tokens = retriever_response.usage.prompt_tokens
        completion_tokens = retriever_response.usage.completion_tokens
        total_tokens = retriever_response.usage.total_tokens

        return {
            'response': response_content,
            'model': model,
            'prompt_tokens': prompt_tokens,
            'completion_tokens': completion_tokens,
            'total_tokens': total_tokens
        }

    except AttributeError as e:
        return {'error': 'Invalid response format', 'details': str(e)}