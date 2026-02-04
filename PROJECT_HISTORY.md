# Project History and Modification Log

This document serves as a comprehensive reference for the project's history, major modifications, and design decisions. It consolidates information from previous summaries and updates.

## 📅 Project Timeline & Phases

### Phase 1: Foundation & Data Configuration
**Goal:** Ensure the application runs consistently in both local and Docker environments, handling data sources correctly.

*   **Data Source Handling:**
    *   Implemented auto-detection logic in `dashboard/utils/config.py` to switch between local paths and Docker mount paths (`/app/data`).
    *   Updated `dashboard/config.json` to default to Docker-friendly paths while maintaining local compatibility.
*   **Docker Setup:**
    *   Modified `docker-compose.yml` to correctly mount the local `data/` directory to `/app/data` in the container.
    *   Ensured `Dockerfile` configurations were correct for the python environment.
*   **Documentation:**
    *   Created `DASHBOARD_SETUP.md` to guide users through setup and usage.

### Phase 2: Streamlit Dashboard Redesign
**Goal:** Align the Streamlit dashboard with provided wireframe specifications, focusing on Profit, Income, and Expense analysis.

*   **Home Page (`01_home.py`):**
    *   **Redesign:** Implemented a card-based layout for Income, Expense, and Net Profit.
    *   **Features:**
        *   "Profit by Month" section with current month focus.
        *   Clickable cards linking to detailed views.
        *   Daily performance chart (Income/Expense/Profit trends).
        *   Monthly Expenses table (Dec/Jan/Feb view).
*   **Income & Expense Pages (`04_income.py`, `05_expense.py`):**
    *   **New Pages:** Created dedicated pages for detailed breakdowns.
    *   **Variance Analysis:** Added tables showing Current Month vs Previous Month with percentage variance.
    *   **Visualizations:** Added pie charts for distribution and bar charts for top sources/categories.
*   **Navigation:**
    *   Streamlined sidebar navigation.
    *   Added `pages/` directory structure for multi-page Streamlit app.

### Phase 3: React Frontend Implementation
**Goal:** Create a modern React-based frontend mirroring the Streamlit dashboard's functionality.

*   **Backend API Expansion (`api/main.py`):**
    *   **New Endpoints:**
        *   `GET /api/home`: Aggregated data for the dashboard home (metrics, charts).
        *   `GET /api/income`: Detailed income ledger data with variance analysis.
        *   `GET /api/expense`: Detailed expense ledger data with variance analysis.
    *   **Response Models:** Defined Pydantic models (`HomeDataResponse`, `VarianceItem`, etc.) for structured API responses.
*   **Frontend Architecture (`frontend/src/`):**
    *   **Tech Stack:** React, TypeScript, Vite.
    *   **API Layer:** Created client, hooks (`useHome`, `useIncome`, `useExpense`), and type definitions to consume the new API.
    *   **Components:**
        *   `StatGrid`: For top-level metrics.
        *   `ChartCard`: Reusable wrapper for visualizations.
        *   `LoadingState` / `ErrorState`: For better UX.
    *   **Pages:**
        *   `HomePage`: Replicates Streamlit home view.
        *   `IncomePage` / `ExpensePage`: Detailed variance tables and charts.

---

## 📂 Detailed File Modifications

### Backend & Configuration

| File | Change Type | Description |
|------|-------------|-------------|
| `dashboard/config.json` | Modified | Updated `smb_share` path for Docker compatibility. |
| `dashboard/utils/config.py` | Modified | Added path auto-detection logic (Docker vs Local). |
| `docker-compose.yml` | Modified | Updated volume mappings (`./data:/app/data`). |
| `api/main.py` | Modified | Added endpoints for Home, Income, and Expense data; added Pydantic models. |

### Streamlit Dashboard (`dashboard/`)

| File | Change Type | Description |
|------|-------------|-------------|
| `pages/01_home.py` | Modified | Total UI overhaul: kpi cards, daily trend graph, monthly tables. |
| `pages/04_income.py` | Created | Detailed income analysis with variance tables. |
| `pages/05_expense.py` | Created | Detailed expense analysis with variance tables. |
| `utils/metrics.py` | Modified | Added specific calculation logic for variance and monthly aggregation. |

### React Frontend (`frontend/`)

| File | Change Type | Description |
|------|-------------|-------------|
| `src/api/types.ts` | Modified | Added interfaces for `VarianceItem`, `HomeDataResponse`, etc. |
| `src/api/hooks.ts` | Modified | Added React Query hooks for fetching dashboard data. |
| `src/pages/HomePage.tsx` | Created | Main dashboard view implementation. |
| `src/pages/IncomePage.tsx` | Created | Income breakdown view. |
| `src/pages/ExpensePage.tsx` | Created | Expense breakdown view. |

---

## 📊 Current System Architecture

The system now consists of two parallel frontend interfaces powered by the same data:

1.  **Streamlit App:**
    *   Directly reads Excel/CSV files.
    *   Best for quick internal analysis and data exploration.
    *   Located in `dashboard/`.

2.  **React App (Vite) + FastAPI:**
    *   FastAPI (`api/`) serves data as JSON.
    *   React App (`frontend/`) consumes API.
    *   Best for end-user experience, scalability, and modern UI.

## 📝 Reference Documents

For specific details, refer to these created logs:
*   `CHANGES_SUMMARY.md`: Details on initial Docker/Data setup.
*   `REACT_FRONTEND_UPDATE.md`: Specifics of the React/API work.
*   `SUMMARY.md`: Overview of the Streamlit Wireframe implementation.

---
*Last Updated: February 4, 2026*
