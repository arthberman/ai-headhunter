# AI Headhunting

A sophisticated multi-agent AI platform designed to automate technical recruiting workflows. Built with LangGraph, this system orchestrates specialized agents to handle candidate matching, scorecard generation, company research, and interactive feedback collection.

## Features

### Core Agents

- **Matcher Agent** - Advanced candidate-to-job matching using semantic analysis and configurable scoring algorithms
- **Scorecard Generator** - Creates comprehensive evaluation scorecards with structured candidate assessments
- **Feeder Agent** - Generates and synthesizes recruiting queries, manages search parameters
- **Company Researcher** - Automated company intelligence gathering using web search and API integration
- **Feedback Chat** - Interactive conversational interface for collecting recruiter feedback on candidates
- **Setup Graph** - Handles initial configuration, authentication, and system initialization

### Technical Capabilities

- **Multi-Agent Orchestration** - LangGraph-powered state machines coordinate complex workflows
- **Multi-LLM Integration** - Leverages OpenAI, Anthropic and Groq for optimal performance
- **Secure Authentication** - Token-based API authentication with organization-scoped access control
- **Session Management** - PostgreSQL-backed session persistence and state management
- **External Data Integration** - Real-time company research via Tavily API and Crustdata
- **Conversation History** - Persistent storage for multi-turn agent interactions

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    LangGraph Cloud                       │
├─────────────────────────────────────────────────────────┤
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌─────────┐ │
│  │ Matcher  │  │Scorecard │  │  Feeder  │  │ Setup   │ │
│  │  Agent   │  │Generator │  │  Agent   │  │  Graph  │ │
│  └──────────┘  └──────────┘  └──────────┘  └─────────┘ │
│  ┌──────────┐  ┌──────────┐                             │
│  │ Company  │  │Feedback  │                             │
│  │Researcher│  │   Chat   │                             │
│  └──────────┘  └──────────┘                             │
├─────────────────────────────────────────────────────────┤
│              Security & Authentication                   │
├─────────────────────────────────────────────────────────┤
│              PostgreSQL DB  │  Session Management       │
└─────────────────────────────────────────────────────────┘
```

## Tech Stack

**Core Framework:**
- Python 3.12+
- LangGraph 0.3.5+ (Agent orchestration)
- LangChain 0.3.20+ (LLM integration)
- Pydantic 2.10+ (Data validation)

**AI/LLM Providers:**
- Anthropic (via AWS Bedrock)
- OpenAI
- Groq

**Infrastructure:**
- PostgreSQL - State persistence and session management
- LangGraph Cloud - Production deployment
- Docker & Docker Compose - Local development

**External APIs:**
- Tavily API - Web search and research
- Crustdata API - Company intelligence
- RapidAPI - Additional data sources

## Deployment

This system is deployed via **LangGraph Cloud** and can be accessed using the **LangGraph SDK**.

### Using the LangGraph SDK

```python
from langgraph_sdk import get_client

# Connect to deployed graph
client = get_client(url="YOUR_LANGGRAPH_CLOUD_URL")

# Invoke the matcher agent
response = await client.runs.create(
    assistant_id="matcher",
    input={
        "candidate": {
            "skills": ["Python", "Machine Learning", "AWS"],
            "experience_years": 5
        },
        "job_requirements": {
            "required_skills": ["Python", "AI/ML"],
            "min_experience": 3
        }
    }
)
```

## Project Structure

```
ai-headhunter/
├── src/
│   ├── matcher/           # Candidate matching logic
│   ├── setup/             # Setup and initialization
│   ├── feeder/            # Query generation
│   ├── company_researcher/ # Company intelligence
│   ├── feedback/          # Feedback processing
│   ├── feedback_chat/     # Interactive feedback
│   ├── security/          # Authentication
│   └── utils/             # Shared utilities
├── tests/                 # Test suite
├── langgraph.json         # LangGraph configuration
└── docker-compose.yml     # Docker orchestration
```

## License

Distributed under the MIT License.

## Acknowledgements

- [LangGraph](https://github.com/langchain-ai/langgraph) - Agent orchestration framework
- [LangChain](https://github.com/langchain-ai/langchain) - LLM integration library
- [Anthropic Claude](https://www.anthropic.com) - Claude models
- [OpenAI](https://openai.com) - GPT models

---

**Portfolio Project** - Demonstrates advanced AI agent architecture, multi-agent orchestration, production-ready security, and modern Python development practices.
