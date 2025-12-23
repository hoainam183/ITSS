"""
Seed script for Community Board
- Creates a mock user (teacher)
- Creates sample posts with tags
- Creates a pinned announcement post

Run: python -m scripts.seed_community
"""

import asyncio
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime, timedelta
from app.db.mongodb import init_db
from app.models.users import User, UserProfile
from app.models.community import CommunityPost, Comment
from app.core.security import get_password_hash


# ============================================
# SEED USER DATA
# ============================================

SEED_USER_DATA = {
    "username": "tanaka_sensei",
    "email": "tanaka@school.com",
    "password": "password123",  # Will be hashed
    "role": "teacher",
    "profile": {
        "full_name": "田中先生",
        "school": "ハノイ日本人学校",
        "experience": 5,
        "avatar": None,
    }
}


# ============================================
# SAMPLE POSTS DATA
# ============================================

SAMPLE_POSTS = [
    {
        "title": "📢 コミュニティ掲示板へようこそ！",
        "content": """皆さん、コミュニティ掲示板へようこそ！

このスペースは、ハノイで働く日本人教師の皆さんが経験や知識を共有するための場所です。

【ルール】
1. 互いを尊重しましょう
2. 建設的なフィードバックを心がけましょう
3. 個人情報は共有しないでください
4. 質問は具体的に書きましょう

何か困ったことがあれば、遠慮なく投稿してください！""",
        "tags": ["お知らせ", "ルール"],
        "is_pinned": True,
    },
    {
        "title": "ベトナム人学生との効果的なコミュニケーション方法",
        "content": """3年間ハノイで教えてきた経験から、いくつかのポイントを共有します。

1. **間接的な表現を理解する**
ベトナムの学生は直接「わかりません」と言いにくいことがあります。
「ちょっと難しいです」＝「全然わかりません」の場合も。

2. **グループワークを活用**
個人で発言するより、グループで話し合ってから発表する方が
学生は安心して意見を言えます。

3. **褒めることを忘れずに**
小さな進歩でも褒めると、学生のモチベーションが上がります。

皆さんの経験も聞かせてください！""",
        "tags": ["コミュニケーション", "経験共有", "ヒント"],
    },
    {
        "title": "文化の違いで困った経験はありますか？",
        "content": """先日、授業中に学生が急に黙ってしまうことがありました。
理由を聞いても「大丈夫です」としか言わず...

後から他の先生に聞いたら、私の質問の仕方が
学生にとってプレッシャーだったようです。

同じような経験をされた方、どう対処されましたか？
アドバイスをいただけると嬉しいです。""",
        "tags": ["質問", "文化", "相談"],
    },
    {
        "title": "授業で使える日本文化紹介のアイデア",
        "content": """来月、日本文化を紹介する授業をする予定です。
今考えているのは：

- お正月の伝統（年賀状、おせち料理）
- 日本の学校生活（部活、文化祭）
- 和食文化

他にベトナムの学生が興味を持ちそうなトピックはありますか？
過去にやってみて反応が良かったものがあれば教えてください！""",
        "tags": ["授業", "日本文化", "アイデア"],
    },
    {
        "title": "学生の遅刻への対応について",
        "content": """最近、同じ学生が何度も遅刻しています。
理由を聞くと毎回「バスが遅れた」と言うのですが...

日本式に厳しく対応すべきか、
ベトナムの文化を考慮して柔軟に対応すべきか迷っています。

皆さんはどのように対応されていますか？""",
        "tags": ["相談", "生徒指導", "遅刻"],
    },
    {
        "title": "おすすめの教材・リソース共有",
        "content": """日本語教育に役立つリソースをいくつか見つけたので共有します：

1. **NHK World - やさしい日本語ニュース**
   https://www3.nhk.or.jp/news/easy/

2. **みんなの日本語 オンライン練習**
   初級〜中級の文法練習に最適

3. **YouTube - 日本語の森**
   JLPT対策に使えます

他におすすめがあれば、ぜひコメントで教えてください！""",
        "tags": ["リソース", "教材", "共有"],
    },
]


async def get_or_create_seed_user():
    """Get existing user or create one for seeding"""
    # Try to get first user in database
    user = await User.find_one()
    if user:
        print(f"✅ Using existing user: {user.username} ({user.email})")
        print(f"   User ID: {user.id}")
        return user
    
    # Create new user for seeding
    print("📝 Creating seed user...")
    profile = UserProfile(**SEED_USER_DATA["profile"])
    
    new_user = User(
        username=SEED_USER_DATA["username"],
        email=SEED_USER_DATA["email"],
        password=get_password_hash(SEED_USER_DATA["password"]),  # Hash password properly
        role=SEED_USER_DATA["role"],
        profile=profile,
    )
    await new_user.insert()
    print(f"✅ Created seed user: {new_user.username} ({new_user.email})")
    print(f"   User ID: {new_user.id}")
    print(f"   Password: {SEED_USER_DATA['password']} (for testing)")
    return new_user


async def seed_community():
    """Seed community data"""
    print("🌱 Starting Community Board seed...")
    
    # Initialize database
    await init_db()
    
    # Get or create seed user
    user = await get_or_create_seed_user()
    
    # Check existing posts
    existing_posts = await CommunityPost.find_all().count()
    if existing_posts > 0:
        print(f"⚠️  Found {existing_posts} existing posts. Skipping post creation.")
        
        # Still try to seed comments for existing posts
        posts = await CommunityPost.find_all().to_list()
        await seed_comments(user.id, posts)
        print("\n🎉 Community Board seed completed!")
        return
    
    # Create sample posts
    print("📝 Creating sample posts...")
    
    for i, post_data in enumerate(SAMPLE_POSTS):
        # Vary the created_at dates for realistic sorting
        created_at = datetime.now() - timedelta(days=len(SAMPLE_POSTS) - i, hours=i * 2)
        
        post = CommunityPost(
            author_id=user.id,
            title=post_data["title"],
            content=post_data["content"],
            tags=post_data["tags"],
            is_pinned=post_data.get("is_pinned", False),
            views=i * 5,  # Some initial views
            upvotes=i * 2,  # Some initial upvotes
            created_at=created_at,
            updated_at=created_at,
            last_activity=created_at,
        )
        post.excerpt = post.generate_excerpt()
        await post.insert()
        
        status = "📌 PINNED" if post.is_pinned else f"   #{i+1}"
        print(f"   {status}: {post.title[:40]}...")
    
    print(f"\n✅ Created {len(SAMPLE_POSTS)} sample posts")
    
    # Store post IDs for comments (sorted by created_at to match seed order)
    posts = await CommunityPost.find_all().sort("+created_at").to_list()
    
    # Create sample comments
    await seed_comments(user.id, posts)
    
    print("\n🎉 Community Board seed completed!")


# ============================================
# SAMPLE COMMENTS DATA
# ============================================

SAMPLE_COMMENTS = [
    # Comments for post about communication (index 1, not pinned)
    {
        "post_index": 1,  # "ベトナム人学生との効果的なコミュニケーション方法"
        "comments": [
            {
                "content": "とても参考になりました！特にグループワークのアドバイスは早速試してみます。",
                "replies": [
                    "私も同じ方法を試しましたが、効果がありました！",
                    "@田中先生 良かったです！結果を教えてください。",
                ]
            },
            {
                "content": "3年間の経験を共有していただきありがとうございます。私はまだ1年目なので、このようなアドバイスはとても助かります。",
                "replies": [
                    "頑張ってください！最初の1年は大変ですが、きっと慣れますよ。",
                ]
            },
        ]
    },
    # Comments for post about cultural differences (index 2)
    {
        "post_index": 2,  # "文化の違いで困った経験はありますか？"
        "comments": [
            {
                "content": "私も同じ経験があります。学生に直接聞くより、授業後に個別に話しかける方が良いかもしれません。",
                "replies": [
                    "そうですね。グループの前で質問されるのは恥ずかしいと感じる学生が多いようです。",
                    "@山田先生 個別に話しかけるのは良いアイデアですね！",
                ]
            },
            {
                "content": "ベトナムの文化では、先生に対して遠慮することが礼儀とされています。それを理解してから、コミュニケーションがスムーズになりました。",
                "replies": []
            },
        ]
    },
    # Comments for post about teaching materials (index 5)
    {
        "post_index": 5,  # "おすすめの教材・リソース共有"
        "comments": [
            {
                "content": "NHK Worldのリンク、ありがとうございます！学生にも紹介しました。",
                "replies": [
                    "学生の反応はどうでしたか？",
                    "私のクラスでは毎週1つのニュースを読む宿題にしています。",
                ]
            },
        ]
    },
]


async def seed_comments(user_id, posts):
    """Seed sample comments and replies"""
    
    # Check existing comments
    existing_comments = await Comment.find_all().count()
    if existing_comments > 0:
        print(f"⚠️  Found {existing_comments} existing comments. Skipping comment creation.")
        return
    
    print("💬 Creating sample comments...")
    
    total_comments = 0
    
    for comment_data in SAMPLE_COMMENTS:
        post_index = comment_data["post_index"]
        if post_index >= len(posts):
            continue
            
        post = posts[post_index]
        
        for root_comment_data in comment_data["comments"]:
            # Create root comment
            root_comment = Comment(
                post_id=post.id,
                author_id=user_id,
                content=root_comment_data["content"],
                depth=0,
                created_at=datetime.now() - timedelta(hours=total_comments + 5),
            )
            await root_comment.insert()
            total_comments += 1
            
            # Create replies
            for reply_content in root_comment_data["replies"]:
                reply = Comment(
                    post_id=post.id,
                    author_id=user_id,
                    content=reply_content,
                    parent_comment_id=root_comment.id,
                    depth=1,
                    created_at=datetime.now() - timedelta(hours=total_comments + 2),
                )
                await reply.insert()
                total_comments += 1
            
            # Update post's comment_count
            reply_count = len(root_comment_data["replies"])
            post.comment_count += 1 + reply_count
        
        await post.save()
    
    print(f"   Created {total_comments} comments (with replies)")


async def clear_community_data():
    """Clear all community data for re-seeding"""
    await init_db()
    
    print("🗑️  Clearing community data...")
    
    # Clear in order (comments first due to foreign key-like relationship)
    from app.models.community import Upvote
    
    upvote_count = await Upvote.find_all().count()
    await Upvote.find_all().delete()
    print(f"   Deleted {upvote_count} upvotes")
    
    comment_count = await Comment.find_all().count()
    await Comment.find_all().delete()
    print(f"   Deleted {comment_count} comments")
    
    post_count = await CommunityPost.find_all().count()
    await CommunityPost.find_all().delete()
    print(f"   Deleted {post_count} posts")
    
    print("✅ Community data cleared!")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--clear":
        asyncio.run(clear_community_data())
    else:
        asyncio.run(seed_community())
