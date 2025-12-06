from openai import OpenAI
from dotenv import load_dotenv
import os


load_dotenv()
deployment_name = "Llama-4-Maverick-17B-128E-Instruct-FP8"

client = OpenAI(
    base_url=f"{os.environ.get('AZURE_OPENAI_ENDPOINT_CHAT')}",
    api_key= os.environ.get('AZURE_OPENAI_API_KEY')
)

def get_llm_result(message):
    model = model
    completion=[
        {
            "role": "user",
            "content": "{message}"
        }
    ]

    print(completion.choices[0].message)

