# Multi-Agent Research Report Generator

## Overview
A multi-agent AI system that generates research reports using 5 specialized agents.

## Agents & Frameworks
| Agent | Framework | Role |
|---|---|---|
| Security Agent | Custom Python | Input validation & guardrails |
| Planner Agent | LangGraph | Task decomposition workflow |
| Research Agent | CrewAI | Information gathering |
| Analyst Agent | CrewAI | Data analysis |
| Report Writer | Semantic Kernel | Professional report generation |
| Critic Agent | LangChain | Quality review |
| Orchestrator | Custom Python | Agent coordination |

## Setup
```bash
pip install -r requirements.txt
python app.py
```

## Demo
Visit the live endpoint: [your-azure-url]

## Architecture
See ARCHITECTURE.md for full architecture diagram.
