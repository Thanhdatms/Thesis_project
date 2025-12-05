from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import asyncpg



from routers import chatbot, tables
from services.database import Database

DATABASE_URL = "postgresql://neondb_owner:npg_iuvITr7PNXC0@ep-weathered-boat-a14az5b7-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"


@asynccontextmanager
async def lifespan(app: FastAPI):
    await Database.connect(DATABASE_URL)
    yield
    await Database.close()
    
app = FastAPI(lifespan=lifespan)


origins = [
    "http://localhost",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chatbot.router)
app.include_router(tables.router)