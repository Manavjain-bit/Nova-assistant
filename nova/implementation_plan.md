# Implementation Plan: AI Voice Personal Assistant (Nova)

This plan outlines the architecture, database schema, and phased implementation for building **Nova**, a production-ready AI Voice Personal Assistant. Nova will feature a React/Next.js frontend with high-end premium animations and a FastAPI backend with PostgreSQL, Redis, and AI integrations (GPT, Whisper, TTS) alongside advanced local modules (Task Manager, Reminder System, Habit/Goal Trackers, Google Calendar/Gmail integrations, and File Search).

---

## Architecture & Design Decisions

### 1. High-Level Architecture
Nova will use a decoupled client-server architecture:
* **Frontend**: Next.js (App Router), TypeScript, TailwindCSS, Zustand for state management, React Query for server state, Framer Motion for Apple-like animations, and Lucide icons.
* **Backend**: FastAPI (Python 3.10+), SQLAlchemy for ORM, PostgreSQL for relational storage, Redis for rate limiting, caching, and chat session locks, and APScheduler for running scheduled/recurring reminders.
* **AI Engine**: Python wrappers around OpenAI (GPT-4o/o1 for core assistant, Whisper for STT, OpenAI TTS or ElevenLabs for voice output).
  * *Robustness Fallbacks*: If OpenAI/ElevenLabs API keys are not supplied, Nova will gracefully degrade to use a lightweight local rule-based/NLP planner (using simple semantic matchers) and browser-based Web Speech API (SpeechRecognition and SpeechSynthesis) for voice control.
* **Deployment/Containerization**: Docker Compose running the frontend, backend, PostgreSQL database, and Redis.

### 2. Relational Database Schema
We will define a single, well-indexed database schema containing the following models:
* `users`: Auth credentials, OAuth details, preferences, profile configurations.
* `tasks`: ID, user_id, title, description, status, priority, due_date, recurrence (JSON/string), parent_id (for subtasks), category, estimated_duration, priority_score, created_at, updated_at.
* `habits`: ID, user_id, name, category, custom_rules, streak_count, last_completed_date, created_at.
* `habit_logs`: ID, habit_id, date, status (completed/missed).
* `goals`: ID, user_id, title, description, type (long-term/short-term), progress_percentage, deadline, created_at.
* `milestones`: ID, goal_id, title, description, is_completed, due_date.
* `reminders`: ID, user_id, title, type (one-time/recurring), cron_expression, next_trigger, voice_path, email_notification, is_sent, metadata (e.g. coordinates for future location reminders).
* `notes`: ID, user_id, title, content (rich text), is_pinned, tags (array), voice_url, created_at, updated_at.
* `conversations`: ID, user_id, summary, created_at.
* `messages`: ID, conversation_id, sender (user/assistant), text_content, audio_url, created_at.
* `memory_entries`: ID, user_id, key (e.g. name, preferences, friend_list), value, category (short-term/long-term/summarized), last_accessed.
* `notifications`: ID, user_id, title, message, is_read, created_at.

---

## User Review Required

> [!IMPORTANT]
> **API Keys & Integrations**: For local execution, the system will use sandbox/mock files for Gmail, Google Calendar, and File Search (e.g., scanning a designated workspace directory) to ensure it works without requiring active GCP client credentials immediately.
>
> **Voice Wake Word**: The wake-phrase "Hey Nova" will be supported client-side using the Web Speech API's continuous listening features. This avoids needing complex, platform-specific local model training (like PocketSphinx) in the web container.

---

## Proposed Changes

The codebase will be organized under the following enterprise structure:
* `frontend/`: Next.js App Router codebase.
* `backend/`: FastAPI backend with SQLAlchemy, routers, services, and tests.
* `database/`: Database configuration and migration scripts (Alembic).
* `docker/`: Dockerfiles and docker-compose configurations.
* `docs/`: Markdown documentation (ER Diagram, API Specs, Deployment).
* `tests/`: Test suites for both frontend and backend.
* `scripts/`: Automation scripts (db seeding, dev environment helpers).

---

### Phase 1: Base Project Setup, Database Schema, & Security
* Create Python backend project structure, dependencies (`requirements.txt`), and Dockerfiles.
* Create Next.js frontend with Tailwind and Zustand.
* Set up SQLAlchemy DB configuration, models, Alembic migrations, and SQLite fallback for local test execution.
* Implement JWT-based auth (register, login, password encryption) and Google OAuth route stubs.

### Phase 2: Task Manager & AI Smart Prioritization
* Develop REST APIs for Task Manager: CRUDS for tasks, subtasks, categories, and deadlines.
* Build Smart Prioritization engine: An algorithmic prioritize-ranking helper that scores tasks using urgency, importance, due date, estimated duration, and dependency constraints.
* Set up unit tests for task management and prioritization.

### Phase 3: Reminder System & Scheduler
* Setup APScheduler background thread in FastAPI.
* Implement natural language reminder parser: Parses query strings like *"Remind me to call Rahul tomorrow after lunch"* using regex and simple semantic rules or LLM function calling, calculating the next trigger timestamp.
* Implement desktop/browser notification dispatching.

### Phase 4: Goals, Habits, Notes, & Mock integrations
* Implement Goal and Habit trackers (CRUD, streak metrics, logs, milestone tracking).
* Implement Notes API (pinned notes, text searches, tags).
* Integrate Gmail & Google Calendar connectors: Create structured service classes. By default, they will access a simulated internal mail and event calendar database if GCP credentials are not active.
* Implement File Search service: Scans the user's workspace directory (filtering for PDF, images, TXT files) and indexes filenames/contents.

### Phase 5: AI Engine, Memory Manager, & Daily Briefing / Night Review
* Create the AI core service (`backend/app/services/ai.py`) wrapping OpenAI GPT.
* Implement Memory Manager:
  * **Short-Term Memory**: Retains the last $N$ turns of the conversation.
  * **Long-Term Memory**: Automatically extracts key user facts (e.g., name, friends, work, preferences) and saves them in the `memory_entries` table.
  * **Summarization**: Compresses old history when the token threshold is exceeded.
* Build Daily Briefing generator (Morning weather, schedule, workload summary) and Night Review prompt (Mood, productivity, auto-task update).

### Phase 6: Voice Assistant (STT / TTS)
* Connect Web Speech API Speech-to-Text in the frontend dashboard.
* Implement wake-word detection ("Hey Nova") locally in browser.
* Connect OpenAI TTS / ElevenLabs backend endpoints for vocal responses. Provide standard HTML5 Web Speech Synthesis API fallback if credentials are absent.

### Phase 7: Next.js Frontend Dashboard UI
* Build the premium Apple-like Dashboard using TailwindCSS and Framer Motion.
* Include visual sections: Today's Schedule, Tasks, Habit circles, Goal tracker rings, Notes list, Calendar, Daily Briefing visual cards, and a large glowing circular AI Voice Assistant Button with continuous voice waves.
* Add dark/light mode toggle.

### Phase 8: Verification & Packaging
* Verify 90%+ code coverage on core routes.
* Package Docker Compose configuration for one-click setup.
* Add documentation, deployment guide, and example environment variables.

---

## Verification Plan

### Automated Tests
* Run pytest: `pytest backend/app/tests`
* Run frontend lint and tests: `npm run lint && npm run test`

### Manual Verification
* Access dashboard on `http://localhost:3000` to interact with voice button, tasks, habits, and AI chat.
* Test voice wakeup in browser.
