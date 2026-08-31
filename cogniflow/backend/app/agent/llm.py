def get_llm():
    """Create the configured chat model only when a graph run needs it."""
    from langchain_community.chat_models import ChatOllama

    return ChatOllama(model="llama3.2", temperature=0)
