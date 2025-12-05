import os
from openai import AzureOpenAI
from langgraph.graph import StateGraph, START, END
from typing import Annotated

from langchain.chat_models import init_chat_model
from langchain_core.messages import BaseMessage
from typing_extensions import TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from Chatbot.infrastructure.llm.LLM_connector import get_openai_response


# --- State definition ---
class State(TypedDict):
    messages: Annotated[list, add_messages]


# --- Node function ---
def chatbot(state: State) -> State:
    messages = state["messages"]

    chat_payload = []
    for m in messages:
        if isinstance(m, HumanMessage):
            chat_payload.append({"role": "user", "content": m.content})
        elif isinstance(m, AIMessage):
            chat_payload.append({"role": "assistant", "content": m.content})
        elif isinstance(m, SystemMessage):
            chat_payload.append({"role": "system", "content": m.content})
        else:
            chat_payload.append({"role": "user", "content": str(m)})

    # Gọi Azure OpenAI
    response = llm.chat.completions.create(
        model="gpt-4o",
        messages=chat_payload,
    )

    ai_msg = response.choices[0].message
    ai_response = ai_msg.content

    print(f"🤖 AI:", ai_response)

    # Trả lại LangGraph state — dùng AIMessage để giữ đúng kiểu
    return {"messages": [AIMessage(content=ai_response)]}


# --- Build graph ---
graph_builder = StateGraph(State)
graph_builder.add_node("chatbot", chatbot)
graph_builder.add_edge("chatbot", END)
graph_builder.set_entry_point("chatbot")

# --- Add memory ---
memory = InMemorySaver()
graph = graph_builder.compile(checkpointer=memory)


# --- Run test ---
if __name__ == "__main__":
    thread_id_01 = "session-001"
    thread_id_02 = 'session-002'

    print("\n=== Round 1 ===")
    graph.invoke(
        {"messages": [HumanMessage(content="Hello, My name is Alex?")]},
        config={"thread_id": thread_id_01},
    )

    print("\n=== Round 2 ===")
    graph.invoke(
        {"messages": [HumanMessage(content="Remember my name?")]},
        config={"thread_id": thread_id_02},
    )

    print("\n=== Round 3 (new session) ===")
    graph.invoke(
        {"messages": [HumanMessage(content="Tell me my name")]},
        config={"thread_id": thread_id_01},
    )