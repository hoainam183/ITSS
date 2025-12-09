from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware

from app.api.routers import emotion, students, conversation, community
from app.core.config import settings
from app.db.mongodb import init_db


# Hàm xử lý vòng đời ứng dụng (Bật lên thì kết nối DB)
@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(students.router, prefix="/students", tags=["Students"])
app.include_router(emotion.router)
app.include_router(conversation.router)
app.include_router(community.router)


@app.get("/")
async def root():
    return {"message": "Insight Bridge API is running!"}