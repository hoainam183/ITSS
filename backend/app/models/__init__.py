# app/models/__init__.py

from app.models.users import User
from app.models.education import (
    ConversationScenario, 
    ConversationSimulation, 
    MessageAnalysis
)
from app.models.community import (
    CommunityPost, 
    Comment, 
    SystemSetting,
    Upvote
)

# Danh sách này sẽ được dùng ở db/mongodb.py
all_models = [
    User,
    ConversationScenario,
    ConversationSimulation,
    MessageAnalysis,
    CommunityPost,
    Comment,
    SystemSetting,
    Upvote
]