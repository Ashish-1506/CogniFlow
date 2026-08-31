import json

from pydantic import BaseModel, Field

from ..state import AgentState


class SynthesisOutput(BaseModel):
    response: str = Field(min_length=1)


def create_synthesizer_node(llm):
    structured_llm = llm.with_structured_output(SynthesisOutput)

    def synthesizer(state: AgentState) -> dict:
        prompt = (
            "Answer the user's query comprehensively using only the supplied evidence. "
            "Include inline citations such as [Jira-402] or [Notion-Q3]. "
            "Do not invent evidence.\n"
            f"User query: {state['user_query']}\n"
            f"Memory context: {state['memory_context']}\n"
            f"Evidence: {json.dumps(state['gathered_evidence'])}"
        )
        result = structured_llm.invoke(prompt)
        return {
            "messages": [*state["messages"], {"role": "assistant", "content": result.response}]
        }

    return synthesizer


def synthesizer_node(state: AgentState) -> dict:
    from ..llm import get_llm

    return create_synthesizer_node(get_llm())(state)
