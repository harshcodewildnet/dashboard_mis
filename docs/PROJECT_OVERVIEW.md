# Tally-MIS Project Overview

This document provides a concise, comprehensive overview of the Tally-MIS project. It is intended as a single source to feed into GPT or other tools to generate documentation and plan next steps.

## What This Project Does

Tally-MIS is a utility and dashboard suite that exports accounting and inventory data from Tally Prime via its XML server, normalizes it into relational tables, loads it into a chosen database, and offers reporting and dashboards for analysis and MIS.

- Extracts master and transaction data from Tally Prime using TDL/XML.
- Normalizes hierarchical Tally data into RDBMS tables with consistent schemas.
- Loads into SQL Server, PostgreSQL, MySQL/MariaDB, or Google BigQuery. Also supports CSV/JSON/ADLS.
- Provides a Streamlit dashboard and an Excel-based MIS pipeline for reporting.
- Ships with a library of SQL reports for multiple platforms.

## Architecture Overview

- Tally Prime XML Server (source): exports data described in YAML (`tally-export-config*.yaml`).
- Node.js/TypeScript Loader (`src/`): reads XML from Tally, transforms, and writes to target DB.
- Database Schemas: platform-specific SQL scripts in `platform/<db>/` and root `database-structure*.sql`.
- Dashboard (`dashboard/`): Python Streamlit app reading the relational schema and rendering visuals; includes MIS pipeline to generate Excel reports.
- Containerization: Multi-stage Dockerfile for the loader, and a `docker-compose.yml` that brings up Postgres, the loader (dev), and the dashboard.

High-level data flow:

1. Tally Prime serves XML over TCP (default port 9000).
2. The loader requests master/transaction data per YAML definition.
3. Data is normalized and inserted into relational tables.
4. Dashboard and SQL reports query the loaded tables for analysis.

## Repository Layout

- Root
  - `README.md`: User guide, requirements, setup, and usage.
  - `config.json`: Primary configuration (DB connection + Tally options).
  - `tally-export-config.yaml` / `tally-export-config-incremental.yaml`: Tally export specs; choose per sync mode.
  - `database-structure.sql` / `database-structure-incremental.sql`: Base relational schema for full/incremental modes.
  - `docker-compose.yml`, `Dockerfile`: Containerization and dev orchestration.
  - `run.bat`, `run-gui.bat`, `gui.html`: CLI and browser-based config UI.
  - `reports/`: Portable SQL report queries for BigQuery and MSSQL.
  - `platform/`: Per-DB structure and view scripts (duckdb, bigquery, mysql, postgresql, etc.).
  - `src/`: Node/TypeScript loader sources (`*.mts`, ES modules) and `tsconfig.json`.
  - `dashboard/`: Streamlit app, MIS pipeline, Python requirements.
  - `docs/`: Deep-dive docs on data structure, options, BigQuery, FAQ, and release history.

## Core Components

- Loader (Node/TypeScript):
  - Uses `js-yaml`, `tedious` (MSSQL), `pg` + `pg-copy-streams` (Postgres), `mysql2`, `@google-cloud/bigquery`, and `ws`.
  - Multi-stage Docker build compiles TS and runs dev (`nodemon`/`tsx`) or production (`node dist/index.mjs`).
  - Controlled by `config.json` and the YAML export config.

- Dashboard (Streamlit):
  - App: `dashboard/app.py` connects to Postgres (from docker-compose) and renders pages: Home, Sales Analysis, Ledger Explorer, Voucher Relations, Raw Data, MIS Reports, Mappings.
  - MIS Pipeline: `dashboard/mis_pipeline/main.py` orchestrates ETL → canonical models → aggregations → Excel (`MIS_Report.xlsx`).
  - Mapping files (`ledger_mapping.xlsx`, `cost_centre_mapping.xlsx`) can be edited via UI.

- Reports:
  - SQL queries under `reports/` for popular dashboards (trial balance, sales/purchase registers, profit-loss, ledger views) across BigQuery and MSSQL.

## Data Model Highlights

Tally’s hierarchical data is flattened into relational tables. Key concepts:

- GUID: Every entity row in Tally has a GUID; used as the primary linkage across tables.
- Master tables (prefixed `mst_`): `mst_group`, `mst_ledger`, `mst_vouchertype`, `mst_uom`, `mst_stock_item`, etc.
- Transaction tables (prefixed `trn_`): `trn_voucher` (header), derived tables `trn_accounting`, `trn_inventory`, `trn_bill`, `trn_bank`, `trn_cost_centre`, `trn_batch`.
- Signs: In `trn_accounting.amount`, negative = debit, positive = credit. In `trn_inventory.quantity`, negative = outward, positive = inward.
- Logical fields: Many boolean-like fields are numeric (0/1) for cross-DB compatibility (e.g., `is_order_voucher`).
- Relationships: One-to-many links across voucher → entries and master ↔ transaction (see `docs/data-structure.md`).

Special handling:

- Order vouchers (`is_order_voucher = 1`) have no accounting or inventory impact; filter when calculating balances.
- Inventory workflows: GRN/GDN vs Purchase/Sales impact varies by process rigor; use `tracking_number` logic to avoid double-counting in partial workflows.
- Closing balances and closing stock need computed logic explained in `docs/data-structure.md`.

## Configuration

`config.json` has two key sections:

- Database:
  - `technology`: `mssql` | `mysql` | `postgres` | `bigquery` | `adls` | `json` | `csv`.
  - `server`, `port`, `ssl`, `schema`, `username`, `password`.
  - `loadmethod`: `insert` (safe, slower) or `file` (fast, local-only).

- Tally Options:
  - `definition`: export config file (`tally-export-config.yaml` or `tally-export-config-incremental.yaml`).
  - `server`, `port` (default 9000), `company`.
  - Date window: `fromdate`/`todate` (`YYYYMMDD` or `auto`).
  - `sync`: `full` | `incremental`.
  - `frequency`: minutes between incremental sync checks (0 disables repeat).

## Sync Modes

- Full Sync:
  - Use `database-structure.sql` and `tally-export-config.yaml`.
  - Set `sync` to `full`. Use explicit `fromdate`/`todate` or `auto`.

- Incremental Sync:
  - Use `database-structure-incremental.sql` and `tally-export-config-incremental.yaml`.
  - Set `sync` to `incremental` and `frequency` > 0.
  - Supported: SQL Server, MySQL/MariaDB, PostgreSQL (not BigQuery due to update cost).
  - Limitations: Keep period to a single FY, avoid manual deletes, ensure correct DB name, and perform an initial full sync with `auto` period and `frequency=0`.

## Running the Project

Prerequisites:

- Windows 10, Tally Prime, Node.js, target Database Server (or Docker).
- Enable Tally XML Server: Help → Settings → Connectivity → Client/Server → Both.

Options:

1) Command-line loader:

- Configure `config.json` and ensure the target database exists with tables from `database-structure*.sql`.
- Start Tally Prime with the target company active.
- Run `run.bat` (single-shot); check `logs/import-log.txt` and `logs/error-log.txt`.

2) Browser-based UI:

- Run `run-gui.bat` and use `gui.html` to edit/send config.

3) Docker Compose (recommended for dev):

- Spins up Postgres (`tally-db`), loader (`tally-loader` dev), and dashboard (`tally-dashboard`).

```bash
docker compose up --build
```

- Dashboard available at http://localhost:8501.
- Postgres is mapped on `localhost:5444` (container port 5432).
- Source and config files are mounted for live iteration.

## Dashboard Features (Streamlit)

- Pages: Home (KPIs, recent vouchers), Sales Analysis (monthly/group), Ledger Explorer, Voucher Relations, Raw Data, MIS Reports (Excel generation), Mappings (cost centre & ledger groups).
- Uses SQL joins consistent with the data structure rules (filters out order vouchers, handles groupings).
- MIS pipeline generates Excel files with sales/expenses by month, inventory summaries, employee cost, P&L, and raw dumps.

## SQL Reports Library

- `reports/*` includes vendor-specific SQL for common accounting views: ledger, voucher views, trial balance, profit/loss, sales/purchase registers, stock summaries, etc.
- BigQuery queries optimized for Data Studio and Google Sheets integration.

## Known Issues & Notes

- Tally Prime only; Tally.ERP 9 support removed.
- Rare issues when multiple companies are selected and a specific company is targeted.
- Long-running Tally instances may need a restart for freshness.
- For Windows Task Scheduler automation, keep the user session connected (don’t log off).

## Development Notes

- Node project is `type: module` with `.mts` sources; built via `tsc`.
- Dockerfile has three stages: builder (compile), dev (nodemon+tsx), production (run `dist/index.mjs`).
- `package.json` dependencies include DB clients and YAML parsing; types are in `devDependencies`.
- Streamlit dashboard uses SQLAlchemy; python deps in `dashboard/requirements.txt`.

## Quick Start (Dev, Docker Compose)

1. Ensure Docker is installed and running.
2. Set `config.json` for `postgres` (`server: db`, `port: 5432`, `schema: tallydb`, `username: postgres`, `password: password`).
3. Start services:

```bash
docker compose up --build
```

4. Open the dashboard at http://localhost:8501.
5. Load data via the loader (dev service watches `src/` for changes).

## Next Steps (Suggestions)

- Add automated tests for loader transformations and dashboard queries.
- Implement incremental sync strategy for BigQuery (or document safe alternatives).
- Provide CI workflows (lint, build, Docker image, basic integration checks).
- Expand `docs/` with troubleshooting for common DB/Tally connectivity issues.
- Add Power BI/Tableau templates referencing the relational schema.
- Harden `config.json` handling (env vars or secrets) and add validation.
- Review and optimize `loadmethod` pathways (`file` vs `insert`) per target DB and environment.

## References

- User Guide: `README.md`
- Data Structure Guide: `docs/data-structure.md`
- Incremental Sync: `docs/incremental-sync.md`
- Command-line Options: `docs/commandline-options.md`
- BigQuery Notes: `docs/google-bigquery.md`
- FAQ & Releases: `docs/faq.md`, `docs/release-history.md`
