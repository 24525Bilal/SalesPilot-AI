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
│  │  Intent Scoring → Email Agent → CRM Agent     │    │ ← Sequential
│  └─────────────────────────────────────────────┘    │
│                                                     │
│  Services: Bright Data │ Google Gemini │ HubSpot    │
└─────────────────────────────────────────────────────┘
```

## Tech Stack

| Layer     | Technology                                          |
|-----------|-----------------------------------------------------|
| Frontend  | Next.js 16, Tailwind CSS 4, TypeScript              |
| Backend   | FastAPI, Python 3.11+, Pydantic v2                  |
| AI/LLM    | Google Gemini 2.5 Flash (via langchain-google-genai) |
| Web Data  | Bright Data SERP API, Web Scraper API               |
| CRM       | HubSpot API (free tier)                             |
| Streaming | Server-Sent Events (SSE)                            |
| Design    | "Deep Space & Ember" theme (Google Stitch)          |

## Pages

| Route                   | Description                                    |
|-------------------------|------------------------------------------------|
| `/`                     | Mission Control Dashboard — command terminal   |
| `/research`             | Agent Hive — 9 deployed agents overview        |
| `/research/[id]`        | Research Pipeline + Intelligence Dossier       |
| `/history`              | Master Intel Archive — all past research       |
| `/signals`              | Lead Signals — real-time intent monitoring     |
| `/intel`                | Intel Stream — live intelligence feed          |

## Bright Data Integration

Our Orchestrator leverages Bright Data's powerful APIs to autonomously crawl the live internet and extract real-time intelligence instead of relying on outdated LLM training data:

1. **SERP API (`search_google` & `search_google_news`)**: Powers the core research agents (News, Pain Points, Tech Stack, Competitors, Hiring) by performing native Google and News searches through residential proxies, bypassing CAPTCHAs to return structured intelligence.
2. **Web Unlocker (`scrape_page`)**: Bypasses bot detection (like Cloudflare) to scrape the raw HTML/text content directly from target company homepages.
3. **Data Collection API (DCA)**: Specifically targets Bright Data's pre-built LinkedIn Company Profile dataset (`gd_l1viktl72bvl7bjuj0`) to safely and effortlessly extract structured LinkedIn company data.

## 9 AI Agents

1. **Research Agent** — Company overview via Bright Data web scraping
2. **Hiring Agent** — Job posting analysis for growth signals
3. **News Agent** — Funding, M&A, and press event scanning
4. **Tech Stack Agent** — Technology detection and gap analysis
5. **Pain Point Agent** — Frustration extraction from reviews
6. **Competitor Agent** — Competitive landscape mapping
7. **Intent Scoring Agent** — Weighted buying probability (0-100)
8. **Email Agent** — 4-format personalized outreach drafts
9. **CRM Agent** — HubSpot sync and enrichment

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
GEMINI_API_KEY=your_key
HUBSPOT_ACCESS_TOKEN=your_token
```

## Demo Mode

The frontend works in **demo mode** without any backend — click any company in the Live Signal Feed or type a company name to see the full intelligence dossier with sample data.

## Built With

- **Bright Data** — Web scraping, SERP API, and web intelligence ($250 credit)
- **Google Gemini 2.5 Flash** — LLM for analysis and email generation (free tier)
- **HubSpot** — CRM integration (free tier)
- **Google Stitch** — UI/UX design system

## License

MIT — Built for lablab.ai Bright Data AI Agents & Web Data Hackathon
