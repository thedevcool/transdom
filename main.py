from fastapi import FastAPI
from contextlib import asynccontextmanager
from database import connect_to_mongo, close_mongo_connection
from routes import router

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage app startup and shutdown"""
    await connect_to_mongo()
    yield
    await close_mongo_connection()

app = FastAPI(
    title="Transdom API",
    description="Shipping rates and pricing API",
    version="1.0.0",
    lifespan=lifespan
)

@app.get("/")
def read_root():
    """Health check endpoint"""
    return {"status": "ok", "message": "Transdom API is running"}

# Include routes
app.include_router(router)


