import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI

from src.db.sessions import POOL
from src.api.routers import user_router, token_router, account_router, fake_data_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        yield
    finally:
        await POOL.close()


app = FastAPI(title="FastAPI with SQLAlchemy Async", lifespan=lifespan)

app.include_router(user_router)
app.include_router(fake_data_router)
app.include_router(account_router)
app.include_router(token_router)

def main():
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)

if __name__ == "__main__":
    main()
