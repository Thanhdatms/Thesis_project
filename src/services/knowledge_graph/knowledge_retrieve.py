import os
import json
from dotenv import load_dotenv
# IMPORTANT FIX FOR WINDOWS
import asyncio
from openai import OpenAI
from gremlin_python.driver import client as gremlin_client
import sys

from services.knowledge_graph.knowledge_graph_template import QUESTION_ROUTER_TEMPLATE, SUMMARY_GREMLIN_TEMPLATE, SUMMARY_QUESTION
if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from gremlin_python.driver import client, serializer
import json
from openai import OpenAI

load_dotenv()

deployment_name = "Llama-4-Maverick-17B-128E-Instruct-FP8"

endpoint = "https://thesisresource.services.ai.azure.com/openai/v1/"
model_name = "Llama-4-Maverick-17B-128E-Instruct-FP8"
deployment_name = "Llama-4-Maverick-17B-128E-Instruct-FP8"


openai_client = OpenAI(
    base_url=f"{endpoint}",
    api_key=os.environ.get('AZURE_OPENAI_API_KEY')
)


def get_llm_result(message):
    completion = openai_client.chat.completions.create(
        model=deployment_name,
        messages=[{"role": "user", "content": message}],
    )
    return completion.choices[0].message.content

# --------------------------------------------
# GLOBAL SINGLETON CLIENT  (prevents loop crash)
# --------------------------------------------
GREMLIN_CLIENT = client.Client(
    url=os.environ.get("KNOWLEDGE_URL"),
    traversal_source="g",
    username=os.environ.get("KNOWLEDGE_USERNAME"),
    password=os.environ.get("KNOWLEDGE_GRAPH_PASSWORD"),
    message_serializer=serializer.GraphSONSerializersV2d0()
)

def gremlin_connection(query: str):
    try:
        future = GREMLIN_CLIENT.submitAsync(query)
        result = future.result()
        return result
    except Exception as e:
        print(f"[ERROR] Gremlin Query Failed:\n{query}\nError: {e}")
        raise

def get_knowledge_graph_data(question):
    new_question = get_llm_result(message=SUMMARY_QUESTION.format(question=question))
    print(new_question)
    # Extract text from LLM result
    new_question_text = new_question
    gremlin_require_raw = get_llm_result(message=QUESTION_ROUTER_TEMPLATE.format(question=new_question_text))

    print("raw")
    print(gremlin_require_raw)
    gremlin_require_json = json.loads(gremlin_require_raw)

    # Now gremlin_require_json is a real dict
    key = list(gremlin_require_json.keys())[0]
    print(key)
    print(gremlin_require_json[key])
    
    if key == "handbook":
        data = get_handbook(gremlin_require_json[key])
    elif key == "quarter_report":
        data = get_quarter_report(gremlin_require_json[key])
    elif key == "revenue_report":
        data = get_revenue(gremlin_require_json[key])
        print(data)
    else:
        data = None

    summary_data = get_llm_result(
        message=SUMMARY_GREMLIN_TEMPLATE.format(question = question, data=data)
    )

    return summary_data

def get_handbook(list_data):
    results = []
    for data in list_data:
        gremlin_query = f"g.V().has('id', '{data}').repeat(out()).emit().path()"
        res = gremlin_connection(query=gremlin_query)

        # Extract the actual Gremlin results
        res_data = res.all().result()

        results.append(res_data)
    
    return results

def get_quarter_report(list_data):
    results = []

    for data in list_data:
        gremlin_query = f"g.V().has('id', '{data}').out().valueMap(true)"
        res = gremlin_connection(query=gremlin_query)

        # Extract the actual Gremlin results
        res_data = res.all().result()

        results.append(res_data)

    return results

def get_revenue(list_data):
    results = []

    for data in list_data:
        gremlin_query = f"g.V().has('id', '{data}')"
        res = gremlin_connection(query=gremlin_query)

        # Extract the actual Gremlin results
        res_data = res.all().result()

        results.append(res_data)
        
    return results




# data = get_knowledge_graph_data(question='what is the revenue of product Corsair_K95_RGB_Platinum')
# print(data)

