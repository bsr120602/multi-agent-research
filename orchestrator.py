
import logging
import time
import os
from typing import Callable, Optional

from agents.security_agent import SecurityAgent
from agents.planner_agent import run_planner
from agents.research_crew import run_research_crew
from agents.report_agent import generate_report
from agents.critic_agent import critique_report

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger(__name__)


class MultiAgentOrchestrator:
    """
    Custom Orchestration Layer

    Pipeline (sequential):
    Step 1 → Security Agent     (Custom Python)      — validates input
    Step 2 → Planner Agent      (LangGraph)          — creates research plan
    Step 3 → Research Crew      (CrewAI)             — researches and analyzes
    Step 4 → Report Writer      (Semantic Kernel)    — writes report
    Step 5 → Critic Agent       (LangChain)          — reviews and scores

    Each step has:
    - Logging
    - Error handling with fallback
    - Status tracking
    """

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.security = SecurityAgent()
        self.execution_log = []
        logger.info("✅ MultiAgentOrchestrator initialized with all 5 agents")

    def _log(self, step: str, status: str, detail: str = ""):
        entry = {
            "step": step,
            "status": status,
            "detail": detail,
            "time": time.strftime("%H:%M:%S"),
        }
        self.execution_log.append(entry)
        icon = {"success": "✅", "error": "❌", "running": "🔄"}.get(status, "ℹ️")
        logger.info(f"{icon} [{entry['time']}] {step}: {detail}")

    def run(self, topic: str, progress_cb: Optional[Callable] = None) -> dict:
        """
        Runs the complete 5-step multi-agent pipeline.
        Returns: { success, topic, subtopics, report, log }
        """
        self.execution_log = []

        def prog(msg):
            if progress_cb:
                progress_cb(msg)

        # ── STEP 1: Security Agent ──────────────────────────────────────────
        prog("🔒 Step 1/5 — Security Agent validating input...")
        self._log("Security Agent (Custom)", "running")

        is_valid, msg = self.security.validate(topic)
        if not is_valid:
            self._log("Security Agent (Custom)", "error", msg)
            return {"success": False, "error": msg, "report": None, "log": self.execution_log}

        clean_topic = self.security.sanitize(topic)
        self._log("Security Agent (Custom)", "success", "Input validated & sanitized")

        # ── STEP 2: Planner Agent (LangGraph) ──────────────────────────────
        prog("🗺️  Step 2/5 — Planner Agent (LangGraph) creating plan...")
        self._log("Planner Agent (LangGraph)", "running")
        try:
            subtopics = run_planner(clean_topic, self.api_key)
            self._log("Planner Agent (LangGraph)", "success",
                      f"Plan: {', '.join(subtopics)}")
        except Exception as e:
            subtopics = [clean_topic]
            self._log("Planner Agent (LangGraph)", "error", str(e))

        # ── STEP 3: Research Crew (CrewAI) ─────────────────────────────────
        prog("🔬 Step 3/5 — Research Crew (CrewAI) researching...")
        self._log("Research Crew (CrewAI)", "running")

        # Set API key for CrewAI
        os.environ["OPENAI_API_KEY"] = self.api_key

        try:
            crew_out = run_research_crew(clean_topic, subtopics, self.api_key)
            research = crew_out.get("research", "")
            analysis = crew_out.get("analysis", "")
            self._log("Research Crew (CrewAI)", "success", "Research + analysis complete")
        except Exception as e:
            research = f"Key information gathered about {clean_topic}."
            analysis = f"Notable trends identified for {clean_topic}."
            self._log("Research Crew (CrewAI)", "error", str(e))

        # ── STEP 4: Report Writer (Semantic Kernel) ─────────────────────────
        prog("📝 Step 4/5 — Report Agent (Semantic Kernel) writing report...")
        self._log("Report Writer (Semantic Kernel)", "running")
        try:
            report = generate_report(clean_topic, research, analysis, self.api_key)
            self._log("Report Writer (Semantic Kernel)", "success", "Report generated")
        except Exception as e:
            report = f"# {clean_topic}\n\n{research}\n\n{analysis}"
            self._log("Report Writer (Semantic Kernel)", "error", str(e))

        # ── STEP 5: Critic Agent (LangChain) ───────────────────────────────
        prog("🔍 Step 5/5 — Critic Agent (LangChain) reviewing report...")
        self._log("Critic Agent (LangChain)", "running")
        try:
            final_report = critique_report(report, clean_topic, self.api_key)
            self._log("Critic Agent (LangChain)", "success", "Report reviewed & scored")
        except Exception as e:
            final_report = report
            self._log("Critic Agent (LangChain)", "error", str(e))

        prog("✅ All agents complete — Report ready!")

        return {
            "success": True,
            "topic": clean_topic,
            "subtopics": subtopics,
            "report": final_report,
            "log": self.execution_log,
        }
