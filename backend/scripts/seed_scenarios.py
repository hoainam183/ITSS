"""
Seed script for conversation scenarios
Run: python -m scripts.seed_scenarios
"""

import asyncio
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.mongodb import init_db
from app.models.education import ConversationScenario


# ============================================
# SCENARIO DATA (5 scenarios)
# ============================================

SCENARIOS = [
    {
        "title": "授業に遅刻した理由を伝える練習",
        "description": "ベトナム人生徒が遅刻した理由を日本人教師と共有し、表現をサポートするシナリオ。生徒は言葉が出てこなくて困っている状況です。",
        "difficulty": "easy",
        "category": "classroom",
        "initial_message": "生徒: 先生…すみません。さっき呼ばれたのに、どう言えばいいか分からなくて…。",
    },
    {
        "title": "授業内容が分からないときの伝え方",
        "description": "分からない部分を率直に伝え、先生がフォローする会話パターンを練習します。生徒は迷惑をかけたくないと思っています。",
        "difficulty": "medium",
        "category": "academic",
        "initial_message": "生徒: あの…先生、さっきのところがちょっとよく分からなくて…。迷惑じゃないですか？",
    },
    {
        "title": "学校を休みたい時の相談",
        "description": "体調や家庭の事情で学校を休みたい時、どう先生に伝えるかを練習します。生徒は言いにくそうにしています。",
        "difficulty": "medium",
        "category": "classroom",
        "initial_message": "生徒: 先生、あの…ちょっと相談があるんですけど…。明日のこと、なんですが…。",
    },
    {
        "title": "クラスメートとの問題を相談",
        "description": "クラスメートとのトラブルや人間関係の悩みを先生に相談するシナリオ。生徒は誰にも言えずに悩んでいます。",
        "difficulty": "hard",
        "category": "classroom",
        "initial_message": "生徒: 先生…あの…誰にも言ってないんですけど…。最近、クラスでちょっと…。",
    },
    {
        "title": "家庭の問題を相談",
        "description": "家庭の事情や悩みを信頼できる先生に打ち明けるシナリオ。非常にデリケートな話題なので、慎重な対応が求められます。",
        "difficulty": "hard",
        "category": "personal",
        "initial_message": "生徒: 先生、今日…少し話を聞いてもらえますか？家のことで…ちょっと…。",
    },
]


async def seed_scenarios():
    """Seed conversation scenarios to database"""
    print("🔄 Connecting to database...")
    await init_db()
    
    # Check if scenarios already exist
    existing_count = await ConversationScenario.count()
    if existing_count > 0:
        print(f"⚠️  Found {existing_count} existing scenarios.")
        user_input = input("Do you want to delete and re-seed? (y/N): ")
        if user_input.lower() != 'y':
            print("❌ Aborted. No changes made.")
            return
        
        # Delete existing scenarios
        await ConversationScenario.delete_all()
        print("🗑️  Deleted existing scenarios.")
    
    # Insert new scenarios
    print(f"📝 Inserting {len(SCENARIOS)} scenarios...")
    
    for i, scenario_data in enumerate(SCENARIOS, 1):
        scenario = ConversationScenario(**scenario_data)
        await scenario.insert()
        print(f"   ✅ [{i}/{len(SCENARIOS)}] {scenario_data['title']}")
    
    print(f"\n🎉 Successfully seeded {len(SCENARIOS)} scenarios!")
    
    # Verify
    total = await ConversationScenario.count()
    print(f"📊 Total scenarios in database: {total}")


async def list_scenarios():
    """List all scenarios in database"""
    print("🔄 Connecting to database...")
    await init_db()
    
    scenarios = await ConversationScenario.find_all().to_list()
    
    if not scenarios:
        print("❌ No scenarios found in database.")
        return
    
    print(f"\n📋 Found {len(scenarios)} scenarios:\n")
    print("-" * 60)
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"{i}. {scenario.title}")
        print(f"   ID: {scenario.id}")
        print(f"   Difficulty: {scenario.difficulty}")
        print(f"   Category: {scenario.category}")
        print(f"   Initial: {scenario.initial_message[:50]}...")
        print("-" * 60)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Seed conversation scenarios")
    parser.add_argument("--list", action="store_true", help="List existing scenarios")
    args = parser.parse_args()
    
    if args.list:
        asyncio.run(list_scenarios())
    else:
        asyncio.run(seed_scenarios())

