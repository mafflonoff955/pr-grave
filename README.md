# PR Graveyard

> X-Ray your GitHub repository. Expose the hidden cost of developer friction.

## What it does

Analyzes PR review patterns and CI/CD performance to calculate the dollar cost of developer workflow friction. Includes a What-If simulator to show how much your team would recover by improving key metrics.

## Tracks

- Track G: Code Review Radar
- Track A: Build & CI Scanner (cross-track integration)

## Tech Stack

- **Frontend**: React + Vite + Recharts + Tailwind CSS
- **Backend**: Python FastAPI
- **Data**: GitHub REST API v3 (no database needed)
- **Auth**: GitHub Personal Access Token (PAT) via .env

## Setup

1. Clone this repo
2. Copy `.env.example` → `.env`, add your GitHub token
3. Install Python dependencies:
   ```bash
   cd server
   pip install -e .
   ```
4. Install frontend dependencies:
   ```bash
   cd client
   npm install
   ```
5. Run the backend:
   ```bash
   cd server
   python -m uvicorn app.main:app --reload --port 3001
   ```
6. Run the frontend:
   ```bash
   cd client
   npm run dev
   ```
7. Open http://localhost:5173

## GitHub Token

Create a free token at https://github.com/settings/tokens

- For **public repos**: no scopes needed
- For **private repos**: require `repo` scope

## Project Structure

```
pr-graveyard/
├── client/                      # React frontend
│   ├── src/
│   │   ├── components/
│   │   │   ├── RepoInput.jsx
│   │   │   ├── ScanProgress.jsx
│   │   │   ├── Dashboard.jsx
│   │   │   ├── SummaryCards.jsx
│   │   │   ├── ReviewerHeatmap.jsx
│   │   │   ├── CIBottlenecks.jsx
│   │   │   └── WhatIfSimulator.jsx
│   │   ├── App.jsx
│   │   └── main.jsx
│   └── package.json
├── server/                      # Python FastAPI backend
│   ├── app/
│   │   ├── routes/
│   │   │   ├── github.py        # GitHub API wrapper
│   │   │   └── analyze.py       # Main analysis endpoint
│   │   ├── lib/
│   │   │   ├── pr_analyzer.py   # PR metric calculations
│   │   │   ├── ci_analyzer.py   # CI/CD metric calculations
│   │   │   └── cost_calc.py    # Dollar cost calculations
│   │   ├── config.py
│   │   └── main.py
│   └── pyproject.toml
├── .env.example
└── README.md
```

## API

**POST `/api/analyze`**

Request:
```json
{
  "repoUrl": "facebook/react",
  "teamSize": 8,
  "hourlyRate": 75
}
```

Note: `repoUrl` accepts either `owner/repo` format (e.g. `facebook/react`) or a full GitHub URL (e.g. `https://github.com/facebook/react`).

Response:
```json
{
  "repo": "facebook/react",
  "scannedAt": "2026-03-30T20:00:00",
  "prMetrics": {
    "totalPRs": 50,
    "avgTimeToFirstReview": 14.3,
    "avgTimeToMerge": 48.7,
    "largePRs": 7,
    "reviewerLoad": { ... }
  },
  "ciMetrics": {
    "totalRuns": 142,
    "failureRate": 18.5,
    "avgDurationMinutes": 8.3,
    "workflows": [ ... ]
  },
  "costAnalysis": {
    "breakdown": { ... },
    "totalWastedHoursPerMonth": 348,
    "totalWastedDollarsPerMonth": 26100
  },
  "prsAnalyzed": 50,
  "prsLastMonth": 23
}
```
