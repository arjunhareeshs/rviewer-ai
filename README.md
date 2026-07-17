# RViewer AI

> **RViewer AI** — an end-to-end **AI Resume Intelligence Platform** that parses, analyses, audits, and interviews candidates autonomously. Upload a resume once, and the system produces a structured profile, deep skill analysis, link/portfolio verification, a personalised learning roadmap, a tailored resume builder, and runs a **real-time voice-based mock interview** with a live AI interviewer. Every step is grounded in the candidate's own document using Retrieval-Augmented Generation (RAG).

---

## 1. RViewer AI?

RViewer AI is a AI - full-stack, multi-agent platform designed to act as an **always-on technical career copilot** for both candidates and recruiters.

Unlike a static parser, RViewer AI treats a resume as a living knowledge base:

- **Extraction** — Pulls structured data from PDF/DOCX resumes using a hybrid pipeline (Docling + Vision-Language Models on NVIDIA NIM) and a layout-aware column detector.
- **Indexing** — Chunks, embeds (HuggingFace sentence-transformers), and stores every section in a **Qdrant** vector store so the rest of the system can *query the candidate* semantically.
- **Analysis** — Runs an ATS-style audit, a project-stack analyser, and a role recommender (taxonomy of 100+ tech roles) over the parsed profile.
- **Link Forensics** — Independently scrapes GitHub, GitLab, LeetCode, Codeforces, HackerRank, HackerEarth, Kaggle, StackOverflow, GeeksforGeeks, LinkedIn, Dev.to, Bitbucket, and portfolio sites to **verify** the links on the resume (not just trust them).
- **Roadmap** — Generates a personalised, dependency-aware, multi-track learning roadmap with embedded resource links and an auto-rendered Mermaid mind-map.
- **Resume Builder** — Lets the candidate re-skin, restructure, and export a brand-new PDF resume with AI-injected achievement bullets.
- **Voice Interview** — Spawns a **real-time conversational AI agent** over LiveKit (WebRTC) that conducts a multi-phase interview (intro → projects → technicals → behavioural → wrap-up), speaks via Deepgram TTS, listens via Groq Whisper STT, reasons via Groq/OpenAI/OpenRouter LLMs, and produces a scored PDF evaluation report with a radar chart.
- **Admin Console** — A separate role-gated workspace for recruiters to upload candidates, search via natural-language filters, and review interview outcomes.

The platform is designed to be **multi-modal, multi-tenant, and modular** — every stage is a swappable service, every external AI is a provider abstraction, and every heavy component runs asynchronously.

---

## 2. What is it designed for?

RViewer AI is designed to solve three problems at once:

| Stakeholder | Problem | RViewer AI's solution |
|---|---|---|
| **Job seekers** | "How strong is my resume, really? What should I learn next? Can I practise an interview?" | One upload → full audit, roadmap, builder, and a live mock interview with a scored PDF report. |
| **Recruiters / HR** | "This resume says X — is it true? Can I screen 50 candidates without burning hours?" | A verified candidate profile with independent platform stats, a natural-language candidate search, and an automated first-round interview. |
| **Coaches / Mentors** | "Give my student a plan grounded in *their* resume, not a generic template." | A grounded RAG pipeline that reasons over the candidate's own document plus a dynamic roadmap generator. |

**Design principles**

1. **Grounded, not hallucinated.** Every insight the LLM produces is anchored in the candidate's actual resume (retrieved via vector search) or independently fetched external data.
2. **Provider-agnostic AI.** LLMs (OpenRouter / Groq / OpenAI), VLMs (NVIDIA NIM / OpenAI / Gemini), STT (Groq Whisper / Deepgram) and TTS (Deepgram) are all pluggable via env config.
3. **Stateless workers, stateful agents.** The web layer is a thin FastAPI surface; long-running work (voice agent, vector indexing, scraping) runs in background tasks and LiveKit workers.
4. **Local-first development.** Postgres, Qdrant, and LiveKit all run via `docker-compose`. No cloud lock-in for dev.
5. **Separation of concerns.** `core/` modules own business logic, `api/` owns transport, `models/` owns persistence — clean enough that any stage can be lifted into a microservice.

---

## 3. Folder Structure

```
Rviewer - ai/
├── client/                          # React 19 + TypeScript + Vite frontend
│   ├── public/                      # Static assets
│   ├── src/
│   │   ├── components/
│   │   │   ├── admin/               # Admin layout (recruiter console)
│   │   │   ├── analysis/            # Profile & full-analysis visualisations
│   │   │   ├── builder/             # Drag-resume builder preview
│   │   │   ├── interview/           # LiveKit room shell, mic, captions
│   │   │   ├── landing/             # Hero, navbar, marketing sections
│   │   │   ├── roadmap/             # Mermaid mind-map, side panel, timeline
│   │   │   ├── ui/                  # Animated primitives (Framer Motion)
│   │   │   ├── workspace/           # Authenticated workspace shell
│   │   │   └── ProtectedRoute.tsx   # Role-gated route guard
│   │   ├── pages/
│   │   │   ├── LandingPage.tsx
│   │   │   ├── LoginPage.tsx
│   │   │   ├── RegisterPage.tsx
│   │   │   ├── UploadPage.tsx
│   │   │   ├── NotFoundPage.tsx
│   │   │   ├── analysis/            # Overview / Full / Links / Roadmap
│   │   │   ├── builder/             # Resume builder page
│   │   │   ├── interview/           # Lobby / Room / Report
│   │   │   └── admin/               # Candidates / Upload (recruiter)
│   │   ├── hooks/                   # useResume, useResumeData
│   │   ├── lib/                     # api / interviewApi / builderApi / utils
│   │   ├── providers/               # SmoothScrollProvider (Lenis)
│   │   ├── stores/                  # Zustand: auth, resume, interview, builder, roadmap, admin
│   │   └── types/                   # Shared TypeScript types
│   ├── package.json
│   ├── vite.config.ts
│   └── tailwind.config.js
│
├── server/                          # Python 3.13 FastAPI backend
│   ├── app/
│   │   ├── main.py                  # FastAPI app, CORS, rate-limit, lifespan
│   │   ├── config.py                # Pydantic-Settings (providers, secrets, paths)
│   │   ├── api/
│   │   │   ├── v1/                  # REST routers
│   │   │   │   ├── auth.py          # JWT register/login
│   │   │   │   ├── resumes.py       # Upload / fetch / list
│   │   │   │   ├── retrieval.py     # RAG query endpoint
│   │   │   │   ├── analysis.py      # ATS, projects, role recommendation
│   │   │   │   ├── builder.py       # AI-assisted resume re-skin
│   │   │   │   ├── roadmap.py       # Personalised learning roadmap
│   │   │   │   ├── admin.py         # Recruiter NL search & candidate ops
│   │   │   │   ├── interview.py     # Room create/start/end + report
│   │   │   │   └── router.py        # Aggregates all v1 routers
│   │   │   └── websocket/           # Real-time channels (e.g. progress)
│   │   ├── core/                    # Domain logic (framework-free)
│   │   │   ├── extraction/          # Docling + VLM + column detector + cleaner
│   │   │   ├── embedding/           # Chunker + HF embedder
│   │   │   ├── rag/                 # Qdrant indexer, retriever, query engine, synthesizer
│   │   │   ├── analysis/            # ATS analyser, project analyser, role recommender, tech tier
│   │   │   ├── link_analysis/       # 13 platform scrapers + viz generator
│   │   │   ├── roadmap/             # Generator + link fetcher (Playwright)
│   │   │   ├── builder/             # PDF generator + template injector
│   │   │   ├── interview/
│   │   │   │   ├── agent.py         # LiveKit voice pipeline (STT → LLM → TTS)
│   │   │   │   ├── agent_entrypoint.py
│   │   │   │   ├── flow_manager.py  # Multi-phase state machine
│   │   │   │   ├── llm_service.py   # Provider-agnostic interview LLM
│   │   │   │   ├── session_manager.py
│   │   │   │   ├── report_generator.py  # PDF + radar chart
│   │   │   │   ├── resume_service.py
│   │   │   │   ├── sanitization.py
│   │   │   │   └── prompts/         # interview.md, report.md
│   │   │   └── admin/               # Natural-language candidate filter
│   │   ├── db/                      # Async SQLAlchemy engine + migrations
│   │   ├── models/                  # SQLAlchemy ORM (resume, interview, builder, roadmap, admin)
│   │   ├── schemas/                 # Pydantic request/response models
│   │   └── utils/                   # Auth, helpers
│   ├── data/                        # Local persistence
│   │   ├── sessions/                # Per-room session JSON
│   │   ├── vector_store/            # Per-room Qdrant namespaces
│   │   └── outputs/                 # Generated PDF reports
│   ├── templates/                   # Resume template specs (JSON)
│   ├── uploads/                     # Raw resume uploads
│   ├── livekit.yaml                 # LiveKit server config
│   ├── run_dev.py                   # Windows-safe dev launcher (forrtl fix)
│   ├── run_agent.py                 # LiveKit agent worker launcher
│   ├── init_db.py                   # DB bootstrap
│   ├── requirements.txt
│   └── .env
│
├── shared/                          # Cross-package inputs / scripts
│   ├── inputs/
│   └── scripts/
│
├── docker/
│   └── (Dockerfiles for prod deploy)
│
├── docs/                            # Architecture & design notes
│
├── test/                            # E2E / integration test fixtures
│   ├── inputs/
│   ├── outputs/
│   └── scripts/
│
├── docker-compose.yml               # Postgres + Qdrant + LiveKit
├── .github/workflows/               # CI
├── .gitignore
└── README.md                        # ← you are here
```

---

## 4. Key Technical Highlights

- **Hybrid document extraction.** Docling handles the structural pass; a VLM (Llama 3.2 90B Vision via NVIDIA NIM) recovers content that text-only OCR misses. A column detector reconciles the two when a multi-column layout confuses either one.
- **Per-room vector isolation.** Every interview room gets its own Qdrant namespace, so retrieval is bounded to *that candidate's* resume + transcript — no cross-candidate leakage.
- **Provider-agnostic AI stack.** LLM, VLM, STT, and TTS are all selected by env vars (`LLM_PROVIDER`, `VLM_PROVIDER`, `STT_PROVIDER`, `TTS_PROVIDER`). Default routes: OpenRouter Llama 3.3 70B, NVIDIA NIM Llama 3.2 90B Vision, Groq Whisper, Deepgram Aura.
- **Voice pipeline with phase management.** A LiveKit worker composes Silero VAD → STT → LLM (with a multi-phase state machine for intro / projects / technicals / behavioural / wrap-up) → TTS, streaming everything back over WebRTC.
- **Prompt-injection resistant.** A dedicated `sanitization.py` layer scrubs and validates candidate-supplied content before it reaches the interview LLM.
- **Verified links, not just trust.** 13 platform-specific scrapers (GitHub, GitLab, LeetCode stats, Codeforces, HackerRank, HackerEarth, Kaggle, StackOverflow, GeeksforGeeks, LinkedIn, Dev.to, Bitbucket, generic portfolio) cross-check the resume's claims and produce a verification dashboard.
- **Resume builder with AI bullets.** Template-injection engine rewrites achievement lines using role-aware LLM prompts and exports a polished PDF via `fpdf2`.
- **Roadmap as a graph.** A structured JSON roadmap with `nodes`, `depends_on` edges, and `tracks` is rendered client-side as a Mermaid mind-map plus a timeline view, with curated learning resources attached per node.
- **Recruiter NL search.** A natural-language filter (e.g. *"3+ years of Python, has Kaggle medals"*) is parsed into structured DB queries.
- **Async by default.** `asyncpg`, async SQLAlchemy, async FastAPI routes, async background tasks. No request ever blocks on a scrape or an LLM call.
- **Windows-dev friendly.** `run_dev.py` sets `FOR_DISABLE_CONSOLE_CTRL_HANDLER=1` and `WATCHFILES_FORCE_POLLING=1` to avoid the `forrtl: error (200)` crash that uvicorn's reload watcher triggers when TF is in the process tree.

---

## 5. Features

### Candidate-facing
- **Resume upload** (PDF / DOCX) with progress, validation, and re-upload flow.
- **Structured profile** auto-generated from the parsed resume.
- **Full analysis dashboard**: ATS score, missing sections, weak bullet detection, quantified-achievement coverage.
- **Project analyser**: stack detection, complexity tier, and impact scoring per project.
- **Role recommender**: matches the candidate against a curated role taxonomy with fit scores and skill-gap deltas.
- **Link verification page**: per-platform stats vs. resume claims, with a confidence badge.
- **Personalised learning roadmap**: tracks, nodes, dependencies, durations, milestones, and curated resources — viewable as a mind-map, a side panel, or a timeline.
- **AI resume builder**: rewrite, restructure, re-skin, and export a new PDF.
- **Mock voice interview**: lobby → live room → scored PDF report with a 6-axis radar chart.
- **Auth** (JWT), profile, and history of past interviews.

### Recruiter-facing (`/admin`)
- **Bulk candidate upload**.
- **Natural-language candidate search**.
- **Per-candidate interview history & reports**.
- **Role-gated routes** (admin-only `ProtectedRoute`).

### Cross-cutting
- **Rate limiting** via `slowapi`.
- **CORS** config driven by env.
- **Health endpoint** at `GET /api/health`.
- **OpenAPI docs** auto-generated at `/docs`.
- **Local infra** via `docker-compose` (Postgres, Qdrant, LiveKit).
- **Animated, smooth-scrolling UI** (Framer Motion + Lenis) with a clean, dark, recruiter-friendly aesthetic.

---

## 6. Tech Stack

### Frontend
- **React 19** + **TypeScript** + **Vite 8**
- **React Router v6** (with v7 future flags)
- **Tailwind CSS 3** + **PostCSS** + **Autoprefixer**
- **Framer Motion** (animation), **Lenis** (smooth scroll)
- **Zustand** (state), **Axios** (HTTP)
- **LiveKit Components React** + `livekit-client` (real-time room)
- **Mermaid** (mind-maps), **Recharts** (charts)
- **Lucide React** (icons), **clsx** + **tailwind-merge** (styling)

### Backend
- **Python 3.13**, **FastAPI**, **Uvicorn**
- **Async SQLAlchemy 2** + **asyncpg** (Postgres)
- **Pydantic v2** + **pydantic-settings**
- **Alembic** (migrations), **python-jose**, **passlib[bcrypt]**, **python-multipart** (auth & uploads)
- **Docling** (PDF/DOCX extraction)
- **sentence-transformers** + **HuggingFace** (embeddings)
- **llama-index** + **llama-index-vector-stores-qdrant** + **qdrant-client** (RAG)
- **OpenAI / OpenRouter / Groq** (LLM)
- **google-generativeai** (VLM template injection)
- **LiveKit Agents SDK** + `livekit-plugins-{deepgram,silero,openai,groq}` (voice)
- **LangChain** (`langchain-core`, `langchain-groq`, `langchain-openai`, `langchain-community`)
- **FAISS** (interview-specific vector store)
- **Playwright** + `playwright-stealth` (link analysis)
- **fpdf2** + **Matplotlib** (PDF + radar chart reports)
- **BeautifulSoup4**, **Kaggle** (scraping)
- **slowapi** (rate limiting), **aiofiles** (async IO), **httpx** (HTTP client)
- **Torch**, **Pillow** (vision backend)

### Infrastructure
- **PostgreSQL 15** (relational store)
- **Qdrant** (vector store, REST + gRPC)
- **LiveKit Server** (WebRTC SFU)
- **Docker Compose** for local dev

---

## 7. Scalability

RViewer AI is architected to scale along three axes — **concurrency**, **storage**, and **AI cost** — without rewriting the core.

### 7.1 Concurrency
- **Stateless web tier.** FastAPI is fully async and holds no in-process session state beyond a tiny `session_manager` for room lifetimes. Run it behind Gunicorn/Uvicorn workers, K8s pods, or a managed runtime and scale horizontally.
- **Voice workers are independent processes.** `run_agent.py` boots a LiveKit agent worker that auto-registers with the LiveKit server; add N workers and you can run N simultaneous interviews. Workers are pull-based, so K8s can autoscale on queue depth.
- **Background work doesn't block the API.** Indexing, scraping, and report generation run as background tasks; long operations stream progress over WebSockets.

### 7.2 Storage
- **Vector store is sharded by room.** Each interview room owns a Qdrant namespace, so reads are bounded to the candidate in focus. The same node can host thousands of rooms; for higher scale, switch Qdrant to **cluster mode** with sharded collections.
- **Postgres is the system of record.** Resumes, sessions, scores, and admin metadata all live there. Indexes are scoped per query path; for high write throughput, push hot paths (event logs, transcript chunks) to a time-series or queue and bulk-insert.
- **Local FS for files, S3-compatible for prod.** Raw uploads and generated PDFs are local in dev; in prod, swap the `UPLOAD_DIR` and `OUTPUTS_DIR` to S3/MinIO with a thin storage abstraction (already isolated to a few functions in `core/`).

### 7.3 AI cost & latency
- **Provider switching per env.** A regional LLM, a cheaper STT, a faster VLM — change a `.env` line, no code change.
- **Per-room retrieval budgets.** Retrieval is bounded by the room's own vector namespace, so cost is roughly constant per interview rather than growing with the global corpus.
- **Prompt caching & budget control.** The interview LLM service uses a phase-aware system prompt, and the roadmap/analysis prompts are cached on the resume hash, so the same candidate re-running a flow pays only for delta.

### 7.4 Operational scaling
- **Rate-limited APIs** (`slowapi`) protect against accidental LLM-bill blowups.
- **Health checks** are wired into `docker-compose` for every dependency, ready for K8s liveness probes.
- **Modular `core/` packages** mean any single stage (extraction, link analysis, voice, RAG) can be extracted into a microservice if load demands.

---

## 8. Getting Started

### Prerequisites
- **Node.js 20+**
- **Python 3.13**
- **Docker** + **Docker Compose**
- API keys for at least one provider in each category (LLM, VLM, STT, TTS)

### 1. Clone & configure
```bash
git clone <repo-url>
cd "Rviewer - ai"
cp server/.env.example server/.env   # then fill in keys
cp client/.env.example client/.env   # if present
```

### 2. Boot infrastructure
```bash
docker compose up -d                 # postgres :5433, qdrant :6333, livekit :7880
```

### 3. Backend
```bash
cd server
pip install -r requirements.txt
python init_db.py
python run_dev.py                    # FastAPI on http://127.0.0.1:8000
# In a second terminal:
python run_agent.py                  # LiveKit voice agent worker
```

### 4. Frontend
```bash
cd client
npm install
npm run dev                          # Vite on http://localhost:5173
```

### 5. Try it
1. Register at `http://localhost:5173/register`.
2. Upload a PDF resume.
3. Explore **Overview → Full Analysis → Links → Roadmap**.
4. Hit **Builder** to regenerate a polished PDF.
5. Hit **Interview** → start a room → speak with the AI interviewer.
6. Download the scored PDF report with the radar chart.

---

## 9. Environment Variables (selected)

| Key | Purpose | Default |
|---|---|---|
| `LLM_PROVIDER` / `LLM_API_KEY` / `LLM_MODEL` | Text generation | `openrouter` / `meta-llama/llama-3.3-70b-instruct` |
| `VLM_PROVIDER` / `VLM_API_KEY` / `VLM_MODEL` | Vision extraction | `nvidia` / `meta/llama-3.2-90b-vision-instruct` |
| `STT_PROVIDER` / `STT_API_KEY` / `STT_MODEL` | Speech-to-text | `groq` / `whisper-large-v3` |
| `TTS_PROVIDER` / `TTS_API_KEY` / `TTS_MODEL` | Text-to-speech | `deepgram` / `aura-helios-en` |
| `DATABASE_URL` | Postgres DSN | `postgresql+asyncpg://postgres:postgres@localhost:5433/rviewer` |
| `LIVEKIT_URL` / `LIVEKIT_API_KEY` / `LIVEKIT_API_SECRET` | WebRTC SFU | `ws://localhost:7880` / `devkey` / `secret` |
| `GITHUB_TOKEN` / `KAGGLE_USERNAME` / `KAGGLE_KEY` | Scraping auth | — |
| `MAX_FILE_SIZE_MB` | Upload limit | `10` |
| `VAD_THRESHOLD` / `VAD_MIN_SPEECH_MS` / `VAD_MIN_SILENCE_MS` | Voice activity detection | `0.8` / `250` / `300` |

---

## 10. Roadmap (project, not product)

- [ ] Multi-language resume support.
- [ ] Recruiter-side interview scheduling & calendar integration.
- [ ] Fine-tuned evaluator model for tighter scoring consistency.
- [ ] Tenant isolation at the DB level for SaaS deployment.
- [ ] WebSocket streaming for the analysis pipeline (true live progress).

---

## 11. License

Add your license of choice (MIT / Apache-2.0 / proprietary) here.

---

## 12. Acknowledgements

Built on top of **FastAPI**, **React**, **LiveKit**, **Qdrant**, **PostgreSQL**, **Docling**, **LlamaIndex**, **sentence-transformers**, **LangChain**, **Playwright**, **fpdf2**, **Mermaid**, **Framer Motion**, and the open-source AI community.
