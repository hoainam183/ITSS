"""
Large-scale seed script for Community Board
- Creates multiple users (10-15 teachers + 1 admin)
- Creates many posts (30-50 posts)
- Creates many comments and replies distributed across posts
- Perfect for testing pagination, search, filtering, and performance

Run: python -m scripts.seed_community_large
Run with clear: python -m scripts.seed_community_large --clear
"""

import asyncio
import sys
import os
import random

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime, timedelta
from app.db.mongodb import init_db
from app.models.users import User, UserProfile
from app.models.community import CommunityPost, Comment, Upvote
from app.core.security import get_password_hash


# ============================================
# SEED USERS DATA
# ============================================

TEACHER_USERS = [
    {
        "username": "tanaka_sensei",
        "email": "tanaka@school.com",
        "password": "password123",
        "role": "teacher",
        "profile": {
            "full_name": "田中太郎",
            "school": "ハノイ日本人学校",
            "experience": 5,
        }
    },
    {
        "username": "yamada_sensei",
        "email": "yamada@school.com",
        "password": "password123",
        "role": "teacher",
        "profile": {
            "full_name": "山田花子",
            "school": "ハノイ日本人学校",
            "experience": 3,
        }
    },
    {
        "username": "suzuki_sensei",
        "email": "suzuki@school.com",
        "password": "password123",
        "role": "teacher",
        "profile": {
            "full_name": "鈴木一郎",
            "school": "ベトナム日本語学校",
            "experience": 7,
        }
    },
    {
        "username": "sato_sensei",
        "email": "sato@school.com",
        "password": "password123",
        "role": "teacher",
        "profile": {
            "full_name": "佐藤美咲",
            "school": "ハノイ日本人学校",
            "experience": 2,
        }
    },
    {
        "username": "watanabe_sensei",
        "email": "watanabe@school.com",
        "password": "password123",
        "role": "teacher",
        "profile": {
            "full_name": "渡辺健",
            "school": "ハノイ日本語センター",
            "experience": 4,
        }
    },
    {
        "username": "ito_sensei",
        "email": "ito@school.com",
        "password": "password123",
        "role": "teacher",
        "profile": {
            "full_name": "伊藤由美",
            "school": "ハノイ日本人学校",
            "experience": 6,
        }
    },
    {
        "username": "kobayashi_sensei",
        "email": "kobayashi@school.com",
        "password": "password123",
        "role": "teacher",
        "profile": {
            "full_name": "小林正",
            "school": "ベトナム日本語学校",
            "experience": 8,
        }
    },
    {
        "username": "kato_sensei",
        "email": "kato@school.com",
        "password": "password123",
        "role": "teacher",
        "profile": {
            "full_name": "加藤愛",
            "school": "ハノイ日本人学校",
            "experience": 1,
        }
    },
    {
        "username": "yoshida_sensei",
        "email": "yoshida@school.com",
        "password": "password123",
        "role": "teacher",
        "profile": {
            "full_name": "吉田雄一",
            "school": "ハノイ日本語センター",
            "experience": 9,
        }
    },
    {
        "username": "matsumoto_sensei",
        "email": "matsumoto@school.com",
        "password": "password123",
        "role": "teacher",
        "profile": {
            "full_name": "松本さくら",
            "school": "ハノイ日本人学校",
            "experience": 3,
        }
    },
    {
        "username": "inoue_sensei",
        "email": "inoue@school.com",
        "password": "password123",
        "role": "teacher",
        "profile": {
            "full_name": "井上大輔",
            "school": "ベトナム日本語学校",
            "experience": 5,
        }
    },
    {
        "username": "kimura_sensei",
        "email": "kimura@school.com",
        "password": "password123",
        "role": "teacher",
        "profile": {
            "full_name": "木村麻衣",
            "school": "ハノイ日本人学校",
            "experience": 4,
        }
    },
    {
        "username": "hayashi_sensei",
        "email": "hayashi@school.com",
        "password": "password123",
        "role": "teacher",
        "profile": {
            "full_name": "林健太",
            "school": "ハノイ日本語センター",
            "experience": 6,
        }
    },
    {
        "username": "shimizu_sensei",
        "email": "shimizu@school.com",
        "password": "password123",
        "role": "teacher",
        "profile": {
            "full_name": "清水優子",
            "school": "ハノイ日本人学校",
            "experience": 2,
        }
    },
]

ADMIN_USER = {
    "username": "admin",
    "email": "admin@school.com",
    "password": "admin123",
    "role": "admin",
    "profile": {
        "full_name": "管理者",
        "school": "システム管理者",
        "experience": 10,
    }
}


# ============================================
# SAMPLE POSTS DATA (Expanded)
# ============================================

POST_TITLES_AND_CONTENT = [
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
    {
        "title": "宿題を提出しない学生への対応",
        "content": """クラスに宿題を提出しない学生が数人います。
注意しても改善されず、困っています。

ベトナムの学生は宿題の概念が日本と少し違うと聞きました。
どのように対応すれば良いでしょうか？""",
        "tags": ["相談", "宿題", "生徒指導"],
    },
    {
        "title": "JLPT対策の授業で使えるゲーム",
        "content": """JLPT対策の授業が少し堅苦しくなってきたので、
ゲームを取り入れたいと思っています。

おすすめのゲームやアクティビティがあれば教えてください！
特にN4、N5レベルの学生向けのものが知りたいです。""",
        "tags": ["授業", "JLPT", "ゲーム", "アクティビティ"],
    },
    {
        "title": "学生が積極的に発言しない",
        "content": """授業中、質問しても誰も手を挙げません。
「わかりますか？」と聞いても「はい」としか答えません。

もっと学生が積極的に発言するようになる方法はありますか？""",
        "tags": ["相談", "授業", "発言"],
    },
    {
        "title": "ベトナム語ができないので不安",
        "content": """ベトナムに来てまだ1ヶ月ですが、ベトナム語が全くできません。
学生とのコミュニケーションで困ることがあります。

ベトナム語を勉強した方が良いでしょうか？
それとも日本語だけで授業を進めるべきでしょうか？""",
        "tags": ["相談", "ベトナム語", "コミュニケーション"],
    },
    {
        "title": "作文の添削に時間がかかりすぎる",
        "content": """学生の作文を添削するのに1人30分以上かかってしまいます。
クラスに20人いるので、全員分を添削するのに10時間以上かかります。

効率的な添削方法があれば教えてください。""",
        "tags": ["相談", "作文", "添削", "効率化"],
    },
    {
        "title": "学生の名前を覚えるコツ",
        "content": """新しいクラスが始まりましたが、学生の名前がなかなか覚えられません。
特にベトナムの名前は発音が難しく...

名前を早く覚えるコツがあれば教えてください！""",
        "tags": ["相談", "名前", "クラス管理"],
    },
    {
        "title": "オンライン授業のコツ",
        "content": """来週からオンライン授業を始めることになりました。
対面授業とは違う難しさがあると思います。

オンライン授業で気をつけるべきポイントや
おすすめのツールがあれば教えてください！""",
        "tags": ["相談", "オンライン", "授業", "ツール"],
    },
    {
        "title": "学生がスマホを授業中に使う",
        "content": """授業中にスマホをいじっている学生がいます。
注意してもすぐにまた使ってしまいます。

スマホの使用をどう管理すれば良いでしょうか？""",
        "tags": ["相談", "スマホ", "授業", "管理"],
    },
    {
        "title": "日本語能力の差が大きいクラス",
        "content": """クラス内で日本語能力の差が大きく、授業の進め方に困っています。
上級者には物足りなく、初心者には難しすぎる...

このようなクラスをどう運営すれば良いでしょうか？""",
        "tags": ["相談", "クラス運営", "レベル差"],
    },
    {
        "title": "学生が質問に来ない",
        "content": """「わからないことがあったら質問に来てください」と言っても、
誰も質問に来ません。

学生が質問しやすい環境を作るにはどうすれば良いでしょうか？""",
        "tags": ["相談", "質問", "コミュニケーション"],
    },
    {
        "title": "ベトナムの祝日について",
        "content": """ベトナムの祝日が多くて、授業スケジュールが立てにくいです。
主要な祝日を教えてください。

また、祝日が近づくと学生の集中力が落ちる気がします。
皆さんはどう対応されていますか？""",
        "tags": ["相談", "祝日", "スケジュール"],
    },
    {
        "title": "学生のモチベーションを上げる方法",
        "content": """最近、学生のモチベーションが下がっている気がします。
特に中級レベルで伸び悩んでいる学生が多いです。

モチベーションを上げる良い方法があれば教えてください！""",
        "tags": ["相談", "モチベーション", "中級"],
    },
    {
        "title": "発音指導のコツ",
        "content": """学生の発音を直したいのですが、どう指導すれば良いかわかりません。
特に「つ」「ふ」「らりるれろ」の発音が難しいようです。

発音指導のコツや練習方法があれば教えてください！""",
        "tags": ["相談", "発音", "指導"],
    },
    {
        "title": "期末試験の問題作成",
        "content": """期末試験の問題を作成することになりました。
バランスの良い問題を作るにはどうすれば良いでしょうか？

また、過去に使った問題で良かったものがあれば共有してください！""",
        "tags": ["相談", "試験", "問題作成"],
    },
    {
        "title": "学生との距離感",
        "content": """学生と親しくなりすぎて、授業中に集中してくれなくなりました。
でも、厳しくしすぎると学生が離れていく気がします...

適切な距離感を保つコツがあれば教えてください。""",
        "tags": ["相談", "距離感", "クラス運営"],
    },
    {
        "title": "日本語学習アプリの紹介",
        "content": """学生に日本語学習アプリを紹介したいのですが、
おすすめのアプリがあれば教えてください！

特に無料で使えるものが良いです。""",
        "tags": ["リソース", "アプリ", "学習"],
    },
    {
        "title": "学生のプレゼンテーション評価",
        "content": """学生のプレゼンテーションを評価することになりました。
どのような観点で評価すれば良いでしょうか？

評価シートのテンプレートがあれば共有してください！""",
        "tags": ["相談", "プレゼン", "評価"],
    },
    {
        "title": "クラス内のグループ分け",
        "content": """グループワークをする際、どうグループ分けすれば良いでしょうか？
能力別？それともランダム？

効果的なグループ分けの方法があれば教えてください！""",
        "tags": ["相談", "グループワーク", "クラス運営"],
    },
    {
        "title": "学生の宿題チェック方法",
        "content": """宿題をチェックするのに時間がかかりすぎます。
効率的なチェック方法があれば教えてください。

また、宿題を提出しない学生への対応も悩んでいます。""",
        "tags": ["相談", "宿題", "チェック", "効率化"],
    },
    {
        "title": "日本語の敬語指導",
        "content": """学生に敬語を教えるのが難しいです。
特に「です・ます」と「だ・である」の使い分けが...

敬語指導のコツや練習方法があれば教えてください！""",
        "tags": ["相談", "敬語", "指導"],
    },
    {
        "title": "学生の作文を発表させる方法",
        "content": """学生の作文をクラスで発表させたいのですが、
恥ずかしがって発表したがりません。

発表しやすい環境を作るにはどうすれば良いでしょうか？""",
        "tags": ["相談", "作文", "発表"],
    },
    {
        "title": "授業の準備時間を短縮したい",
        "content": """毎日の授業準備に時間がかかりすぎます。
効率的な準備方法があれば教えてください。

また、使えるテンプレートがあれば共有してください！""",
        "tags": ["相談", "準備", "効率化"],
    },
    {
        "title": "学生のリスニング力を上げる方法",
        "content": """学生のリスニング力がなかなか上がりません。
効果的なリスニング練習方法があれば教えてください！

おすすめの教材もあれば教えてください。""",
        "tags": ["相談", "リスニング", "練習"],
    },
    {
        "title": "クラス内のいじめ対応",
        "content": """クラス内でいじめのような行動が見られます。
どう対応すれば良いでしょうか？

ベトナムの文化を考慮した対応方法があれば教えてください。""",
        "tags": ["相談", "いじめ", "対応"],
    },
    {
        "title": "学生の読解力を上げる方法",
        "content": """学生の読解力がなかなか上がりません。
効果的な読解練習方法があれば教えてください！

おすすめの読解教材もあれば教えてください。""",
        "tags": ["相談", "読解", "練習"],
    },
    {
        "title": "学生の会話力を上げる方法",
        "content": """学生の会話力がなかなか上がりません。
特に自然な会話ができるようになりたいです。

効果的な会話練習方法があれば教えてください！""",
        "tags": ["相談", "会話", "練習"],
    },
    {
        "title": "学生の漢字学習をサポートする方法",
        "content": """学生が漢字を覚えるのに苦労しています。
効果的な漢字学習方法があれば教えてください！

おすすめの漢字教材もあれば教えてください。""",
        "tags": ["相談", "漢字", "学習"],
    },
    {
        "title": "学生の文法理解を深める方法",
        "content": """学生が文法を理解しているようでも、実際に使えないことがあります。
文法の理解を深める方法があれば教えてください！""",
        "tags": ["相談", "文法", "理解"],
    },
    {
        "title": "学生の語彙力を増やす方法",
        "content": """学生の語彙力がなかなか増えません。
効果的な語彙学習方法があれば教えてください！

おすすめの語彙教材もあれば教えてください。""",
        "tags": ["相談", "語彙", "学習"],
    },
]

COMMENT_TEMPLATES = [
    "とても参考になりました！",
    "私も同じ経験があります。",
    "良いアイデアですね！",
    "早速試してみます。",
    "ありがとうございます！",
    "私のクラスでも同じ問題があります。",
    "とても助かります！",
    "他の方法も試してみたいです。",
    "学生の反応はどうでしたか？",
    "私も同じように感じています。",
    "良いアドバイスをありがとうございます！",
    "参考にさせていただきます。",
    "私の経験では...",
    "そうですね、確かにその通りです。",
    "他にも良い方法があれば教えてください。",
]

REPLY_TEMPLATES = [
    "私も同じ方法を試しましたが、効果がありました！",
    "良いアイデアですね！",
    "学生の反応はどうでしたか？",
    "私のクラスでも試してみます。",
    "ありがとうございます！",
    "とても参考になります。",
    "他にも良い方法があれば教えてください。",
    "私も同じように感じています。",
]


# ============================================
# HELPER FUNCTIONS
# ============================================

async def create_users():
    """Create multiple users for seeding"""
    await init_db()
    
    users = []
    
    # Create admin user
    admin = await User.find_one({"email": ADMIN_USER["email"]})
    if not admin:
        profile = UserProfile(**ADMIN_USER["profile"])
        admin = User(
            username=ADMIN_USER["username"],
            email=ADMIN_USER["email"],
            password=get_password_hash(ADMIN_USER["password"]),
            role=ADMIN_USER["role"],
            profile=profile,
        )
        await admin.insert()
        print(f"✅ Created admin user: {admin.username}")
    else:
        print(f"✅ Using existing admin user: {admin.username}")
    users.append(admin)
    
    # Create teacher users
    for user_data in TEACHER_USERS:
        existing = await User.find_one({"email": user_data["email"]})
        if not existing:
            profile = UserProfile(**user_data["profile"])
            user = User(
                username=user_data["username"],
                email=user_data["email"],
                password=get_password_hash(user_data["password"]),
                role=user_data["role"],
                profile=profile,
            )
            await user.insert()
            print(f"✅ Created user: {user.username}")
        else:
            user = existing
            print(f"✅ Using existing user: {user.username}")
        users.append(user)
    
    print(f"\n📊 Total users: {len(users)} (1 admin + {len(users)-1} teachers)")
    return users


async def create_posts(users):
    """Create many posts with random authors"""
    existing_count = await CommunityPost.find_all().count()
    if existing_count > 0:
        print(f"⚠️  Found {existing_count} existing posts. Skipping post creation.")
        posts = await CommunityPost.find_all().sort("+created_at").to_list()
        return posts
    
    print(f"\n📝 Creating {len(POST_TITLES_AND_CONTENT)} posts...")
    posts = []
    
    for i, post_data in enumerate(POST_TITLES_AND_CONTENT):
        # Random author (exclude admin for most posts)
        author = random.choice(users[1:]) if not post_data.get("is_pinned") else users[0]  # Admin pins announcement
        
        # Vary created_at dates (spread over last 30 days)
        days_ago = random.randint(0, 30)
        hours_ago = random.randint(0, 23)
        created_at = datetime.now() - timedelta(days=days_ago, hours=hours_ago)
        
        post = CommunityPost(
            author_id=author.id,
            title=post_data["title"],
            content=post_data["content"],
            tags=post_data["tags"],
            is_pinned=post_data.get("is_pinned", False),
            views=random.randint(10, 200),
            upvotes=random.randint(0, 50),
            created_at=created_at,
            updated_at=created_at,
            last_activity=created_at + timedelta(hours=random.randint(0, 5)),
        )
        post.excerpt = post.generate_excerpt()
        await post.insert()
        posts.append(post)
        
        if (i + 1) % 10 == 0:
            print(f"   Created {i + 1}/{len(POST_TITLES_AND_CONTENT)} posts...")
    
    print(f"✅ Created {len(posts)} posts")
    return posts


async def create_comments(posts, users):
    """Create many comments and replies distributed across posts"""
    existing_count = await Comment.find_all().count()
    if existing_count > 0:
        print(f"⚠️  Found {existing_count} existing comments. Skipping comment creation.")
        return
    
    print(f"\n💬 Creating comments and replies...")
    
    total_comments = 0
    
    # Create comments for each post (random number of comments per post)
    for post in posts:
        # Random number of root comments (2-8 per post)
        num_root_comments = random.randint(2, 8)
        
        for _ in range(num_root_comments):
            # Random author
            author = random.choice(users)
            
            # Random comment content
            comment_content = random.choice(COMMENT_TEMPLATES)
            if random.random() > 0.5:  # 50% chance to add more text
                comment_content += " " + random.choice(COMMENT_TEMPLATES)
            
            # Random created_at (within post's timeframe)
            hours_after_post = random.randint(1, 48)
            comment_created_at = post.created_at + timedelta(hours=hours_after_post)
            
            # Create root comment
            root_comment = Comment(
                post_id=post.id,
                author_id=author.id,
                content=comment_content,
                depth=0,
                upvotes=random.randint(0, 10),
                created_at=comment_created_at,
                updated_at=comment_created_at,
            )
            await root_comment.insert()
            total_comments += 1
            
            # Create replies (0-3 replies per root comment)
            num_replies = random.randint(0, 3)
            for _ in range(num_replies):
                reply_author = random.choice(users)
                reply_content = random.choice(REPLY_TEMPLATES)
                
                hours_after_comment = random.randint(1, 24)
                reply_created_at = comment_created_at + timedelta(hours=hours_after_comment)
                
                reply = Comment(
                    post_id=post.id,
                    author_id=reply_author.id,
                    content=reply_content,
                    parent_comment_id=root_comment.id,
                    depth=1,
                    upvotes=random.randint(0, 5),
                    created_at=reply_created_at,
                    updated_at=reply_created_at,
                )
                await reply.insert()
                total_comments += 1
            
            # Update post comment count
            post.comment_count += 1 + num_replies
        
        # Update post's last_activity to latest comment
        latest_comment = await Comment.find({"postId": post.id}).sort("-createdAt").first()
        if latest_comment:
            post.last_activity = latest_comment.created_at
        
        await post.save()
    
    print(f"✅ Created {total_comments} comments (including replies)")


async def create_upvotes(posts, users):
    """Create random upvotes for posts and comments"""
    existing_count = await Upvote.find_all().count()
    if existing_count > 0:
        print(f"⚠️  Found {existing_count} existing upvotes. Skipping upvote creation.")
        return
    
    print(f"\n👍 Creating upvotes...")
    
    total_upvotes = 0
    
    # Upvote posts
    for post in posts:
        # Random number of users who upvoted (0 to 70% of users)
        num_upvoters = random.randint(0, int(len(users) * 0.7))
        upvoters = random.sample(users, min(num_upvoters, len(users)))
        
        for user in upvoters:
            upvote = Upvote(
                user_id=user.id,
                target_type="post",
                target_id=post.id,
            )
            await upvote.insert()
            total_upvotes += 1
        
        # Update post upvote count
        post.upvotes = len(upvoters)
        await post.save()
    
    # Upvote comments
    comments = await Comment.find_all().to_list()
    for comment in comments:
        # Random number of users who upvoted (0 to 50% of users)
        num_upvoters = random.randint(0, int(len(users) * 0.5))
        upvoters = random.sample(users, min(num_upvoters, len(users)))
        
        for user in upvoters:
            upvote = Upvote(
                user_id=user.id,
                target_type="comment",
                target_id=comment.id,
            )
            await upvote.insert()
            total_upvotes += 1
        
        # Update comment upvote count
        comment.upvotes = len(upvoters)
        await comment.save()
    
    print(f"✅ Created {total_upvotes} upvotes")


async def seed_large_community():
    """Main seeding function"""
    print("🌱 Starting Large-Scale Community Board Seed...")
    print("=" * 60)
    
    # Create users
    users = await create_users()
    
    # Create posts
    posts = await create_posts(users)
    
    # Create comments
    await create_comments(posts, users)
    
    # Create upvotes
    await create_upvotes(posts, users)
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 SEED SUMMARY")
    print("=" * 60)
    print(f"Users: {len(users)} (1 admin + {len(users)-1} teachers)")
    print(f"Posts: {len(posts)}")
    comment_count = await Comment.find_all().count()
    print(f"Comments: {comment_count}")
    upvote_count = await Upvote.find_all().count()
    print(f"Upvotes: {upvote_count}")
    print("\n✅ All users have password: password123")
    print("✅ Admin user: admin@school.com / admin123")
    print("\n🎉 Large-scale seed completed!")


async def clear_all_data():
    """Clear all community and user data"""
    await init_db()
    
    print("🗑️  Clearing all data...")
    
    upvote_count = await Upvote.find_all().count()
    await Upvote.find_all().delete()
    print(f"   Deleted {upvote_count} upvotes")
    
    comment_count = await Comment.find_all().count()
    await Comment.find_all().delete()
    print(f"   Deleted {comment_count} comments")
    
    post_count = await CommunityPost.find_all().count()
    await CommunityPost.find_all().delete()
    print(f"   Deleted {post_count} posts")
    
    # Optionally delete users (commented out to keep auth users)
    # user_count = await User.find_all().count()
    # await User.find_all().delete()
    # print(f"   Deleted {user_count} users")
    
    print("✅ All community data cleared!")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--clear":
        asyncio.run(clear_all_data())
    else:
        asyncio.run(seed_large_community())

