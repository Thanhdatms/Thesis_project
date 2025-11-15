import asyncpg
import time

class Database:
    pool: asyncpg.Pool | None = None

    @classmethod
    async def connect(cls, dsn: str):
        cls.pool = await asyncpg.create_pool(dsn)
        print("Database pool created")

    @classmethod
    async def close(cls):
        if cls.pool:
            await cls.pool.close()
            print("Database pool closed")

    @classmethod
    async def fetch(cls, query: str):
        start_time = time.time()
        print(f"Executing query: {query}")
        try:
            if not cls.pool:
                raise RuntimeError("Database not connected")
            async with cls.pool.acquire() as conn:
                result = await conn.fetch(query)
                print(f"Query execution time: {time.time() - start_time:.3f} seconds")
                return result
        except Exception as e:
            print(f"SQL error: {e}")
            await conn.rollback()
            raise e
