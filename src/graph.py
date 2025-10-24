from typing import Dict, List, TypedDict, Annotated
from langchain_core.messages import HumanMessage, ToolMessage, AIMessage, SystemMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from vector_service import TableRetriever, QuestionRetriever, SQLHandler
from Chatbot.utils.chatbot.prompt_templates import sql_retriver_template, final_answer_template
from Chatbot.infrastructure.llm.LLM_connector import get_openai_response, get_openai_vector
from Chatbot.utils.chatbot.prompt_templates import REGENERATE_SQL_TEMPLATE
class AgentState(TypedDict):
    message: Annotated[list, add_messages]
    user_query: str

    query_embedding: List[float]
    related_queries: List[str]
    related_schemas: List[str]

    sql_generation: str
    sql_verifier_status: bool
    execute_error_message: str
    query_result: str
    final_response: str

def vectorizer(state: AgentState) -> AgentState:
    user_query = state.get("user_query")
    query_embedding = get_openai_vector(user_query)

    return {"query_embedding": query_embedding}

def retrieval_knowledge_base(state: AgentState) -> AgentState:
    related_queries = QuestionRetriever().get_related_question(state.get("user_query"))
    related_schemas = TableRetriever().get_related_table(state.get("user_query"))

    return {"related_queries": related_queries, "related_schemas": related_schemas}


def pre_sql_contextual(state: AgentState) -> AgentState:
    sql_retriver_template = sql_retriver_template(
        related_question=state.get("related_queries"), 
        related_table=state.get("related_schemas"),
        question=state.get("user_query")
    )

    return {"sql_retriver_template": sql_retriver_template}

def error_handler(state: AgentState) -> AgentState:
    return {"error": "An error occurred during processing."}

def sql_generation(state: AgentState) -> AgentState:
    query_prompt = state.get("sql_retriver_template")
    sql_generation = get_openai_response(query_prompt)
    extracted_sql = SQLHandler.extract_sql_response(sql_generation)
    state["sql_generation"] = extracted_sql
    return {"sql_generation": extracted_sql}

    
def sql_verifier(state: AgentState) -> AgentState:
    count = 3
    verify_status = False
    while count > 0:
        try:
            query = state.get("sql_generation")
            query_results = SQLHandler.execute_query(query)
            verify_status = True
            break
        except Exception as e:
            state["execute_error_message"] = str(e)
            count -= 1

            sql_generation = state['sql_generation']
            related_schema = state['related_schemas']
            question = state['user_query']
            error_message = state['execute_error_message']
            regenerate_prompt = REGENERATE_SQL_TEMPLATE.format(
                question=question,
                schema=related_schema,
                sql_query=sql_generation,
                error_message=error_message
            )
            sql_generation = get_openai_response(regenerate_prompt)
            state["sql_generation"] = sql_generation
            if count == 0:
                verify_status = False
                state["sql_generation"] = None
    return {"verify_status": verify_status}
    
def post_sql_contextual(state: AgentState) -> AgentState:
    response_prompt = final_answer_template(
        question=state.get("user_query"),
        answer=state.get("query_result")
    )
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

# Compile
app = graph.compile()


# Export the graph as a PNG image
graph_viz = app.get_graph()
graph_viz.draw_mermaid_png(output_file_path="langgraph_workflow.png")
print("LangGraph workflow exported to langgraph_workflow.png")