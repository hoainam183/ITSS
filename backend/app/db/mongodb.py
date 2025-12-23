from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from app.core.config import settings
from app.models import all_models


async def init_db():
    try:
        # Tạo client
        client = AsyncIOMotorClient(settings.MONGODB_URL)

        # Lấy tên DB từ URL hoặc đặt cứng
        db_name = "insight_bridge_db"

        # Khởi tạo Beanie
        await init_beanie(database=client[db_name], document_models=all_models)
        print("✅ Đã kết nối MongoDB thành công!")
    except Exception as e:
        print(f"❌ Lỗi kết nối Database: {e}")
