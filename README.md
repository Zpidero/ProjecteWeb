# FutDraft — Inazuma Eleven Draft Web

A web application built with Django 6 that lets users explore players and teams from the *Inazuma Eleven* universe, build custom draft lineups, and save them to their profile.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Data Models](#data-models)
- [Setup & Installation](#setup--installation)
- [Running with Docker](#running-with-docker)
- [URL Routes](#url-routes)
- [12-Factor Compliance](#12-factor-compliance)
- [Known Issues / TODOs](#known-issues--todos)

---

## Overview

FutDraft is a fan-made interactive web game inspired by the FIFA FUT Draft mechanic, themed around *Inazuma Eleven*. Users are presented with randomised player choices (filtered by position and power tier), select their squad, choose a formation, name their draft, and save it for later viewing.

Player and team data is fetched from the public REST API and **synced into the local database** via management commands, eliminating all real-time API calls during normal usage:
`https://inazumaeleven-api.onrender.com`

---

## Features

- 🔍 **Player Browser** — Search and filter all Inazuma Eleven players by position, element, archetype, gender, role, age group, school year, and minimum total stats. Paginated (20 per page).
- 🏟️ **Team Browser** — Browse teams with images, paginated and searchable by name.
- 🎲 **Draft Game** — Pick one player per round from 5 random options grouped by power tier. All data served from local DB — no API latency.
- 📋 **My Drafts** — View saved draft lineups with formation and players displayed on a pitch.
- 👤 **User Accounts** — Register, log in, and upload a profile picture.
- 🔧 **Django Admin** — Full admin interface to add, modify and delete all model instances.
- 🐳 **Docker + Docker Compose** — Fully containerised for easy deployment and team collaboration.
- 🌍 **12-Factor compliant** — Secret key and configuration managed via environment variables.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Django 6.0.3 |
| Language | Python 3.14 |
| ASGI Server | Uvicorn 0.41.0 |
| Database | SQLite (via Django ORM) |
| Image Handling | Pillow 12.2.0 |
| Frontend | HTML + Tailwind CSS |
| Containerisation | Docker + Docker Compose |
| Package Manager | uv |
| Config management | python-decouple |
| External API | inazumaeleven-api.onrender.com |

---

## Project Structure

```
DjangoProject1/
├── DjangoProject1/             # Django project config
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
├── myapp/                      # Main application
│   ├── models.py               # Teams, Players, Lineup, Profile, Futdraft
│   ├── views.py                # All view logic (DB-only, no live API calls)
│   ├── urls.py                 # App URL patterns
│   ├── forms.py                # User registration form
│   ├── admin.py                # Django admin registration
│   ├── management/
│   │   └── commands/
│   │       ├── sync_players.py # Sync all players from API → DB
│   │       └── sync_teams.py   # Sync all teams + images from API → DB
│   └── migrations/
├── templates/
│   ├── base.html
│   ├── components/
│   └── myapp/
├── static/
│   ├── css/
│   └── images/
│       ├── elements/           # Element PNG icons (local)
│       └── teams/              # Local team shield fallback image
├── .env.example                # Environment variable template (commit this)
├── .env                        # Actual secrets (never commit)
├── Dockerfile
├── docker-compose.yml
├── manage.py
└── pyproject.toml
```

---

## Data Models

### `Players`
Stores player data synced from the external API.
Fields: `name`, `nickname`, `position`, `element`, `archetype`, `team (FK)`, `power`, `control`, `technique`, `pressure`, `physical`, `agility`, `intelligence`, `total`, `age_Group`, `school_Year`, `gender`, `role`, `image`.

### `Teams`
Stores team name and image URL (nullable). Populated by `sync_teams`.

### `Lineup`
Represents a formation (e.g. `4-3-3`): `forwards`, `midfielders`, `defenders`, `goalKeeper`.

### `Profile`
One-to-one extension of Django's built-in `User`, storing a profile picture.

### `Futdraft`
A saved draft: links a `User`, a `Lineup`, and a set of `Players` (ManyToMany). Stores `player_order` as JSON to preserve pick order.

---

## Setup & Installation

### Prerequisites

- Python 3.14+
- [uv](https://github.com/astral-sh/uv) package manager

### Local Setup

```bash
# 1. Clone the repository
git clone <repo-url>
cd DjangoProject1

# 2. Copy and configure environment variables
cp .env.example .env
# Edit .env and set SECRET_KEY

# 3. Install dependencies
uv sync

# 4. Apply migrations
uv run manage.py migrate

# 5. Sync data from API into DB (one time)
uv run manage.py sync_players
uv run manage.py sync_teams

# 6. Run the development server
uv run manage.py runserver
```

---

## Running with Docker

```bash
# 1. Copy and configure environment variables
cp .env.example .env

# 2. Build and start
docker compose up --build
```

The app will be available at `http://localhost:8000`. Data sync runs automatically on container start.

To run manually inside the container:
```bash
docker compose exec django uv run manage.py sync_players
docker compose exec django uv run manage.py sync_teams
```

---

## URL Routes

| URL | View | Description |
|---|---|---|
| `/` | `home` | Landing page |
| `/game/` | `game_view` | Draft game (login required) |
| `/players/` | `players_list` | Player browser (paginated, filterable) |
| `/teams/` | `teams_list` | Team browser (paginated, searchable) |
| `/player/<id>/` | `player_detail` | Player detail page |
| `/teams/<n>/` | `team_detail` | Team detail + squad list |
| `/random-players/` | `get_random_players` | JSON endpoint for the draft game |
| `/save-draft/` | `save_draft` | Save a completed draft (POST, login required) |
| `/my-drafts/` | `my_drafts` | View saved drafts (login required) |
| `/register/` | `register_view` | User registration |
| `/login/` | `login_view` | User login |
| `/admin/` | Django admin | Full admin interface |

---

## 12-Factor Compliance

| Factor | Implementation |
|---|---|
| Config | `SECRET_KEY` via environment variable (`python-decouple`, `.env` file) |
| Dependencies | Declared in `pyproject.toml`, locked in `uv.lock` |
| Backing services | SQLite configurable via `DATABASES` setting |
| Build/run separation | Docker image build vs. runtime sync commands |
| Dev/prod parity | Docker Compose ensures identical environments across team members |

---

## Known Issues / TODOs

- **Power tier filtering** — certain positions may not have players in all defined power ranges; the view falls back gracefully but ranges could be tuned per-position.
- **SQLite in production** — should be replaced with PostgreSQL for multi-user deployments.
- **Media files** — profile images are stored locally; a cloud storage backend should be used in production.
- **`DEBUG = True`** — must be set to `False` and `ALLOWED_HOSTS` restricted before any public deployment.
