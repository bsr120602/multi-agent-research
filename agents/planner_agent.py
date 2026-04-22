
import logging
from typing import TypedDict, List, Annotated
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
import operator

logger = logging.getLogger(__name__)


# ── State: what gets passed between graph nodes ──────────────────────────────
class ResearchState(TypedDict):
    topic: str
    subtopics: List[str]
    status: str
    error: str


# ── Node functions ────────────────────────────────────────────────────────────
def make_plan_node(llm):
    """Returns the planner node function."""
    def plan_research(state: ResearchState) -> dict:
        """Node 1: Breaks the topic into 3 specific subtopics."""
        logger.info(f"LangGraph Planner: Planning for topic = {state['topic']}")
        try:
            messages = [
                SystemMessage(content="""You are a research planning expert.
                Break down the research topic into exactly 3 specific, relevant subtopics.
                Respond ONLY with a numbered list, one per line:
                1. First subtopic
                2. Second subtopic
                3. Third subtopic"""),
                HumanMessage(content=f"Research Topic: {state['topic']}")
            ]
            response = llm.invoke(messages)
            lines = [l.strip() for l in response.content.strip().split('\n') if l.strip()]
            subtopics = []
            for line in lines:
                # Remove leading numbers/bullets
                cleaned = line.lstrip('0123456789.-) ').strip()
                if cleaned and len(cleaned) > 3:
                    subtopics.append(cleaned)
            if not subtopics:
                subtopics = [f"{state['topic']} overview",
                             f"{state['topic']} applications",
                             f"{state['topic']} future trends"]
            return {"subtopics": subtopics[:3], "status": "planned"}
        except Exception as e:
            logger.error(f"Planner node error: {e}")
            return {"subtopics": [state["topic"]], "status": "error", "error": str(e)}
    return plan_research


def make_validate_node():
    """Returns the validation node function."""
    def validate_plan(state: ResearchState) -> dict:
        """Node 2: Validates that the plan has subtopics."""
        if state.get("subtopics") and len(state["subtopics"]) > 0:
            logger.info("LangGraph Planner: Plan validated ✅")
            return {"status": "validated"}
        return {"status": "error", "error": "Empty plan generated"}
    return validate_plan


# ── Build + compile the LangGraph workflow ────────────────────────────────────
def create_planner_workflow(api_key: str):
    """Builds the LangGraph state machine."""
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.3, api_key=api_key)

    workflow = StateGraph(ResearchState)

    # Add nodes
    workflow.add_node("plan_research", make_plan_node(llm))
    workflow.add_node("validate_plan", make_validate_node())

    # Add edges (the arrows in the flowchart)
    workflow.set_entry_point("plan_research")
    workflow.add_edge("plan_research", "validate_plan")
    workflow.add_edge("validate_plan", END)

    return workflow.compile()


def run_planner(topic: str, api_key: str) -> List[str]:
    """Runs the LangGraph planner and returns a list of subtopics."""
    planner_app = create_planner_workflow(api_key)
    initial_state: ResearchState = {
        "topic": topic,
        "subtopics": [],
        "status": "starting",
        "error": ""
    }
    result = planner_app.invoke(initial_state)
    return result.get("subtopics", [topic])
