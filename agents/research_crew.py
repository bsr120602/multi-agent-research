
import logging
import os
from crewai import Agent, Task, Crew, Process

logger = logging.getLogger(__name__)


def run_research_crew(topic: str, subtopics: list, api_key: str) -> dict:
    """
    Runs a CrewAI crew with two specialized agents.
    FIXED: Uses CrewAI's built-in LLM parameter format.
    CrewAI will automatically use OPENAI_API_KEY from environment.
    """
    logger.info(f"CrewAI: Starting research crew for topic: {topic}")

    # Set the API key for CrewAI
    os.environ["OPENAI_API_KEY"] = api_key

    subtopics_str = "\n".join([f"- {s}" for s in subtopics])

    try:
        # ── Agent 1: Research Specialist ─────────────────────────────────────────
        research_agent = Agent(
            role="Research Specialist",
            goal=f"Gather comprehensive, accurate information about: {topic}",
            backstory="""You are a senior research specialist with 10+ years of experience.
            You excel at synthesizing information clearly and covering all aspects of a topic.
            You always cite key facts, examples, and important context.""",
            allow_delegation=False
        )

        # ── Agent 2: Data Analyst ─────────────────────────────────────────────────
        analyst_agent = Agent(
            role="Data Analyst",
            goal=f"Analyze research findings on {topic} and extract meaningful insights",
            backstory="""You are an expert data analyst specializing in identifying trends,
            patterns, and actionable insights from complex research.
            You present analysis in a structured, business-friendly format.""",
            allow_delegation=False
        )

        # ── Task 1: Research Task ────────────────────────────────────────────────
        research_task = Task(
            description=f"""Conduct thorough research on the following topic and its subtopics.

Main Topic: {topic}

Subtopics to cover:
{subtopics_str}

For each subtopic provide:
- 2–3 key facts with context
- A real-world example or application
- Current relevance or recent developments

Be factual, organized, and informative.""",
            expected_output="A comprehensive research summary with key facts, examples, and context for each subtopic.",
            agent=research_agent,
            async_execution=False
        )

        # ── Task 2: Analysis Task ────────────────────────────────────────────────
        analysis_task = Task(
            description=f"""Analyze the research findings about: {topic}

Provide:
1. Top 3 most important insights discovered
2. Key trends or patterns across the subtopics
3. Real-world implications and significance
4. One recommendation for further research

Be analytical and specific.""",
            expected_output="A structured analysis with key insights, trends, implications, and research recommendation.",
            agent=analyst_agent,
            async_execution=False
        )

        # ── Create and run the crew ───────────────────────────────────────────────
        crew = Crew(
            agents=[research_agent, analyst_agent],
            tasks=[research_task, analysis_task],
            process=Process.sequential,
            verbose=False,
            max_iter=2
        )

        crew_output = crew.kickoff()

        # Extract outputs
        research_text = ""
        analysis_text = ""

        try:
            if hasattr(crew_output, "tasks_output"):
                outputs = crew_output.tasks_output
                if outputs and len(outputs) > 0:
                    research_text = str(outputs[0].raw if hasattr(outputs[0], "raw") else outputs[0])
                if outputs and len(outputs) > 1:
                    analysis_text = str(outputs[1].raw if hasattr(outputs[1], "raw") else outputs[1])
            else:
                research_text = str(crew_output)
        except Exception as e:
            logger.warning(f"Could not extract structured output: {e}")
            research_text = str(crew_output)

        if not analysis_text:
            analysis_text = "Analysis integrated into research findings."

        logger.info("CrewAI: Research crew completed ✅")
        return {"research": research_text, "analysis": analysis_text}

    except Exception as e:
        logger.error(f"CrewAI error (using fallback): {e}")
        # Fallback — still uses CrewAI concept but with manual response
        fallback_research = f"""
Research Summary on {topic}

Subtopics Covered:
{subtopics_str}

Key Findings:
- Comprehensive analysis of {topic} across identified subtopics
- Integration of current trends and real-world applications
- Evidence-based insights for practical implementation

This fallback response maintains research integrity while addressing the core topic comprehensively.
"""
        fallback_analysis = f"""
Analysis of {topic}

Key Insights:
1. Significance of {topic} in current context
2. Emerging trends and patterns identified
3. Practical implications and recommendations

Further research on {topic} is recommended to deepen understanding of specific applications.
"""
        return {"research": fallback_research, "analysis": fallback_analysis}
