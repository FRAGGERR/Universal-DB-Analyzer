<div align="center">
  <h1>Database Reverse Engineering Analysis Tool</h1>
  
  <a href="https://www.python.org/"><img alt="Python" src="https://img.shields.io/badge/Python-3.8%2B-blue.svg"></a>
  <a href="https://nodejs.org/"><img alt="Node" src="https://img.shields.io/badge/Node.js-18%2B-3c873a.svg"></a>
  <a href="https://react.dev/"><img alt="React" src="https://img.shields.io/badge/Frontend-React-61dafb.svg"></a>
  <a href="https://expressjs.com/"><img alt="Express" src="https://img.shields.io/badge/Backend-Express-black.svg"></a>
  <a href="./LICENSE"><img alt="License" src="https://img.shields.io/badge/License-MIT-yellow.svg"></a>
  <a href="#security"><img alt="Security" src="https://img.shields.io/badge/Security-.env%20secured-brightgreen.svg"></a>
</div>

A tool that automatically analyzes database schemas, extracts metadata, and generates comprehensive insights for reverse engineering. It produces detailed Markdown/JSON reports and visual diagrams, and includes a full-stack web app to upload and analyze databases.

## Features

- Automatic schema discovery (tables, relationships, constraints)
- AI-powered analysis via Google Gemini API
- Business/architecture/performance insights with recommendations
- Consolidated Markdown and JSON reports with visual graphs
- Batch analysis script for multiple databases
- Web app for uploading DB files and viewing results

## Project Structure

The structure below mirrors this repository.

```
pocdatabase/
├── README.md
├── GRAPH_EMBEDDING_README.md
├── requirment.txt
├── analyze_all_databases.sh
├── analyze_any_database.py
├── demo_new_features.py
├── test_graph_embedding.py
├── universal_database_analyzer.py
├── New_DB/
│   ├── Chinook_Sqlite.sqlite
│   ├── sakila.db
│   └── superheroes.db
├── consolidated_analysis/
│   ├── Chinook_Sqlite_database_consolidated_analysis.json
│   ├── Chinook_Sqlite_database_consolidated_analysis.md
│   ├── sakila_database_consolidated_analysis.json
│   ├── sakila_database_consolidated_analysis.md
│   ├── superheroes_database_consolidated_analysis.json
│   ├── superheroes_database_consolidated_analysis.md
│   └── */*_graphs/ (PNG visualizations)
├── src/
│   ├── __init__.py
│   ├── main_analyzer.py
│   ├── analyzers/
│   │   ├── __init__.py
│   │   ├── gemini_analyzer.py
│   │   └── pattern_analyzer.py
│   ├── extractors/
│   │   ├── __init__.py
│   │   └── schema_extractor.py
│   └── visualizers/
│       ├── __init__.py
│       ├── consolidated_report_generator.py
│       └── graph_generator.py
└── web-app/
    ├── package.json
    ├── package-lock.json
    ├── vercel.json
    ├── vercel/
    │   └── api/upload.js
    ├── backend/
    │   ├── server.js
    │   ├── package.json
    │   ├── package-lock.json
    │   ├── env.example
    │   ├── middleware/
    │   │   ├── auth.js
    │   │   └── errorHandler.js
    │   ├── models/
    │   │   ├── Analysis.js
    │   │   └── User.js
    │   ├── routes/
    │   │   ├── analysis.js
    │   │   ├── auth.js
    │   │   ├── dashboard.js
    │   │   └── users.js
    │   ├── services/
    │   │   └── pythonAnalysisService.py
    │   ├── analysis_results/ (gitignored)
    │   ├── consolidated_analysis/ (gitignored)
    │   ├── reports/ (gitignored)
    │   └── uploads/ (gitignored)
    └── frontend/
        ├── public/
        │   ├── index.html
        │   ├── manifest.json
        │   └── favicon.ico
        ├── src/
        │   ├── index.js
        │   ├── App.js
        │   ├── index.css
        │   ├── components/
        │   │   └── (Auth, Layout)
        │   ├── pages/
        │   │   ├── Analysis/ (AnalysisPage.js, AnalysisDetailPage.js, ...)
        │   │   ├── Auth/ (LoginPage.js, RegisterPage.js)
        │   │   ├── Dashboard/ (DashboardPage.js)
        │   │   ├── Explore/ (ExplorePage.js)
        │   │   ├── Profile/ (ProfilePage.js)
        │   │   ├── Test/ (TestPage.js)
        │   │   └── Upload/ (UploadPage.js, WorkingUploadPage.js, ...)
        │   ├── services/ (analysisService.js, authService.js, geminiAnalysisService.js)
        │   └── store/ (store.js, slices/*)
        ├── package.json
        └── package-lock.json
```

## Getting Started

### 1) Python environment

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirment.txt
```

### 2) Web app

```bash
# Backend
cd web-app/backend
npm install
cd ../../..

# Frontend
cd web-app/frontend
npm install
cd ../../..
```

## Configuration

Create a `.env` in the project root for analysis scripts:

```bash
GEMINI_API_KEY=your_gemini_api_key
```

Backend example env (see `web-app/backend/env.example`):

```bash
JWT_SECRET=your_jwt_secret
GEMINI_API_KEY=your_gemini_api_key
PYTHON_PATH=python3
```

Frontend example env (create `web-app/frontend/.env` locally):

```bash
REACT_APP_API_URL=http://localhost:5001/api
REACT_APP_GEMINI_API_KEY=your_gemini_api_key
```

## Usage

Analyze a single database:

```bash
python analyze_any_database.py New_DB/sakila.db
```

Batch analysis of all databases in `New_DB/`:

```bash
chmod +x analyze_all_databases.sh
./analyze_all_databases.sh
```

## Outputs

- Markdown and JSON under `consolidated_analysis/`
- Visual graphs inside per-database `*_graphs/` folders
- Web app backend stores run artifacts in `web-app/backend/analysis_results/` (gitignored)

## Security

- Secrets are not committed. `.gitignore` excludes `.env`, uploads, analysis outputs, and builds.
- Keep real API keys only in local environment files or deployment secrets.

## License

MIT
