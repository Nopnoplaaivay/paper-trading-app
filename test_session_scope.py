import asyncio
from sqlalchemy import text
from src.db.sessions import backend_session_scope


async def example_usage():
    async with backend_session_scope(new=True) as session:
        result = await session.execute(text("SELECT 42 AS test;"))
        data = result.all()
        print(data)


if __name__ == "__main__":
    asyncio.run(example_usage())