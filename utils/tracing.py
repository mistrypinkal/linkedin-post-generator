import os


def setup_langsmith():
    """Configure LangSmith tracing."""
    api_key = os.getenv("LANGCHAIN_API_KEY")
    if api_key:
        os.environ["LANGCHAIN_TRACING_V2"] = "true"
        os.environ["LANGCHAIN_PROJECT"] = os.getenv("LANGCHAIN_PROJECT", "linkedin-post-generator")
        return True
    return False


def get_langsmith_client():
    """Return LangSmith client if configured."""
    try:
        from langsmith import Client
        api_key = os.getenv("LANGCHAIN_API_KEY")
        if api_key:
            return Client(api_key=api_key)
    except Exception:
        pass
    return None


def get_run_url(run_id: str):
    """Get LangSmith trace URL for a run."""
    project = os.getenv("LANGCHAIN_PROJECT", "linkedin-post-generator")
    api_key = os.getenv("LANGCHAIN_API_KEY")
    if api_key and run_id:
        return f"https://smith.langchain.com/public/{run_id}/r"
    return None
