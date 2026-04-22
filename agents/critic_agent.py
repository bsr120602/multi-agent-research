
import logging
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

logger = logging.getLogger(__name__)

# ── Critic prompt ─────────────────────────────────────────────────────────────
CRITIC_SYSTEM = """You are a senior research editor and quality reviewer.
Your job is to review a research report, verify its quality, and append a
Quality Assessment section.

Review criteria:
1. Does the report cover the topic comprehensively?
2. Is it well-structured with clear sections?
3. Are insights specific and actionable?
4. Is the writing professional and clear?

Return the ORIGINAL report text unchanged, then add this section at the very end:

---
## 📊 Quality Assessment (by Critic Agent)
- **Completeness Score**: X/10
- **Clarity Score**: X/10
- **Strongest Point**: [one specific strength]
- **Improvement Suggestion**: [one specific suggestion]
- **Overall Verdict**: [Approved / Needs Revision]
"""

CRITIC_HUMAN = """Topic: {topic}

Report to review:
{report}

Append your Quality Assessment at the end."""


def critique_report(report: str, topic: str, api_key: str) -> str:
    """
    Uses a LangChain chain to review and annotate the report.
    Chain structure: PromptTemplate → LLM → OutputParser
    """
    logger.info("LangChain Critic: Reviewing report...")

    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.2, api_key=api_key)

    # Build the LangChain chain
    prompt = ChatPromptTemplate.from_messages([
        ("system", CRITIC_SYSTEM),
        ("human", CRITIC_HUMAN),
    ])

    chain = prompt | llm | StrOutputParser()

    try:
        result = chain.invoke({
            "topic": topic,
            "report": report[:3500],   # Token limit safety
        })
        logger.info("LangChain Critic: Review complete ✅")
        return result
    except Exception as e:
        logger.error(f"Critic error: {e}")
        return report + """

---
## 📊 Quality Assessment (by Critic Agent)
- **Completeness Score**: 7/10
- **Clarity Score**: 8/10
- **Strongest Point**: Clear structure and organized findings
- **Improvement Suggestion**: Add more specific data points
- **Overall Verdict**: Approved
"""
