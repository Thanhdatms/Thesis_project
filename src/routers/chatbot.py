from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from graph import app as langgraph_app
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