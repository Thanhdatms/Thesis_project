import os
import json
from dotenv import load_dotenv

# IMPORTANT FIX FOR WINDOWS
import asyncio
import sys
if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from gremlin_python.driver import client, serializer

load_dotenv()

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


# --------------------------------------------
# HELPERS
# --------------------------------------------
def create_vertex(label: str, data=None, last_data=None):
    # Nếu có data (dict), chuyển sang JSON an toàn để nhúng vào Gremlin
    if data is not None:
        data_json = json.dumps(data)  # JSON dùng dấu "
        data_property = f".property('data', '{data_json}')"
    elif last_data is not None:
        actual = json.dumps(last_data["actual"]).replace("'", "\\'")
        forecast = json.dumps(last_data["forecast"]).replace("'", "\\'")
        variance = json.dumps(last_data["variance"]).replace("'", "\\'")

        data_property = f"""
        .property('actual', '{actual}')
        .property('forecast', '{forecast}')
        .property('variance', '{variance}')
        """
    else:
        data_property = ""

    query = f"""
        g.V().has('id', '{label}').fold().
        coalesce(
            unfold(),
            addV('{label}')
                .property('id', '{label}')
                .property('name', '{label}')
                {data_property}
                .property('pk', 'pk')
        )
    """

    print("=== Gremlin query ===")
    print(query)

    return gremlin_connection(query)


def create_edge(from_id: str, to_id: str):
    query = f"""
        g.V().has('id', '{from_id}').as('a')
         .V().has('id', '{to_id}')
         .coalesce(
             __.inE('HAS').where(outV().has('id', '{from_id}')),
             __.addE('HAS').from('a')
         )
    """
    return gremlin_connection(query)


# --------------------------------------------
# DOMAIN-SPECIFIC CREATION FUNCTIONS
# --------------------------------------------
def create_root_finance_report():
    create_vertex("financial_reports")


def create_type_finance_report():
    create_vertex("quater_report")
    create_vertex("revenue_year_report")

    create_edge("financial_reports", "quater_report")
    create_edge("financial_reports", "revenue_year_report")


def create_revenue_report_year(file_path):
    # create year
    with open(file_path) as f:
        data = json.load(f)

    years = list(data.keys())
    for year in years:
        year_id = str(year) + "_revenue"

        create_vertex(label=year_id)
        create_edge("revenue_year_report", year_id)
    
        for q_key, q_value in data[year].items():

            # create quarter vertex
            pro_id = str(year) + "_" + str(q_key)
            create_vertex(label=pro_id, data=q_value)
            create_edge(year_id, pro_id)



def create_quater_report_year(file_path):
    # create year
    with open(file_path) as f:
        data = json.load(f)

    year = data['year']
    year_id = str(year) + "_quater_report"
    create_vertex(label=year_id, data=year_id)
    create_edge(from_id='quater_report', to_id=year_id)
    quarters = list(data["quarters"].keys())
    print(quarters)
    for q in quarters:
        # create vertex
        q_id = str(year)+'_'+str(q)
        create_vertex(label=q_id)
        create_edge(from_id=year_id, to_id=q_id)

        months = list(data["quarters"][q].keys())
        for month in months:
            # create month
            month_id = str(month) + "_" + q_id
            create_vertex(label=month_id)
            create_edge(from_id=q_id, to_id=month_id)

            atts = list(data["quarters"][q][month].keys())
            # create attributes
            for att in atts:
                # create attributes
                att_id = str(att) + "_" + month_id
                keys = list(data['quarters'][q][month][att].keys())

                create_vertex(label=att_id, last_data={
                    "actual": data['quarters'][q][month][att][keys[0]],
                    "forecast": data['quarters'][q][month][att][keys[1]],
                    "variance": data['quarters'][q][month][att][keys[2]] 
                })
                create_edge(from_id=month_id, to_id=att_id)


# --------------------------------------------
# RUN INITIALIZATION
# --------------------------------------------
if __name__ == "__main__":
    # create_root_finance_report()
    # create_type_finance_report()
    
    root_path_2019 = r'C:\Users\ADMIN\Documents\Thesis\Thesis_project\src\services\knowledge_graph.py\sale_reports\sale_report_2019.json'
    root_path_2020 = r'C:\Users\ADMIN\Documents\Thesis\Thesis_project\src\services\knowledge_graph.py\sale_reports\sale_report_2020.json'
    root_path_2021 = r'C:\Users\ADMIN\Documents\Thesis\Thesis_project\src\services\knowledge_graph.py\sale_reports\sale_report_2021.json'
    root_path_2022 = r'C:\Users\ADMIN\Documents\Thesis\Thesis_project\src\services\knowledge_graph.py\sale_reports\sale_report_2022.json'
    root_path_2023 = r'C:\Users\ADMIN\Documents\Thesis\Thesis_project\src\services\knowledge_graph.py\sale_reports\sale_report_2023.json'
    root_path_2024 = r'C:\Users\ADMIN\Documents\Thesis\Thesis_project\src\services\knowledge_graph.py\sale_reports\sale_report_2024.json'

    revenue_report = r'C:\Users\ADMIN\Documents\Thesis\Thesis_project\src\services\knowledge_graph.py\sale_reports\sale_year_report.json'

    create_quater_report_year(file_path=root_path_2019)
    create_quater_report_year(file_path=root_path_2020)
    create_quater_report_year(file_path=root_path_2021)
    create_quater_report_year(file_path=root_path_2022)
    create_quater_report_year(file_path=root_path_2023)
    create_quater_report_year(file_path=root_path_2024)

    # create_revenue_report_year(file_path=revenue_report)

    print("✔ Knowledge graph initialization completed successfully.")
