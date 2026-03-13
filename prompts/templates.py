# Niche topics mapping
NICHE_TOPICS = {
    "Generative AI": [
        "GPT-4 and large language models reshaping enterprise workflows",
        "Generative AI in content creation and creative industries",
        "Foundation models and fine-tuning strategies",
        "Multimodal AI: text, image, audio, and video generation",
        "AI hallucinations and how to mitigate them",
        "Prompt engineering best practices for production",
        "Open-source vs proprietary LLMs: making the right choice",
    ],
    "Agentic AI": [
        "AI agents that autonomously complete multi-step business tasks",
        "Tool-calling agents replacing traditional automation pipelines",
        "Multi-agent orchestration for complex workflows",
        "Human-in-the-loop vs fully autonomous AI agents",
        "ReAct and plan-and-execute agent patterns",
        "AI agents for software engineering and code generation",
        "Self-healing agents and error recovery strategies",
    ],
    "RAG (Retrieval-Augmented Generation)": [
        "RAG vs fine-tuning: when to use which approach",
        "Advanced RAG techniques: re-ranking, hybrid search, and HyDE",
        "Building enterprise knowledge bases with RAG",
        "Chunking strategies that dramatically improve RAG accuracy",
        "Evaluating RAG pipelines: metrics and best practices",
        "RAG for legal, healthcare, and financial compliance",
        "Real-time RAG with streaming and live data sources",
    ],
    "Multimodal RAG": [
        "Multimodal RAG: combining text, images, and tables from PDFs",
        "Vision-language models powering next-gen document understanding",
        "Colpali and late interaction models for multimodal retrieval",
        "Building chatbots that understand charts, diagrams, and images",
        "Multimodal embeddings: how machines see and read simultaneously",
        "Document AI: extracting insights from complex enterprise documents",
        "Multimodal RAG for medical imaging and clinical notes",
    ],
}

# Lazy import so that missing langchain doesn't crash app on startup
try:
    from langchain_core.prompts import ChatPromptTemplate
except ImportError:
    ChatPromptTemplate = None  # type: ignore

# Main LinkedIn post generation prompt
LINKEDIN_POST_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are an expert LinkedIn content creator specializing in AI and technology trends.
Your posts consistently go viral because they combine deep technical insight with human storytelling.
You write for senior professionals, engineers, founders, and tech leaders who want to stay ahead.

STRICT FORMAT RULES:
1. Hook (1 line only): Bold, scroll-stopping. Surprising, emotional, or thought-provoking.
2. Description (2 lines): Concise story or explanation. Relatable, conversational, builds curiosity.
3. Key Highlights (max 5 bullet points): Short, powerful, jargon-free insights. Use • as bullet.
4. Closing Statement (1 line): Thought-provoking or motivational. Encourages engagement.

STRICT CONSTRAINTS:
- Total word count: UNDER 220 words
- Tone: Engaging, professional, human — NOT corporate or robotic
- Emojis: Only if they genuinely enhance readability. Max 3-4 total.
- NO hashtags in the body (add them at the very end only)
- NO corporate buzzwords like "synergy", "leverage", "game-changer" overuse

OUTPUT FORMAT — return ONLY the post, nothing else."""),
    ("human", """Write a LinkedIn post about this topic: {topic}

Niche: {niche}
Additional context: {context}

Follow the exact format: Hook → Description → Key Highlights → Closing Statement.
Keep it under 220 words. Make it genuinely insightful and shareable.""")
])

# Research/enrichment prompt
RESEARCH_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are an AI research analyst. Extract the 5 most compelling, 
specific, and non-obvious facts or insights about the given AI topic. 
Focus on: recent developments, surprising statistics, real-world impact, 
practical implications, and future trajectories.
Return as a JSON with key "insights" containing a list of strings."""),
    ("human", "Research topic: {topic}\nNiche: {niche}")
])

# Hook generation prompt
HOOK_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are a master copywriter for LinkedIn. Create 3 alternative 
scroll-stopping opening hooks for an AI topic. Each hook must be:
- Exactly 1 line
- Either surprising, counterintuitive, emotionally resonant, or boldly opinionated
- Suitable for senior tech professionals
Return as JSON with key "hooks" containing a list of 3 strings."""),
    ("human", "Topic: {topic}\nNiche: {niche}\nContext: {context}")
])

# Post refinement prompt  
REFINE_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are a LinkedIn post editor. Your job is to refine and improve 
a LinkedIn post while keeping its structure and core message intact.

Improvements to make:
- Ensure it's under 220 words
- Make the hook more compelling if needed
- Ensure bullet points are crisp and impactful
- Verify the closing statement is motivational
- Remove any jargon or corporate speak
- Ensure strategic emoji usage (max 4)

Return ONLY the refined post, nothing else."""),
    ("human", "Original post:\n{post}\n\nUser feedback (if any): {feedback}\n\nRefine this post.")
])
