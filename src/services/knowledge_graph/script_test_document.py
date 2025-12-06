import os
import json
from dotenv import load_dotenv
from gremlin_python.driver import client, serializer

# IMPORTANT FIX FOR WINDOWS
import asyncio
import sys

load_dotenv()
if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

GREMLIN_CLIENT = client.Client(
    url=os.environ.get("KNOWLEDGE_URL"),
    traversal_source="g",
    username=os.environ.get("KNOWLEDGE_USERNAME"),
    password=os.environ.get("KNOWLEDGE_GRAPH_PASSWORD"),
    message_serializer=serializer.GraphSONSerializersV2d0()
)


# --------------------------------------------
# SAFE EXECUTOR
# --------------------------------------------
def gremlin_connection(query: str):
    try:
        future = GREMLIN_CLIENT.submitAsync(query)
        result = future.result()
        return result
    except Exception as e:
        print(f"[ERROR] Gremlin Query Failed:\n{query}\nError: {e}")
        raise

def create_vertex(id: str, label: str, properties: dict):
    # Build chuỗi .property(...)
    prop_str = ""
    for key, values in properties.items():
        # Mỗi key là list → bạn lấy value đầu hoặc nối
        for item in values:
            prop_str += f".property('{key}', '{item['value']}')\n            "

    query = f"""
        g.V().has('id', '{id}').fold().
        coalesce(
            unfold(),
            addV('{label}')
                .property('id', '{id}')
                {prop_str}
                .property('pk', 'pk')
        )
    """

    print("=== Gremlin query ===")
    print(query)

    return gremlin_connection(query)

def create_edge(id: str, label: str, outV: str, inV: str):
    query = f"""
        g.V().has('id', '{outV}').as('a')
         .V().has('id', '{inV}')
         .coalesce(
             __.inE('{label}').where(outV().has('id', '{outV}')),
             __.addE('{label}').from('a').property('id', '{id}').property('pk', 'pk')
         )
    """

    return gremlin_connection(query)

def create_handbook(file_path):

    with open(file_path, encoding="utf-8") as f:
        data = json.load(f)

    vertices = data['vertices']

    # for vertex in vertices:
    #     id = vertex['id']
    #     label = vertex['label']
    #     properties = vertex['properties']

    #     create_vertex(id, label, properties)

    edges = data['edges']

    for edge in edges:
        id = edge['id']
        label = edge['label']
        outV = edge['outV']
        inV = edge['inV']

        create_edge(id, label, outV, inV)

create_handbook(r'C:\Users\ADMIN\Documents\Thesis\Thesis_project\src\services\knowledge_graph.py\sale_reports\document.json')

