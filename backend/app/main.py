from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.db.mongodb import init_db
from app.core.config import settings
from app.api.routers import students
# Hàm xử lý vòng đời ứng dụng (Bật lên thì kết nối DB)
@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    lifespan=lifespan
)
app.include_router(students.router, prefix="/students", tags=["Students"])

@app.get("/")
async def root():
    return {"message": "Insight Bridge API is running!"}