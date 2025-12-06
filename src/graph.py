import json
from typing import List, TypedDict, Annotated
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages

from services.knowledge_graph.knowledge_graph_template import QUESTION_ROUTER_TEMPLATE, SUMMARY_GREMLIN_TEMPLATE, SUMMARY_QUESTION
from services.knowledge_graph.knowledge_retrieve import get_handbook, get_knowledge_graph_data, get_quarter_report, get_revenue
from services.vector_service import SchemaRetriever, QuestionRetriever, SQLHandler
from services.prompt_function import sql_retriever_template, final_answer_template
from services.LLM_connector import to_vector, get_openai_response
from langgraph.checkpoint.memory import  MemorySaver
from langgraph.config import get_stream_writer

from services.prompt_template import ERROR_RESPONSE, REGENERATE_SQL_TEMPLATE, ROUTER_TEMPLATE

class AgentState(TypedDict):
    messages: Annotated[list, add_messages]
    user_query: str
    structured_question: str
    unstructured_question: str

    query_embedding: List[float]
    related_queries: List[str]
    related_schemas: List[str]
    sql_query: str

    sql_generation: str
    sql_verifier_status: bool
    execute_error_message: str
    query_result: str
    final_response: str

    unstructured: bool
    structured: bool
    combined_response: str
    unstructured_response: str
    structured_response: str
    
    
def classify_route(state: AgentState) -> AgentState:
    user_query = state.get("user_query")
    prompt = ROUTER_TEMPLATE.format(question=user_query)
    result = get_openai_response(prompt)
    route = json.loads(result).get("route")
    unstructured = False
    structured = False
    structured_question = None
    unstructured_question = None
    
    if route == "UNSTRUCTURED_DATA":
        print("Route to UNSTRUCTURED_DATA")
        unstructured = True
        structured = False
    elif route == "STRUCTURED_DATA":
        print("Route to STRUCTURED_DATA")
        unstructured = False
        structured = True
    else:
        print("Both route to UNSTRUCTURED_DATA and STRUCTURED_DATA")
        unstructured = True
        structured = True
    
    structured_question = json.loads(result).get("structure_question") if structured else None
    unstructured_question = json.loads(result).get("unstructure_question") if unstructured else None
    print("structured_question:", structured_question)
    print("unstructured_question:", unstructured_question)
    
    return {
        "unstructured": unstructured, 
        "structured": structured,
        "structured_question": structured_question,
        "unstructured_question": unstructured_question,
    }
    

def document_retriever(state: AgentState) -> AgentState:
    question = state.get("unstructured_question")
    summary_data = get_knowledge_graph_data(question)
    return {"unstructured_response": summary_data}

def vectorizer(state: AgentState) -> AgentState:
    user_query = state.get("structured_question")
    print("User Query for Vectorizer:", user_query)
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
    sql_generation = get_openai_response(query_prompt)
    extracted_sql = SQLHandler.extract_sql_response(sql_generation)
    state["sql_generation"] = extracted_sql
    return {"sql_generation": extracted_sql}

    
async def sql_verifier(state: AgentState) -> AgentState:
    count = 3
    verify_status = False

    while count > 0:
        try:
            query = state.get("sql_generation")
            print("Executing SQL Query:", query)
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
            sql_generation = get_openai_response(regenerate_prompt)
 
            state["sql_generation"] = sql_generation
            print(f"Count: {count}")
            if count == 0:
                verify_status = False
                state["sql_generation"] = None
    return {
        "verify_status": verify_status, 
        "structured_response": query_results if verify_status else None
    }
    
def post_sql_contextual(state: AgentState) -> AgentState:
    response_prompt = final_answer_template(
        question=state.get("user_query"),
        answer=state.get("query_result")
    )
    final_response_content = get_openai_response(response_prompt)
    state["final_response"] = final_response_content
    return {"structured_response": final_response_content}

def aggregator(state: AgentState) -> AgentState:
    
    print("Structured Response:", state.get("structured_response"))
    print("Unstructured Response:", state.get("unstructured_response"))
    response_prompt = final_answer_template(
        question=state.get("user_query"),
        structured_response=state.get("structured_response", ""),
        unstructured_response=state.get("unstructured_response", "")
    )
    final_response_content = get_openai_response(response_prompt)
    return {"final_response": final_response_content}
    
def route_structured_decision(state: AgentState) -> AgentState:
    return {"structured": state.get("structured")}

def route_unstructured_decision(state: AgentState) -> AgentState:
    return {"unstructured": state.get("unstructured")}

# Conditional edge function
def should_continue(state: AgentState) -> str:
    status = state.get("verify_status", "successfully")
    return status

def should_route_structured_continue(state: AgentState) -> str:
    if state.get("structured") == True and state.get("unstructured") == False:
        return "STRUCTURED_DATA"
    else:
        return "SKIP"

def should_route_unstructured_continue(state: AgentState) -> str:
    if state.get("unstructured") == True and state.get("structured") == False:
        return "UNSTRUCTURED_DATA"
    else:
        return "SKIP"

# --- Build LangGraph ---
graph = StateGraph(AgentState)

# Add nodes
graph.add_node("classify_route", classify_route)
graph.add_node("vectorizer", vectorizer)
graph.add_node("retrieval_query_and_schema", retrieval_knowledge_base)
graph.add_node("pre_sql_contextual", pre_sql_contextual)
graph.add_node("sql_generation", sql_generation)
graph.add_node("error_handler", error_handler)
graph.add_node("sql_verifier", sql_verifier)
# graph.add_node("post_sql_contextual", post_sql_contextual)
graph.add_node("document_retriever", document_retriever )
graph.add_node("aggregator", aggregator)
graph.add_node("route_structured_decision", route_structured_decision)
graph.add_node("route_unstructured_decision", route_unstructured_decision)

# Add edges
graph.add_edge(START, "classify_route")
graph.add_edge("classify_route", "route_structured_decision")
graph.add_edge("classify_route", "route_unstructured_decision")
graph.add_conditional_edges(
    "route_structured_decision",
    lambda state: "STRUCTURED_DATA" if state.get("structured") else "aggregator",
    {
        "STRUCTURED_DATA": "vectorizer",
        "SKIP": "aggregator",
    }
)
graph.add_conditional_edges(
    "route_unstructured_decision",
    lambda state: "UNSTRUCTURED_DATA" if state.get("unstructured") else "aggregator",
    {
        "UNSTRUCTURED_DATA": "document_retriever",
        "SKIP": "aggregator",
    }
)
graph.add_edge("vectorizer", "retrieval_query_and_schema")
graph.add_edge("retrieval_query_and_schema", "pre_sql_contextual")
graph.add_edge("pre_sql_contextual", "sql_generation")
graph.add_edge("sql_generation", "sql_verifier")
graph.add_conditional_edges(
    "sql_verifier",
    should_continue,
    {
        "successfully": "aggregator",
        "error": "error_handler",
    }
)

# graph.add_edge("post_sql_contextual", END)
graph.add_edge("error_handler", END)
# graph.add_edge("document_retriever", END)
# graph.add_edge("post_sql_contextual", "aggregator")
graph.add_edge("document_retriever", "aggregator")
graph.add_edge("aggregator", END)

# --- Add memory ---
memory = MemorySaver()

# Compile
app = graph.compile(checkpointer=memory)

# Export the graph as a PNG image
graph_viz = app.get_graph()
graph_viz.draw_mermaid_png(output_file_path="langgraph_workflow.png")
print("LangGraph workflow exported to langgraph_workflow.png")