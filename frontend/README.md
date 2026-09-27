# FinSightAI Frontend

This is the simplified frontend for the FinSightAI platform, built purely with HTML, CSS, and Vanilla JavaScript. 

It was specifically designed to be lightweight, easy to understand, and framework-free, while preserving the exact layout and look of the original application.

## Structure

```
frontend/
├── index.html            # Dashboard page
├── finance.html          # Finance overview
├── reconciliation.html   # Reconciliation anomalies
├── ai.html               # FinSight AI Copilot
├── css/
│   └── style.css         # Core styles, design tokens, and layout classes
└── js/
    └── api.js            # Vanilla JS fetch wrappers for backend communication
```

## Running the Application

You do not need a separate frontend development server. 

The frontend is served directly by the FastAPI backend via `StaticFiles`. To run the full application (frontend + backend API), run the following command from the root `FinsightAI` directory:

```bash
python -m uvicorn backend.app.main:app --reload
```

Then visit [http://127.0.0.1:8000](http://127.0.0.1:8000).

## Architecture

- **HTML/CSS/JS**: No React, Vite, or npm build step.
- **Styling**: `style.css` contains the design tokens and layout classes.
- **Data Fetching**: `api.js` uses native `fetch()` to call the FastAPI backend endpoints (e.g., `/api/v1/sales/`).
- **AI Chat**: `ai.html` communicates directly with `/api/v1/ai/chat` using `fetch()` and renders AI markdown responses using `marked.js` from a CDN.
