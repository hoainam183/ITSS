export interface ConversationTopic {
  id: string;
  title: string;
  description: string;
  initialMessage: string;
  goals: string[];
}

export interface ScoreBreakdown {
  emotion: number;
  sincerity: number;
  relevance: number;
}

export interface EvaluationResult {
  aiReply: string;
  scores: ScoreBreakdown;
}

type LateRoute = "supportive" | "strict";

interface TopicConversationState {
  step: number;
  route?: LateRoute;
}

const topicStates = new Map<string, TopicConversationState>();

const lateRouteKeywords: Record<LateRoute, string[]> = {
  supportive: ["調べ", "手伝って", "大丈夫", "携帯", "翻訳", "いいですよ", "落ち着"],
  strict: ["毎回", "理由をしっかり", "注意", "早く家", "約束", "厳しく", "遅れています"],
};

const lateRouteReplies: Record<LateRoute, EvaluationResult[]> = {
  supportive: [
    {
      aiReply: "生徒: …携帯で調べてみますね…。『バスが遅れました。本当にすみません。』",
      scores: { emotion: 62, sincerity: 58, relevance: 54 },
    },
    {
      aiReply:
        "生徒: 今度はもっと早めに出られるようにします。待っていてくださってありがとうございます。",
      scores: { emotion: 74, sincerity: 71, relevance: 68 },
    },
  ],
  strict: [
    {
      aiReply: "生徒: うまく言えなくてすみません…。翻訳アプリで書いてみてもいいですか？",
      scores: { emotion: 45, sincerity: 52, relevance: 50 },
    },
    {
      aiReply:
        "生徒: 電車が途中で止まってしまって…本当に申し訳ありません。次はもっと早く家を出ます。",
      scores: { emotion: 58, sincerity: 63, relevance: 60 },
    },
  ],
};

const cannotUnderstandScript: EvaluationResult[] = [
  {
    aiReply:
      "生徒: ありがとうございます…。じゃあ、自分の言葉で説明してみます。「〜てから」は時間の順番…という感じですか？",
    scores: { emotion: 64, sincerity: 60, relevance: 55 },
  },
  {
    aiReply:
      "生徒: あっ、なるほど！「シャワーを浴びてから、学校に行きます。」という言い方は自然ですか？",
    scores: { emotion: 72, sincerity: 70, relevance: 66 },
  },
  {
    aiReply:
      "生徒: よかった…ありがとうございます先生。もう少し練習してもいいですか？他の文も言い換えてみたいです。",
    scores: { emotion: 78, sincerity: 82, relevance: 74 },
  },
  {
    aiReply:
      "生徒: ぜひお願いします！次の文も挑戦してみます。",
    scores: { emotion: 85, sincerity: 88, relevance: 80 },
  },
];

const defaultFallback: EvaluationResult = {
  aiReply: "生徒: 話してくれてありがとう。もう少しゆっくり教えてもらえると助かります。",
  scores: { emotion: 50, sincerity: 55, relevance: 52 },
};

export function resetConversationState(topicId?: string) {
  if (topicId) {
    topicStates.delete(topicId);
  } else {
    topicStates.clear();
  }
}

export async function fetchConversationTopics(): Promise<ConversationTopic[]> {
  // Simulate network latency so skeleton loaders make sense
  await new Promise((resolve) => setTimeout(resolve, 400));

  return [
    {
      id: "late-to-class",
      title: "授業に遅刻した理由を伝える練習",
      description:
        "ベトナム人生徒が遅刻した理由を日本人教師と共有し、表現をサポートするシナリオ",
      initialMessage:
        "生徒: 先生…すみません。さっき呼ばれたのに、どう言えばいいか分からなくて…。",
      goals: [
        "理由を短く・丁寧に伝える練習",
        "教師が支援の言葉をかけつつヒアリングするパターンを体験",
      ],
    },
    {
      id: "cannot-understand",
      title: "授業内容が分からないときの伝え方",
      description:
        "分からない部分を率直に伝え、先生がフォローする会話パターンを練習",
      initialMessage:
        "生徒: あの…先生、さっきのところがちょっとよく分からなくて…。迷惑じゃないですか？",
      goals: [
        "『すみません、よく分かりません』を自然に言えるようにする",
        "先生側が複数の言い換えや選択肢を提示して安心感を与える",
      ],
    },
  ];
}

export async function mockAiReply(
  topicId: string,
  replyText: string,
): Promise<EvaluationResult> {
  await new Promise((resolve) => setTimeout(resolve, 600));

  const handler =
    topicId === "late-to-class"
      ? handleLateToClass
      : topicId === "cannot-understand"
        ? handleCannotUnderstand
        : handleFallback;

  return handler(topicId, replyText);
}

function handleLateToClass(topicId: string, replyText: string): EvaluationResult {
  const state = getState(topicId);

  if (state.step === 0) {
    state.step = 1;
    topicStates.set(topicId, state);
    return {
      aiReply: "生徒: …あの…えっと…言葉が出てこなくて…。",
      scores: { emotion: 40, sincerity: 48, relevance: 42 },
    };
  }

  if (!state.route) {
    state.route = detectLateRoute(replyText);
  }

  const routeReplies = lateRouteReplies[state.route];
  const routeIndex = Math.min(state.step - 1, routeReplies.length - 1);
  const response = routeReplies[routeIndex];

  state.step += 1;
  topicStates.set(topicId, state);
  return response;
}

function detectLateRoute(message: string): LateRoute {
  const normalized = message.trim();

  if (
    lateRouteKeywords.strict.some((keyword) =>
      normalized.includes(keyword),
    )
  ) {
    return "strict";
  }

  if (
    lateRouteKeywords.supportive.some((keyword) =>
      normalized.includes(keyword),
    )
  ) {
    return "supportive";
  }

  // Default to supportive unless explicitly strict
  return "supportive";
}

function handleCannotUnderstand(topicId: string): EvaluationResult {
  const state = getState(topicId);
  const scriptIndex = Math.min(state.step, cannotUnderstandScript.length - 1);
  const response = cannotUnderstandScript[scriptIndex];
  state.step += 1;
  topicStates.set(topicId, state);
  return response;
}

function handleFallback(topicId: string): EvaluationResult {
  const state = getState(topicId);
  state.step += 1;
  topicStates.set(topicId, state);
  return defaultFallback;
}

function getState(topicId: string): TopicConversationState {
  const current = topicStates.get(topicId);
  if (current) {
    return current;
  }
  const initial: TopicConversationState = { step: 0 };
  topicStates.set(topicId, initial);
  return initial;
}

