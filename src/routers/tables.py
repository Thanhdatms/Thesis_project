from datetime import datetime
from decimal import Decimal
import os
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
import httpx
from pydantic import BaseModel
from graph import app as langgraph_app
from services.database import Database
router = APIRouter(prefix="/tables", tags=["tables"])

@router.get("")
async def get_list_tables(request: Request):
    try:
        url = f"https://console.neon.tech/api/v2/projects/{os.getenv("NEON_PROJECT_ID")}/branches/{os.getenv("NEON_BRANCH_ID")}/schema?db_name={os.getenv("NEON_DB_NAME")}&format=json"
        
        headers = {
            "Authorization": f"Bearer {os.getenv("NEON_API_KEY")}",
            "Content-Type": "application/json"
        } 
        async with httpx.AsyncClient() as client:
            result = await client.get(url, headers=headers)
        
            if result.status_code != 200:
                raise HTTPException(status_code=result.status_code, detail="Failed to fetch tables from Neon database")
            
            schemas = result.json().get("json", {})
            tables = [table for table in schemas.get("tables", []) if table.get("schema") == "public"]
            
            return JSONResponse(
                status_code=200,
                content={"tables": tables}
            )
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )
        
@router.get("/{table_name}")
async def get_table_schema(table_name: str, request: Request):
    try:
        db_pool = Database.pool
        async with db_pool.acquire() as conn:            
            # Fetch table data
            data_query = f"SELECT * FROM {table_name} LIMIT 100;"
            data_rows = await conn.fetch(data_query)
            print(data_rows)
            def convert_row(row):
                converted = {}
                for key, value in dict(row).items():
                    if isinstance(value, datetime):
                        converted[key] = value.isoformat()
                    elif isinstance(value, Decimal):
                        converted[key] = float(value)
                    else:
                        converted[key] = value
                return converted

            data = [convert_row(row) for row in data_rows]
            return JSONResponse(
                status_code=200,
                content={
                    "data": data
                }
            )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        ) 