from pydantic import BaseModel, Field

from ..state import AgentState


class PlanStep(BaseModel):
    step: str = Field(min_length=1, description="One sequential action required")


class PlanOutput(BaseModel):
    steps: list[PlanStep] = Field(description="Ordered actions to answer the query")


def create_planner_node(llm):
    structured_llm = llm.with_structured_output(PlanOutput)

    def planner(state: AgentState) -> dict:
        prompt = (
            "Create a short, sequential plan for answering the user query. "
            "Use the available enterprise connectors when evidence is needed.\n"
            f"User query: {state['user_query']}\n"
            f"Memory context: {state['memory_context']}\n"
            f"Previous execution messages: {state['messages']}\n"
            "If a previous tool failed, change the search strategy or connector parameters."
        )
        result = structured_llm.invoke(prompt)
        plan = [item.step for item in result.steps]
        return {"plan": plan, "current_step": 0}

    return planner


def planner_node(state: AgentState) -> dict:
    from ..llm import get_llm

    return create_planner_node(get_llm())(state)
