# Water Body Encroachment Complaint System
### Using Knowledge-Based Agent, Forward Chaining and Constraint Satisfaction

A full-stack, AI-driven public grievance and ecological protection system designed to detect, analyze, and track suspected encroachment onto lakes, ponds, canals, and protected water bodies using **symbolic, Knowledge-Based Artificial Intelligence (Forward Chaining & CSP)** with **PostgreSQL** storage.

---

## 🏛️ Project Highlights

- **Citizens**: Register, file complaints with geolocation picker, upload photographic evidence, track AI reasoning trace, and view status history.
- **Symbolic AI Engine**:
  - **Forward Chaining**: Infers whether reports qualify as *Possible Encroachment* requiring *Official Verification* through verifiable logical rules.
  - **Backward Chaining**: Goal-directed reasoning explaining why a specific conclusion was reached.
  - **Constraint Satisfaction (CSP)**: Backtracking search to match complaints to the appropriate government department (Revenue, Municipal, Water Resources, Pollution Board) based on jurisdiction, water body type, and caseload constraints.
  - **A\* Pathfinding (Optional)**: Calculates inspection routes from regional offices to complaint sites.
- **Authorities**: Dashboard with live GIS map (Leaflet.js), AI explanation inspector, verification status transitions, remarks logging, and reassignment controls.
- **Zero Black-Box ML**: Built purely with explainable, deterministic classical AI algorithms.
- **Database**: **PostgreSQL** with `psycopg` driver & SQLAlchemy ORM.

---

## 📂 Project Structure

```text
├── backend/
│   ├── app.py                      # Flask Application entry point
│   ├── config.py                   # App & PostgreSQL / SQLAlchemy configuration
│   ├── database.py                 # DB connection & ORM/Session management
│   ├── models/                     # User, Complaint, WaterBody, Authority, Evidence, History
│   ├── routes/                     # Blueprint routes (auth, complaints, ai, etc.)
│   ├── services/                   # Complaint & GIS services
│   ├── ai/                         # Knowledge Base, Forward/Backward Chaining, CSP, A*
│   ├── utils/                      # Password helpers, file upload validators
│   └── tests/                      # Pytest unit tests for AI and APIs
├── frontend/
│   ├── templates/                  # Jinja2 HTML templates (Citizen & Authority)
│   └── static/                     # CSS styles, Leaflet map scripts, visual explainer
├── database/
│   ├── schema.sql                  # PostgreSQL database schema (DDL)
│   └── seed.sql                    # Initial demo records (lakes, authorities, rules)
├── requirements.txt                # Python package dependencies (Flask, SQLAlchemy, psycopg)
├── .env.example                    # Environment variable template with DATABASE_URL
└── README.md
```

---

## 🚀 Quick Setup Instructions

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Set your PostgreSQL connection string in `.env`:
```env
DATABASE_URL=postgresql+psycopg://<username>:<password>@<host>:<port>/<database>
```
*(Example: `postgresql+psycopg://postgres:postgres@localhost:5432/water_body_encroachment`)*
*(Note: If PostgreSQL is not reachable during local development/offline testing, the system safely falls back to local SQLite to ensure uninterrupted development and testing).*

### 3. Initialize Database (Optional CLI or Auto-Init)
Run the PostgreSQL schema & seed:
```bash
psql -U postgres -d water_body_encroachment -f database/schema.sql
psql -U postgres -d water_body_encroachment -f database/seed.sql
```
Or let the Flask application initialize tables automatically on first run!

### 4. Run the Application
```bash
python backend/app.py
```
Open your browser at `http://127.0.0.1:5000`.

### 5. Default Demo Accounts
- **Admin**: `admin@waterbodies.gov.in` / `Password@123`
- **Authority**: `officer.revenue@waterbodies.gov.in` / `Password@123`
- **Citizen**: `citizen@example.com` / `Password@123`
