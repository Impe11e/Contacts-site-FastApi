import redis.asyncio as redis

from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from fastapi_limiter import FastAPILimiter

from src.conf.config import settings
from src.routes import contacts, auth, users

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(contacts.router, prefix='/api')
app.include_router(auth.router, prefix='/api')
app.include_router(users.router, prefix='/api')


@app.on_event("startup")
async def startup():
    """
    This function is executed when the application starts.
    It connects to Redis and initializes the FastAPI Limiter for rate-limiting.
    """
    try:
        r = await redis.Redis(host=settings.redis_host, port=settings.redis_port, db=0, encoding="utf-8",
                              decode_responses=True)
        await FastAPILimiter.init(r)
    except Exception as e:
        print(f"Error connecting to Redis: {e}")
        raise e

@app.get("/")
def read_root():
    """
    A simple root endpoint to test if the API is working correctly.
    Returns a simple message.
    """
    return {"message": "Hello World"}
