# SalesPilot AI

> Autonomous AI-powered account research and personalized outreach platform.  
> Built for the **Bright Data AI Agents & Web Data Hackathon**.

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                    Frontend (Next.js)                │
│  Mission Control → Agent Pipeline → Intel Dossier   │
│         ↕ SSE streaming   ↕ REST API                │
├─────────────────────────────────────────────────────┤
│                   Backend (FastAPI)                  │
│  ┌─────────────────────────────────────────────┐    │
│  │              Orchestrator                    │    │
│  │  ┌─────────┬─────────┬─────────────────┐    │    │
│  │  │Research │ Hiring  │  News  │TechStack│    │    │
│  │  │ Agent   │  Agent  │ Agent  │  Agent  │    │    │ ← Parallel
│  │  ├─────────┼─────────┼────────┼─────────┤    │    │
│  │  │PainPoint│Competitor│        │         │    │    │
│  │  │ Agent   │  Agent  │        │         │    │    │
│  │  └─────────┴─────────┴────────┴─────────┘    │    │
│  │          ↓                                    │    │
│  │  Intent Scoring → Email Agent                 │    │ ← Sequential
│  └─────────────────────────────────────────────┘    │
│                                                     │
│  Services: Bright Data │ Groq │ Google Gemini       │
└─────────────────────────────────────────────────────┘
```

## Tech Stack

| Layer     | Technology                                          |
|-----------|-----------------------------------------------------|
| Frontend  | Next.js 16, Tailwind CSS 4, TypeScript              |
| Backend   | FastAPI, Python 3.11+, Pydantic v2                  |
| Database  | SQLite (Local File Persistence)                     |
| AI/LLM    | Groq (Llama 3) & Google Gemini 2.5 Flash            |
| Web Data  | Bright Data SERP API, Web Scraper API               |
| Streaming | Server-Sent Events (SSE)                            |
| Design    | "Deep Space & Ember" theme (Google Stitch)          |

## Key Features

- **Autonomous Research Pipeline**: 8 specialized AI agents parallel-crawl the web and analyze data using Bright Data.
- **AI Head-to-Head Comparison**: Select any two completed company researches to generate a decisive, opinionated 8-dimension comparison report with a clear winner and risk analysis.
- **Local SQLite Persistence**: All research and comparison histories are instantly saved to a local database, preserving your data across server restarts.
- **Real-Time Agent Feed**: Watch the AI agents work in real-time with Server-Sent Events (SSE) streaming updates directly to the frontend.
- **Intent Scoring**: Algorithmically determines a 0-100 Buying Intent Score based on tech stack gaps, recent funding, and aggressive hiring signals.

## Infrastructure & Reliability

- **Dockerized AWS Deployment**: Fully containerized with a highly optimized multi-stage Next.js builder, orchestrated by `supervisord` to run FastAPI, Node, and Nginx in a single lightweight VPS.
- **Robust Real-Time SSE**: Real-time agent status streaming via Server-Sent Events, complete with Nginx proxy un-buffering (`proxy_buffering off`) for instantaneous UI updates.
- **Fault-Tolerant State Recovery**: UI seamlessly infers active agents across page reloads using a hybrid approach of live SSE streams combined with incremental SQLite database saves.

## Pages

| Route                   | Description                                    |
|-------------------------|------------------------------------------------|
| `/`                     | Mission Control Dashboard & Research History   |
| `/research/[id]`        | Research Pipeline + Intelligence Dossier       |
| `/compare/[idA]/[idB]`  | AI Head-to-Head Comparison Report              |

## Bright Data Integration

Our Orchestrator leverages Bright Data's powerful APIs to autonomously crawl the live internet and extract real-time intelligence instead of relying on outdated LLM training data:

1. **SERP API (`search_google` & `search_google_news`)**: Powers the core research agents (News, Pain Points, Tech Stack, Competitors, Hiring) by performing native Google and News searches through residential proxies, bypassing CAPTCHAs to return structured intelligence.
2. **Web Unlocker (`scrape_page`)**: Bypasses bot detection (like Cloudflare) to scrape the raw HTML/text content directly from target company homepages.
3. **Data Collection API (DCA)**: Specifically targets Bright Data's pre-built LinkedIn Company Profile dataset (`gd_l1viktl72bvl7bjuj0`) to safely and effortlessly extract structured LinkedIn company data.

## 8 AI Agents

1. **Research Agent** — Company overview via Bright Data web scraping
2. **Hiring Agent** — Job posting analysis for growth signals
3. **News Agent** — Funding, M&A, and press event scanning
4. **Tech Stack Agent** — Technology detection and gap analysis
5. **Pain Point Agent** — Frustration extraction from reviews
6. **Competitor Agent** — Competitive landscape mapping
7. **Intent Scoring Agent** — Weighted buying probability (0-100)
8. **Email Agent** — 4-format personalized outreach drafts

## Quick Start

### Frontend
```bash
cd frontend
npm install
npm run dev
# → http://localhost:3000
```

### Backend
```bash
cd backend
pip install -r requirements.txt
cp .env.example .env  # Fill in API keys
uvicorn app.main:app --reload --port 8000
```

### Environment Variables
```env
BRIGHT_DATA_API_TOKEN=your_token
GROQ_API_KEY=your_key
GOOGLE_API_KEY=your_key
```

## Built With

- **Bright Data** — Web scraping, SERP API, and web intelligence ($250 credit)
- **Groq Llama 3** — Lightning fast primary LLM for analysis and email generation
- **Google Gemini 2.5 Flash** — Fallback LLM engine
- **SQLite** — Local Database Persistence
- **Google Stitch** — UI/UX design system

## License

MIT — Built for lablab.ai Bright Data AI Agents & Web Data Hackathon
