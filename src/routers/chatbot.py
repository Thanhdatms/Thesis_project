import csv
from fastapi import APIRouter, File, Form, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from graph import app as langgraph_app
from services.vector_service import SQLHandler

router = APIRouter(prefix="/chatbot", tags=["chatbot"])


class PromptRequest(BaseModel):
    question: str

@router.post("/prompt")
async def post_prompt(prompt_request: PromptRequest, request: Request):
    thread_id = "session-001"

    try:
        user_prompt = prompt_request.question
        
        initial_state = {
            "user_query": user_prompt
        }
        
        final_state = await langgraph_app.ainvoke(initial_state, config={"thread_id": thread_id})
        print(f"Final State: {final_state["final_response"]}")
        return JSONResponse(
            status_code=200,
            content={"data": final_state["final_response"]}
        )

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )
        
# @router.post("/stream")
# async def prompt_stream(prompt_request: PromptRequest):
#     thread_id = "session-001"
#     user_prompt = prompt_request.question

#     initial_state = {"user_query": user_prompt}


#     async def event_generator():
#         final_output = None
#         async for mode, event in langgraph_app.astream(
#             initial_state,
#             config={"thread_id": thread_id},
#             stream_mode=["updates", "custom"],
#         ):

#             if (mode == "custom"):
#                 yield (
#                     "event: progress\n"
#                     f"data: {event}\n\n"
#                 )
            
#             if (
#                mode == "updates" and
#                "post_sql_contextual" in event
#                 and "final_response" in event["post_sql_contextual"]
#             ):
#                 final_output = event["post_sql_contextual"]["final_response"]

#         # 3. After streaming loop is done → send final SSE event
#         if final_output is not None:
#             yield (
#                 "event: final\n"
#                 f"data: {json.dumps(final_output)}\n\n"
#             )

#     return StreamingResponse(event_generator(), media_type="text/event-stream")
        
        
@router.post("/execute_queries/")
async def execute():
    try:
        csv_file = "sql_query_responses_1.csv"

        # 1. Read all rows first
        rows = []
        with open(csv_file, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames  # keep the header
            if "sql" not in fieldnames or "answer" not in fieldnames:
                raise Exception("CSV must contain columns 'sql' and 'answer'")
            
            for row in reader:
                rows.append(row)

        # 2. Execute query for each row
        for row in rows:
            sql_query = row.get("sql")
            result = await SQLHandler.execute_query(sql_query)
            row["answer"] = result  # Write the result to the answer column

        # 3. Rewrite the CSV with updated answer column
        with open(csv_file, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)

        return "done"

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )
