from typing import TypedDict, Optional, List
import json
import os
import sys

from langsmith import traceable

# Ensure project root on path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser

from prompts.templates import (
    LINKEDIN_POST_PROMPT,
    RESEARCH_PROMPT,
    HOOK_PROMPT,
    REFINE_PROMPT
)


# ── State Schema ──────────────────────────────────────────────────────────────

class PostState(TypedDict):
    # Inputs
    niche: str
    topic: str
    custom_context: str
    # Intermediate
    research_insights: List[str]
    hook_alternatives: List[str]
    draft_post: str
    word_count: int
    # Output
    final_post: str
    hashtags: List[str]
    error: Optional[str]
    # Control
    refinement_feedback: str
    needs_refinement: bool


# ── Node Functions ────────────────────────────────────────────────────────────
@traceable(name="research_node")
def research_node(state: PostState) -> PostState:
    """Research node: gather key insights about the topic."""
    try:
        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)
        chain = RESEARCH_PROMPT | llm | JsonOutputParser()
        result = chain.invoke({
            "topic": state["topic"],
            "niche": state["niche"]
        })
        insights = result.get("insights", [])
        return {**state, "research_insights": insights, "error": None}
    except Exception as e:
        return {**state, "research_insights": [], "error": str(e)}


@traceable(name="hook_generation_node")
def hook_generation_node(state: PostState) -> PostState:
    """Hook node: generate multiple hook alternatives."""
    try:
        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.8)
        chain = HOOK_PROMPT | llm | JsonOutputParser()

        context = state.get("custom_context", "")
        if state["research_insights"]:
            context += "\n\nKey insights: " + "; ".join(state["research_insights"][:3])

        result = chain.invoke({
            "topic": state["topic"],
            "niche": state["niche"],
            "context": context
        })
        hooks = result.get("hooks", [])
        return {**state, "hook_alternatives": hooks}
    except Exception as e:
        return {**state, "hook_alternatives": [], "error": str(e)}

@traceable(name="draft_post_node")
def draft_post_node(state: PostState) -> PostState:
    """Draft node: generate the full LinkedIn post."""
    try:
        llm = ChatOpenAI(model="gpt-4o", temperature=0.7)
        chain = LINKEDIN_POST_PROMPT | llm | StrOutputParser()

        # Build enriched context
        context_parts = []
        if state.get("custom_context"):
            context_parts.append(state["custom_context"])
        if state.get("research_insights"):
            context_parts.append("Insights: " + "; ".join(state["research_insights"][:4]))
        if state.get("hook_alternatives"):
            context_parts.append("Consider these hooks: " + " | ".join(state["hook_alternatives"][:2]))

        draft = chain.invoke({
            "topic": state["topic"],
            "niche": state["niche"],
            "context": "\n".join(context_parts) if context_parts else "No additional context."
        })

        word_count = len(draft.split())
        return {**state, "draft_post": draft, "word_count": word_count}
    except Exception as e:
        return {**state, "draft_post": "", "word_count": 0, "error": str(e)}

@traceable(name="quality_check_node")
def quality_check_node(state: PostState) -> PostState:
    """Quality check: decide if post needs refinement."""
    draft = state.get("draft_post", "")
    word_count = len(draft.split())

    needs_refinement = (
            word_count > 220 or
            state.get("refinement_feedback", "") != "" or
            len(draft.strip()) < 50
    )

    return {**state, "needs_refinement": needs_refinement, "word_count": word_count}

@traceable(name="refine_post_node")
def refine_post_node(state: PostState) -> PostState:
    """Refinement node: polish the post based on feedback."""
    try:
        llm = ChatOpenAI(model="gpt-4o", temperature=0.5)
        chain = REFINE_PROMPT | llm | StrOutputParser()

        refined = chain.invoke({
            "post": state["draft_post"],
            "feedback": state.get("refinement_feedback", "Ensure under 220 words and maximum impact.")
        })

        word_count = len(refined.split())
        return {**state, "draft_post": refined, "word_count": word_count, "needs_refinement": False}
    except Exception as e:
        return {**state, "error": str(e)}

@traceable(name="hashtag_node")
def hashtag_node(state: PostState) -> PostState:
    """Hashtag node: generate relevant hashtags."""
    try:
        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)
        prompt = f"""Generate 8-10 highly relevant LinkedIn hashtags for a post about:
Topic: {state['topic']}
Niche: {state['niche']}

Return ONLY a JSON with key "hashtags" as a list of strings (include the # symbol).
Mix broad and niche-specific tags. Examples: #GenerativeAI #LangChain #RAG #AIAgents"""

        from langchain_core.messages import HumanMessage
        response = llm.invoke([HumanMessage(content=prompt)])
        parsed = json.loads(response.content)
        hashtags = parsed.get("hashtags", [])

        # Assemble final post with hashtags
        final_post = state["draft_post"].strip()
        if hashtags:
            final_post += "\n\n" + " ".join(hashtags)

        return {**state, "hashtags": hashtags, "final_post": final_post}
    except Exception as e:
        return {**state, "hashtags": [], "final_post": state["draft_post"], "error": str(e)}


# ── Routing Logic ─────────────────────────────────────────────────────────────

def should_refine(state: PostState) -> str:
    if state.get("needs_refinement", False):
        return "refine"
    return "hashtags"


# ── Graph Builder ─────────────────────────────────────────────────────────────

def build_graph() -> StateGraph:
    workflow = StateGraph(PostState)

    # Add nodes
    workflow.add_node("research", research_node)
    workflow.add_node("hooks", hook_generation_node)
    workflow.add_node("draft", draft_post_node)
    workflow.add_node("quality_check", quality_check_node)
    workflow.add_node("refine", refine_post_node)
    workflow.add_node("hashtags", hashtag_node)

    # Set entry point
    workflow.set_entry_point("research")

    # Define edges
    workflow.add_edge("research", "hooks")
    workflow.add_edge("hooks", "draft")
    workflow.add_edge("draft", "quality_check")
    workflow.add_conditional_edges(
        "quality_check",
        should_refine,
        {"refine": "refine", "hashtags": "hashtags"}
    )
    workflow.add_edge("refine", "hashtags")
    workflow.add_edge("hashtags", END)

    return workflow.compile()


# Singleton compiled graph
_graph = None


def get_graph():
    global _graph
    if _graph is None:
        _graph = build_graph()
    return _graph