# Master Agent Prompt — Water Body Encroachment Complaint System

## Role

You are a senior full-stack software engineer, AI engineer, database designer, UI/UX developer, tester, and technical project mentor.

Your task is to **design and implement the complete Water Body Encroachment Complaint and Monitoring System** described below.

Treat this document as the authoritative project specification. Build the project systematically, keep the architecture simple enough for a college AI project, and ensure that the implementation is actually runnable.

---

# 1. Project Goal

Build a web-based system that allows citizens to report suspected encroachment of water bodies such as:

- Lakes
- Ponds
- Canals
- Rivers
- Other protected water bodies

The system must allow citizens to submit:

- Complaint description
- Location
- Optional photograph/evidence
- Water-body information where available

The system must then use a **Knowledge-Based AI reasoning engine**, not machine learning, to perform preliminary reasoning about the complaint.

The system must:

1. Receive the complaint.
2. Store the complaint and location.
3. Convert complaint information into facts.
4. Apply propositional rules.
5. Use Forward Chaining as the main reasoning algorithm.
6. Optionally use Backward Chaining for verification/explanation.
7. Use CSP for authority assignment.
8. Allow authorities to review and update complaints.
9. Allow citizens to track complaint status.
10. Display complaints and water bodies on an interactive map.

The system must never claim that an encroachment is legally confirmed. The AI result should be phrased as:

- `Possible Encroachment`
- `Requires Official Verification`
- `Insufficient Information`
- `No Preliminary Encroachment Indicator`

Final legal/administrative decisions must remain with authorized officials.

---

# 2. Mandatory Technical Stack

Use the following stack unless there is a strong technical reason to change something. If a change is necessary, explain why before making it.

## Frontend

- HTML5
- CSS3
- JavaScript
- Bootstrap 5
- Leaflet.js

## Map

- Leaflet.js
- OpenStreetMap

## Backend

- Python 3.x
- Flask
- REST APIs
- JSON

## Database

- PostgreSQL (driver: psycopg via SQLAlchemy / Flask-SQLAlchemy; connection: DATABASE_URL)

## AI / Reasoning

Implement these in Python:

1. Knowledge-Based Agent
2. Propositional Logic
3. Forward Chaining — MAIN ALGORITHM
4. Backward Chaining — SUPPORTING ALGORITHM
5. Constraint Satisfaction Problem (CSP) — AUTHORITY ASSIGNMENT
6. A* Search — OPTIONAL inspection-route feature

Do NOT use:

- TensorFlow
- PyTorch
- YOLO
- CNN
- Deep Learning
- Machine Learning models

Basic OpenCV may be used only for optional image preprocessing and must not become the main AI algorithm.

---

# 3. Main AI Architecture

Implement the reasoning pipeline as:

```text
Complaint
    ↓
Fact Extraction
    ↓
Knowledge Base
    ↓
Propositional Rules
    ↓
Forward Chaining
    ↓
Preliminary Result
    ↓
CSP Authority Assignment
    ↓
Authority Dashboard
    ↓
Official Verification
```

Optional:

```text
Complaint
    ↓
Backward Chaining
    ↓
Reason / Evidence Explanation
```

Optional:

```text
Authority Office
    ↓
A* Search
    ↓
Inspection Location
```

---

# 4. Knowledge-Based Agent

Create a modular Knowledge Base.

It should store facts such as:

```text
Construction = YES
Inside_Water_Boundary = YES
Permission = NO
Water_Body_Type = LAKE
Affected_Area = HIGH
Location = AREA_A
```

Do not hard-code all rules directly into Flask route files.

Keep AI logic in a separate module.

Recommended structure:

```text
backend/
├── app.py
├── config.py
├── database.py
├── models/
├── routes/
├── services/
├── ai/
│   ├── knowledge_base.py
│   ├── propositional_logic.py
│   ├── forward_chaining.py
│   ├── backward_chaining.py
│   ├── csp.py
│   └── astar.py
├── utils/
└── tests/
```

---

# 5. Propositional Logic

Represent rules clearly.

Example:

```text
C = Construction exists
W = Location is inside water-body boundary
P = Permission exists
E = Possible Encroachment
```

Rule:

```text
C AND W → E
```

Rule:

```text
E AND NOT P → Verification Required
```

Create a clean rule representation that can be processed by the reasoning engine.

The system should be able to show an explanation such as:

```text
Reasoning:
- Construction reported: YES
- Location inside mapped water boundary: YES
- Permission available: NO
- Rule R1 triggered
- Rule R2 triggered

Preliminary result:
Possible Encroachment — Requires Official Verification
```

---

# 6. Forward Chaining

This is the most important AI algorithm.

Implement a forward-chaining inference engine.

Input:

```text
Facts + Rules
```

Output:

```text
Derived Facts + Conclusion + Reasoning Trace
```

Example:

```text
Facts:
Construction = YES
InsideBoundary = YES
Permission = NO

Rule 1:
Construction AND InsideBoundary
→ PossibleEncroachment

Rule 2:
PossibleEncroachment AND Permission = NO
→ VerificationRequired
```

Output:

```text
PossibleEncroachment = YES
VerificationRequired = YES
```

The engine must also return a trace showing which rules fired.

---

# 7. Backward Chaining

Implement backward chaining as a supporting reasoning method.

Example goal:

```text
PossibleEncroachment
```

The engine should determine what facts are required:

```text
Construction = YES
InsideBoundary = YES
```

Then recursively verify whether those facts exist.

Use this primarily for:

- Explanation
- Verification
- Demonstrating the syllabus algorithm

Do not unnecessarily duplicate the entire forward-chaining workflow.

---

# 8. CSP Authority Assignment

Create a CSP-based authority assignment component.

Variables may include:

```text
Complaint
WaterBody
Location
District
Authority
```

Constraints may include:

```text
Location must belong to authority jurisdiction.
Water-body type must be handled by an eligible department.
Authority must be active.
Authority must be available for assignment.
```

Example:

```text
Location = Area A
WaterBodyType = Lake
Department = Municipal Authority

→ Assign to eligible municipal authority.
```

The CSP module should return:

```text
Selected Authority
Reason / Constraints Satisfied
```

Keep this deterministic and easy to demonstrate.

---

# 9. A* Search

Make A* optional.

If implemented, use it for:

```text
Authority Office → Complaint Location
```

Use:

```text
f(n) = g(n) + h(n)
```

where:

- `g(n)` = cost travelled
- `h(n)` = estimated remaining cost

Do not make A* a dependency for the main complaint workflow.

---

# 10. User Roles

Implement two primary roles.

## Citizen

Citizen can:

- Register
- Login
- Submit complaint
- Enter description
- Select location
- Upload optional evidence
- View complaint ID
- Track complaint status
- View authority response/history

## Authority/Admin

Authority can:

- Login
- View assigned complaints
- Filter complaints
- View evidence
- View map location
- View AI reasoning result
- Verify complaint
- Add remarks
- Change status
- Assign/reassign complaints
- Resolve/close complaints
- View statistics

Use role-based authorization.

---

# 11. Complaint Workflow

Implement:

```text
SUBMITTED
    ↓
AI_REVIEWED
    ↓
ASSIGNED
    ↓
UNDER_VERIFICATION
    ↓
ACTION_REQUIRED
    ↓
ACTION_TAKEN
    ↓
RESOLVED
```

Alternative statuses:

```text
REJECTED
DUPLICATE
INSUFFICIENT_INFORMATION
```

Every status change must be recorded in a history table.

---

# 12. Database

Use PostgreSQL (via SQLAlchemy / Flask-SQLAlchemy with psycopg driver; connection configured via DATABASE_URL). Keep latitude and longitude as standard numeric fields for the MVP (do not introduce PostGIS unless specifically required later).

Create at least these tables:

## users

```text
id
name
email
password_hash
role
phone
created_at
```

## water_bodies

```text
id
name
type
district
boundary_data
status
```

## complaints

```text
id
user_id
water_body_id
description
latitude
longitude
classification
priority
status
created_at
updated_at
```

## complaint_evidence

```text
id
complaint_id
file_path
file_type
uploaded_at
```

## authorities

```text
id
name
department
jurisdiction
contact
status
```

## authority_assignments

```text
id
complaint_id
authority_id
assigned_at
assigned_by
```

## rules

```text
id
rule_name
conditions
conclusion
priority
active
```

## complaint_status_history

```text
id
complaint_id
old_status
new_status
remarks
changed_by
changed_at
```

Use proper primary keys, foreign keys, indexes, and timestamps.

---

# 13. REST API

Implement at least:

```text
POST   /api/auth/register
POST   /api/auth/login

POST   /api/complaints
GET    /api/complaints
GET    /api/complaints/<id>
PUT    /api/complaints/<id>

POST   /api/complaints/<id>/analyze
POST   /api/complaints/<id>/assign

GET    /api/water-bodies
GET    /api/authorities

PUT    /api/complaints/<id>/status
GET    /api/complaints/<id>/history
```

Use JSON responses consistently.

Handle validation errors and authorization errors properly.

---

# 14. Frontend Pages

Create a clean responsive UI.

## Public

```text
/
 /login
 /register
```

## Citizen

```text
/citizen/dashboard
/citizen/complaint/new
/citizen/complaints
/citizen/complaints/<id>
```

## Authority

```text
/admin/dashboard
/admin/complaints
/admin/complaints/<id>
/admin/map
```

Use Bootstrap components.

Use Leaflet for maps.

---

# 15. Complaint Form

The form should contain:

```text
Complaint title
Description
Water body type
Water body name (optional)
Latitude
Longitude
Location picker
Photograph/evidence
```

Use browser geolocation only after the user gives appropriate permission.

Allow manual map selection as a fallback.

Do not require precise location access if the user chooses to enter/select the location manually.

---

# 16. Map Module

Use Leaflet + OpenStreetMap.

Features:

- Interactive map
- Complaint marker
- Location selection
- Water-body markers
- Optional water-body boundary polygons
- Complaint status markers
- Popup with complaint ID/status

For the prototype, use sample water-body boundary data.

Do not claim that sample boundaries are authoritative cadastral/legal boundaries.

---

# 17. Dashboard

## Citizen Dashboard

Show:

```text
Total Complaints
Pending
Under Verification
Resolved
```

Also show a complaint table:

```text
Complaint ID
Location
Classification
Priority
Status
Created Date
```

## Authority Dashboard

Show:

```text
Total Assigned
Pending Verification
High Priority
Action Required
Resolved
```

Include:

- Filters
- Search
- Status badges
- Map
- Recent complaints
- Basic charts if useful

---

# 18. Security

Implement:

- Password hashing
- Input validation
- Role-based authorization
- Secure file upload validation
- File size limits
- Allowed file extensions
- SQL injection protection through parameterized queries/ORM
- CSRF protection where applicable
- Environment variables for secrets
- No hard-coded database passwords
- Proper error handling

Never expose stack traces or database credentials to users.

---

# 19. Recommended Project Structure

Use a clean structure such as:

```text
water-body-encroachment/
│
├── backend/
│   ├── app.py
│   ├── config.py
│   ├── database.py
│   │
│   ├── models/
│   ├── routes/
│   ├── services/
│   │
│   ├── ai/
│   │   ├── knowledge_base.py
│   │   ├── propositional_logic.py
│   │   ├── forward_chaining.py
│   │   ├── backward_chaining.py
│   │   ├── csp.py
│   │   └── astar.py
│   │
│   ├── utils/
│   └── tests/
│
├── frontend/
│   ├── templates/
│   └── static/
│       ├── css/
│       ├── js/
│       └── images/
│
├── database/
│   ├── schema.sql
│   └── seed.sql
│
├── docs/
│
├── .env.example
├── requirements.txt
├── README.md
└── .gitignore
```

If using Flask's template system, it is acceptable to keep templates and static files inside the Flask application directory instead of a separate frontend deployment.

---

# 20. Development Rules

Follow these rules strictly:

1. Build incrementally.
2. Keep AI logic independent from Flask routes.
3. Keep database logic independent from AI logic.
4. Do not put all code in one file.
5. Use clear function/class names.
6. Add comments where the AI algorithm is implemented.
7. Write unit tests for each reasoning algorithm.
8. Validate every API input.
9. Use environment variables for secrets.
10. Keep the UI simple and professional.
11. Prefer maintainability over unnecessary complexity.
12. Do not introduce ML just to make the project sound more advanced.
13. Do not invent legal rules or government jurisdiction data.
14. Use clearly labeled demo/sample data where real official data is unavailable.
15. Do not claim AI detection is legally authoritative.

---

# 21. Testing Requirements

Create tests for:

## Forward Chaining

```text
Construction + InsideBoundary
→ PossibleEncroachment
```

## Backward Chaining

```text
Goal: PossibleEncroachment
→ Required facts are checked
```

## CSP

```text
Location + WaterBodyType + Jurisdiction
→ Correct eligible authority
```

## Complaint API

Test:

- Valid submission
- Missing fields
- Invalid coordinates
- Invalid file
- Unauthorized access

## Authentication

Test:

- Registration
- Login
- Wrong password
- Role restrictions

---

# 22. Sample Seed Data

Create realistic but clearly fictional/demo data.

Example water bodies:

```text
Demo Lake A
Demo Pond B
Demo Canal C
```

Example authorities:

```text
Municipal Water Body Department
Revenue/Survey Authority
Water Resources Department
Environmental Authority
```

Do not present fictional departments or boundaries as real government data.

---

# 23. Error Handling

The system should gracefully handle:

- Database unavailable
- Invalid request
- Missing complaint
- Unauthorized user
- Invalid file
- Invalid location
- AI rule failure
- No eligible authority
- Duplicate complaint

Return useful messages.

Example:

```json
{
  "success": false,
  "message": "No eligible authority was found for this complaint."
}
```

---

# 24. AI Explanation UI

Every AI result should be explainable.

Example:

```text
AI Preliminary Analysis

Facts:
✓ Construction reported
✓ Location inside mapped boundary
✓ Permission not provided

Rules Triggered:
✓ R001 — Construction + boundary condition
✓ R002 — No permission condition

Result:
POSSIBLE ENCROACHMENT

Next Step:
OFFICIAL VERIFICATION REQUIRED
```

This is important for demonstrating the Knowledge-Based AI aspect.

---

# 25. Implementation Order

Implement in this order:

### Step 1
Create project structure.

### Step 2
Create Python virtual environment and dependencies.

### Step 3
Configure Flask.

### Step 4
Configure PostgreSQL.

### Step 5
Create database schema and seed data.

### Step 6
Implement authentication.

### Step 7
Implement complaint CRUD.

### Step 8
Implement file upload.

### Step 9
Implement Leaflet map.

### Step 10
Implement Knowledge Base.

### Step 11
Implement Propositional Logic.

### Step 12
Implement Forward Chaining.

### Step 13
Implement Backward Chaining.

### Step 14
Implement CSP authority assignment.

### Step 15
Connect AI engine to complaint submission.

### Step 16
Build authority dashboard.

### Step 17
Implement status history.

### Step 18
Add testing.

### Step 19
Improve UI.

### Step 20
Prepare README and project documentation.

---

# 26. MVP Definition

The minimum working product MUST include:

```text
✓ Registration/Login
✓ Citizen complaint submission
✓ Location selection
✓ Optional evidence upload
✓ PostgreSQL storage
✓ Knowledge Base
✓ Propositional Rules
✓ Forward Chaining
✓ CSP Authority Assignment
✓ Authority Dashboard
✓ Complaint Status Tracking
✓ Reasoning Explanation
```

Only after these work should you add:

```text
Optional:
- Backward Chaining UI
- A* route planning
- Advanced analytics
- OpenCV preprocessing
- More detailed GIS features
```

---

# 27. Expected Final Output

When implementation is complete, provide:

1. Complete source code.
2. Database schema.
3. Seed/demo data.
4. `requirements.txt`.
5. `.env.example`.
6. README with setup instructions.
7. API documentation.
8. AI algorithm explanation.
9. Test cases and results.
10. Project architecture documentation.
11. Screenshots or instructions for running the application.
12. A clear explanation of where each syllabus algorithm is used.

---

# 28. Definition of Done

The project is considered complete only when:

- The Flask server starts successfully.
- PostgreSQL connection works.
- Users can register and login.
- Citizens can submit complaints.
- Complaints are stored in PostgreSQL.
- Location is displayed on the map.
- The AI engine generates a preliminary result.
- Forward chaining produces a reasoning trace.
- CSP assigns an eligible authority.
- Authorities can view assigned complaints.
- Authorities can update status.
- Citizens can track status.
- Status history is stored.
- Invalid requests are handled safely.
- Core AI algorithms have unit tests.
- README contains complete setup/run instructions.
- No required ML framework is present.

---

# 29. Development Philosophy

Do not over-engineer the project.

This is a college AI project, so prioritize:

```text
Correct AI algorithm implementation
        >
Clear architecture
        >
Working end-to-end system
        >
Explainability
        >
Clean UI
        >
Optional advanced features
```

The project should be easy to demonstrate to a faculty member:

> "This complaint entered the system. These facts were extracted. These rules fired. Forward Chaining produced this preliminary conclusion. CSP selected this authority. The authority can now verify and resolve the complaint."

That should be the central demonstration of the project.

---

# 30. Final Project Title

Use:

**Water Body Encroachment Complaint System Using Knowledge-Based Agent, Forward Chaining and Constraint Satisfaction**

Alternative:

**AI-Based Water Body Encroachment Complaint and Monitoring System Using Knowledge-Based Reasoning**

