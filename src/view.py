from rest_framework.views import APIView
from rest_framework.response import Response
from Chatbot.core.services.vector_service import QuestionRetriever, TableRetriever
from Chatbot.utils.chatbot.prompt_templates import final_answer_template, sql_retriver_template
from Chatbot.infrastructure.llm.LLM_connector import *
from Chatbot.core.services.vector_service import SQLHandler 
from azure.ai.inference.models import UserMessage
from .serializer import sql_response_serializer, final_response
from rest_framework.views import APIView
from rest_framework.response import Response
from Chatbot.infrastructure.llm.LLM_connector import get_openai_response

class QuestionHandler(APIView):
    def post(self, request):
        """
        Handles POST requests to process a user's question, retrieve related data,
        generate SQL queries, execute them, and return a formatted response.
        """
        question = request.data.get('question')
        if not question:
            return Response({"error": "Question is required"}, status=400)

        try:
            related_question = QuestionRetriever.get_related_question(question=question)
            related_table = TableRetriever.get_related_table(question=question)
            sql_prompt = sql_retriver_template(
                related_question=related_question, 
                related_table=related_table,
                question=question
            )
            print(sql_prompt)
            query_response = get_openai_response(sql_prompt)
            extracted_query = SQLHandler.extract_sql_response(query_response)  
            query_results = execute_sql_query(query=extracted_query)

            # Generate final response
            response_prompt = final_answer_template(
                question=question,
                answer=query_results
            )
            final_response_content = get_openai_response(response_prompt)
            
            return Response({
                "message": "Success",
                "data": {
                    "response": final_response_content
                }
            }, status=200)

        except Exception as e:
            return Response({"error": f"An unexpected error occurred: {str(e)}"}, status=500)

def validate_query(data):
    if not data:
        return None
    try:
        # Handle single-column results
        if all(len(item) == 1 for item in data):
            if isinstance(data[0][0], int):
                return data[0][0]
            elif isinstance(data[0][0], str):
                return [item[0] for item in data]
        elif all(len(item) >= 2 for item in data) and all(isinstance(item[1], str) for item in data):
            return data
        return None
    except Exception as e:
        return None
    
def execute_sql_query(query):
    if query is None:
        return None
    
    try:
        db_instance = AzureSQLConnection.get_instance()
        cursor = db_instance.cursor()
        db_instance.autocommit = True
        cursor.execute(query=query)
        query_results = cursor.fetchall()

        if not query_results:
            return None

        db_instance.commit()
        return query_results

    except Exception as e:
        print(f"Error: {e}")
        return "Error: " + str(e)
    finally:
        cursor.close()