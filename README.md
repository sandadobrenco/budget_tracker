# Budget Tracker

A small CLI-based **personal budget tracking** application built in Python.  
The main goals of the project are:

- to provide a simple local tool for tracking income, expenses and transfers;
- to demonstrate **two design patterns** in a realistic way:
  - **Factory Method** – for transaction creation
  - **Strategy** – for flexible reporting

## 1. Project Overview

The app lets you:

- define and use **transaction categories** (Income / Expense / Transfer)
- **add / list / update / delete** transactions
- generate several types of **budget reports**:
  - simple CLI summary
  - detailed CLI report with category breakdown
  - PDF report (simple or detailed) saved to disk
- keep an **audit** of generated reports and their filters in the database

Data is stored in a local **SQLite** database via SQLAlchemy + Alembic.  

---
## 2. Tech Stack

**Language & Runtime**

- Python 3.9+

**Main Libraries** :contentReference[oaicite:1]{index=1}  

- **SQLAlchemy** – ORM for database access
- **Alembic** – database migrations
- **Pydantic v2** – data validation & schemas
- **pydantic-settings + python-dotenv** – configuration & .env loading
- **Click** – command-line interface
- **Rich** – nice, colored CLI output and tables
- **FPDF** – generate PDF reports

Database:

- **SQLite** (file-based) via SQLAlchemy

---

## 3. Configuration (`.env`)

The project is configured via environment variables loaded from a `.env` file in the project root.  
Example `.env`: :contentReference[oaicite:2]{index=2}  

```env
APP_NAME=Budget Tracker
DEBUG=False

DATABASE_URL= your-db-url

LOG_LEVEL=DEBUG
TIMEZONE=Europe/Bucharest
DEFAULT_CURRENCY=RON

---

## 4. Commands to run the project 

python -m venv .venv
. .venv/Scripts/Activate.ps1
pip install -r requirements.txt

alembic upgrade head
python -m app.db.seed

CLI usage:

List all categories (transaction types):
python -m app.cli.main categories list

Filter by main type (INCOME, EXPENSE, TRANSFER):
python -m app.cli.main categories list --main-type INCOME
python -m app.cli.main categories list --main-type EXPENSE
python -m app.cli.main categories list --main-type TRANSFER

Add a transaction:
python -m app.cli.main transactions add 

Key options:

--type-id : ID from categories list (FK to transaction_types).

--amount : decimal value (e.g. 2500, 1200.50).

--currency : one of the supported currencies (e.g. RON, EUR, USD).

--date : date of the transaction in YYYY-MM-DD.

--recurring/--no-recurring : mark the transaction as recurring / non-recurring.

--recurrence : NONE|DAILY|WEEKLY|MONTHLY|YEARLY.

--description : free text description.

List Transactions:

python -m app.cli.main transactions list --limit 20

Shows a table with:

ID
date
amount
currency
transaction_type_id
recurring flag
recurrence type

Update transactions:
python -m app.cli.main transactions update

Any option you provide (--amount, --currency, --date, --recurring, --recurrence, --description, --type-id) will be updated; fields not provided remain unchanged.

Delete a transaction:
python -m app.cli.main transactions delete --id

Reports:

All report commands accept similar filters:

--start-date / --end-date (required) – period in YYYY-MM-DD

--main-type – optional (INCOME|EXPENSE|TRANSFER)

--category-id – can be repeated; filter by specific transaction_type IDs

--min-amount / --max-amount – numeric filters on amount

--recurring – include only recurring transactions

--currency – filter by currency and format amounts in that currency

Simple Report CLI:
python -m app.cli.main reports simple --start-date --end-date --currency 

Output includes:

total income
total expenses
balance
transaction count

Detailed Report CLI:
python -m app.cli.main reports detailed --start-date --end-date --currency 

Output includes:

SUMMARY (balance, total income, total expenses)
INCOME BY CATEGORY (category, total, number of transactions)
EXPENSES BY CATEGORY (category, total, number of transactions)

PDF Report:
# PDF based on simple report
python -m app.cli.main reports pdf --start-date  --end-date  --currency  --kind simple

# PDF based on detailed report
python -m app.cli.main reports pdf --start-date  --end-date  --currency  --kind detailed

Report history:
python -m app.cli.main reports history



---

Design Patterns

The project demonstrates two classic patterns: Factory Design Pattern and Strategy Design Pattern

Factory Method – Transaction Creation
The DatabaseTransactionFactory encapsulates how a Transaction object is created and initialized for different main transaction types:

INCOME

EXPENSE

TRANSFER

By centralizing creation in a factory, we can:
- keep service and CLI code simpler,
- extend behaviour (new transaction types, extra fields) by updating or subclassing the factory,
- follow the Open/Closed Principle (easier to extend without changing existing high-level code).


Strategy – Reporting System
In this app:

ReportService depends on the abstract AbstractReportStrategy:

strategy.generate(transactions, filters) -> Report

At runtime, different strategies can be injected:

SimpleReportStrategy → creates a minimal SimpleReport (totals & transaction count).

DetailedReportStrategy → builds a DetailedReport with category breakdown (INCOME and EXPENSE tables).

PDFReportStrategy → wraps another strategy (simple or detailed), delegates generation to it, then renders the result to a PDF file.

The CLI commands select the right strategy:

reports simple → uses SimpleReportStrategy.

reports detailed → uses DetailedReportStrategy.

reports pdf --kind simple|detailed → uses PDFReportStrategy(inner_strategy=Simple/Detailed).

Why it’s useful here:

- ullows to use different strategies to generate reports (simple summary vs. detailed breakdown, CLI vs. PDF).
- we can add a new report type later (e.g. weekly summary, CSV export, category-focused report) by:
- This keeps the reporting logic modular, testable, and easy to extend.