from typing import List, TypedDict, Annotated
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages

from services.vector_service import SchemaRetriever, QuestionRetriever, SQLHandler
from services.vector_service import SchemaRetriever, QuestionRetriever, SQLHandler
from services.prompt_function import sql_retriever_template, final_answer_template
from services.LLM_connector import to_vector, get_openai_response
from langgraph.checkpoint.memory import  MemorySaver
from langgraph.config import get_stream_writer

from services.prompt_template import ERROR_RESPONSE, REGENERATE_SQL_TEMPLATE
from services.prompt_template import ERROR_RESPONSE, REGENERATE_SQL_TEMPLATE
class AgentState(TypedDict):
    messages: Annotated[list, add_messages]
    user_query: str

    query_embedding: List[float]
    related_queries: List[str]
    related_schemas: List[str]
    sql_query: str
    sql_query: str

    sql_generation: str
    sql_verifier_status: bool
    execute_error_message: str
    query_result: str
    final_response: str
    
    
def vectorizer(state: AgentState) -> AgentState:
    writer = get_stream_writer()
    writer({"progress": "Vecotr questiob"})
    user_query = state.get("user_query")
    query_embedding = to_vector(user_query)
 
    return {"query_embedding": query_embedding}

def retrieval_knowledge_base(state: AgentState) -> AgentState:
    writer = get_stream_writer()
    writer({"progress": "Retrieval knowledge base"})
    related_queries = QuestionRetriever.get_related_question(state.get("user_query"))
    related_schemas = SchemaRetriever.get_related_schemas(state.get("user_query"))
    return {"related_queries": related_queries, "related_schemas": related_schemas}


def pre_sql_contextual(state: AgentState) -> AgentState:
    writer = get_stream_writer()
    writer({"progress": "Retrieval sql template"})
    sql_query = sql_retriever_template(
        related_question=state.get("related_queries"), 
        related_table=state.get("related_schemas"),
        question=state.get("user_query")
    )
    return {"sql_query": sql_query}

def error_handler(state: AgentState) -> AgentState:
    return {"error": "An error occurred during processing."}

def sql_generation(state: AgentState) -> AgentState:
    query_prompt = state.get("sql_query")
    query_prompt = state.get("sql_query")
    sql_generation = get_openai_response(query_prompt)
    extracted_sql = SQLHandler.extract_sql_response(sql_generation)
    state["sql_generation"] = extracted_sql
    return {"sql_generation": extracted_sql}

    
async def sql_verifier(state: AgentState) -> AgentState:
async def sql_verifier(state: AgentState) -> AgentState:
    count = 3
    verify_status = False


    while count > 0:
        try:
            query = state.get("sql_generation")
            if not query:
                raise ValueError("No SQL query is generated.")
            
            query_results = await SQLHandler.execute_query(query)
            verify_status = True
            break
        except Exception as e:
            # print(ERROR_RESPONSE.format(error=str(e)))
            # state["execute_error_message"] = ERROR_RESPONSE.format(error=str(e))
            count -= 1
            sql_generation = state['sql_generation']
            related_schema = state['related_schemas']
            question = state['user_query']
            error_message = str(e)
            regenerate_prompt = REGENERATE_SQL_TEMPLATE.format(
                question=question,
                schema=related_schema,
                sql_query=sql_generation,
                error_message=error_message
            )
            print(regenerate_prompt)
            sql_generation = get_openai_response(regenerate_prompt)
 
            state["sql_generation"] = sql_generation
            print(f"Count: {count}")
            print(f"Count: {count}")
            if count == 0:
                verify_status = False
                state["sql_generation"] = None
    return {
        "verify_status": verify_status, 
        "query_result": query_results if verify_status else None
    }
    
def post_sql_contextual(state: AgentState) -> AgentState:
    response_prompt = final_answer_template(
        question=state.get("user_query"),
        answer=state.get("query_result")
    )
    print("Query Result:", state.get("query_result"))
    final_response_content = get_openai_response(response_prompt)
    state["final_response"] = final_response_content
    return {"final_response": final_response_content}

# Conditional edge function
def should_continue(state: AgentState) -> str:
    status = state.get("verify_status", "successfully")
    return status

# --- Build LangGraph ---
graph = StateGraph(AgentState)

# Add nodes
graph.add_node("vectorizer", vectorizer)
graph.add_node("retrieval_query_and_schema", retrieval_knowledge_base)
graph.add_node("pre_sql_contextual", pre_sql_contextual)
graph.add_node("sql_generation", sql_generation)
graph.add_node("error_handler", error_handler)
graph.add_node("sql_verifier", sql_verifier)
graph.add_node("post_sql_contextual", post_sql_contextual)

# Add edges
graph.add_edge("vectorizer", "retrieval_query_and_schema")
graph.add_edge("retrieval_query_and_schema", "pre_sql_contextual")
graph.add_edge("pre_sql_contextual", "sql_generation")
graph.add_edge("sql_generation", "sql_verifier")
graph.add_conditional_edges(
    "sql_verifier",
    should_continue,
    {
        "successfully": "post_sql_contextual",
        "error": "error_handler",
    }
)
graph.add_edge("post_sql_contextual", END)
graph.add_edge("error_handler", END)

graph.set_entry_point("vectorizer")

# --- Add memory ---
memory = MemorySaver()

# Compile
app = graph.compile(checkpointer=memory)

# Export the graph as a PNG image
graph_viz = app.get_graph()
graph_viz.draw_mermaid_png(output_file_path="langgraph_workflow.png")
print("LangGraph workflow exported to langgraph_workflow.png")







