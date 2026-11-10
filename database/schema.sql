-- =====================================================================
-- Database Schema for Water Body Encroachment Complaint System
-- Compatible with PostgreSQL 13+ / 14+ / 15+ / 16+
-- Uses standard numeric latitude/longitude fields (No PostGIS required)
-- =====================================================================

-- 1. Users Table (Citizens, Authorities, Admins)
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(120) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(30) NOT NULL DEFAULT 'citizen', -- 'citizen', 'authority', 'admin'
    phone VARCHAR(20) DEFAULT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_user_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_user_role ON users(role);

-- 2. Water Bodies Table (Lakes, Ponds, Canals, Rivers)
CREATE TABLE IF NOT EXISTS water_bodies (
    id SERIAL PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    type VARCHAR(50) NOT NULL, -- 'LAKE', 'POND', 'CANAL', 'RIVER', 'WETLAND'
    district VARCHAR(100) NOT NULL,
    boundary_data TEXT DEFAULT NULL, -- GeoJSON polygon or coordinate array string
    status VARCHAR(50) DEFAULT 'PROTECTED', -- 'PROTECTED', 'UNDER_THREAT', 'CRITICAL'
    center_latitude NUMERIC(10, 7) DEFAULT NULL,
    center_longitude NUMERIC(10, 7) DEFAULT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_wb_district ON water_bodies(district);
CREATE INDEX IF NOT EXISTS idx_wb_type ON water_bodies(type);

-- 3. Authorities Table
CREATE TABLE IF NOT EXISTS authorities (
    id SERIAL PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    department VARCHAR(100) NOT NULL, -- 'MUNICIPAL', 'REVENUE', 'WATER_RESOURCES', 'ENVIRONMENTAL'
    jurisdiction VARCHAR(100) NOT NULL, -- District or area name, e.g., 'Central District', 'North Zone'
    contact VARCHAR(100) DEFAULT NULL,
    email VARCHAR(150) DEFAULT NULL,
    status VARCHAR(30) DEFAULT 'ACTIVE', -- 'ACTIVE', 'INACTIVE', 'OVERLOADED'
    max_active_cases INT DEFAULT 20,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_auth_dept ON authorities(department);
CREATE INDEX IF NOT EXISTS idx_auth_jurisdiction ON authorities(jurisdiction);
CREATE INDEX IF NOT EXISTS idx_auth_status ON authorities(status);

-- 4. Complaints Table
CREATE TABLE IF NOT EXISTS complaints (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    water_body_id INT REFERENCES water_bodies(id) ON DELETE SET NULL,
    title VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,
    latitude NUMERIC(10, 7) NOT NULL,
    longitude NUMERIC(10, 7) NOT NULL,
    classification VARCHAR(80) DEFAULT 'Pending Preliminary Analysis',
    priority VARCHAR(20) DEFAULT 'MEDIUM', -- 'LOW', 'MEDIUM', 'HIGH', 'CRITICAL'
    status VARCHAR(40) NOT NULL DEFAULT 'SUBMITTED',
    -- Workflow: SUBMITTED -> AI_REVIEWED -> ASSIGNED -> UNDER_VERIFICATION -> ACTION_REQUIRED -> ACTION_TAKEN -> RESOLVED / REJECTED
    has_construction BOOLEAN DEFAULT FALSE,
    inside_boundary BOOLEAN DEFAULT FALSE,
    has_permission BOOLEAN DEFAULT FALSE,
    affected_area_level VARCHAR(20) DEFAULT 'MEDIUM', -- 'LOW', 'MEDIUM', 'HIGH'
    ai_reasoning_trace JSONB DEFAULT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_complaint_status ON complaints(status);
CREATE INDEX IF NOT EXISTS idx_complaint_user ON complaints(user_id);
CREATE INDEX IF NOT EXISTS idx_complaint_water_body ON complaints(water_body_id);
CREATE INDEX IF NOT EXISTS idx_complaint_priority ON complaints(priority);

-- 5. Complaint Evidence Table (Photos, Documents)
CREATE TABLE IF NOT EXISTS complaint_evidence (
    id SERIAL PRIMARY KEY,
    complaint_id INT NOT NULL REFERENCES complaints(id) ON DELETE CASCADE,
    file_path VARCHAR(300) NOT NULL,
    file_type VARCHAR(50) NOT NULL, -- 'image/jpeg', 'image/png', 'application/pdf'
    original_filename VARCHAR(255) DEFAULT NULL,
    uploaded_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_evidence_complaint ON complaint_evidence(complaint_id);

-- 6. Authority Assignments (Tracks CSP and manual assignment)
CREATE TABLE IF NOT EXISTS authority_assignments (
    id SERIAL PRIMARY KEY,
    complaint_id INT NOT NULL REFERENCES complaints(id) ON DELETE CASCADE,
    authority_id INT NOT NULL REFERENCES authorities(id) ON DELETE CASCADE,
    assigned_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    assigned_by VARCHAR(50) DEFAULT 'AI_CSP_SYSTEM', -- 'AI_CSP_SYSTEM' or 'ADMIN'
    assignment_reason TEXT DEFAULT NULL,
    status VARCHAR(30) DEFAULT 'ASSIGNED' -- 'ASSIGNED', 'ACCEPTED', 'TRANSFERRED'
);

CREATE INDEX IF NOT EXISTS idx_assignment_complaint ON authority_assignments(complaint_id);
CREATE INDEX IF NOT EXISTS idx_assignment_authority ON authority_assignments(authority_id);

-- 7. Rules Table (Propositional Logic Knowledge Base in DB)
CREATE TABLE IF NOT EXISTS rules (
    id SERIAL PRIMARY KEY,
    rule_name VARCHAR(100) NOT NULL UNIQUE,
    description VARCHAR(255) DEFAULT NULL,
    conditions JSONB NOT NULL, -- JSONB format of antecedent propositions
    conclusion VARCHAR(120) NOT NULL, -- Consequent proposition
    priority INT DEFAULT 1,
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_rule_active ON rules(active);

-- 8. Complaint Status History (Audit trail of every status change)
CREATE TABLE IF NOT EXISTS complaint_status_history (
    id SERIAL PRIMARY KEY,
    complaint_id INT NOT NULL REFERENCES complaints(id) ON DELETE CASCADE,
    old_status VARCHAR(40) DEFAULT NULL,
    new_status VARCHAR(40) NOT NULL,
    remarks TEXT DEFAULT NULL,
    changed_by INT REFERENCES users(id) ON DELETE SET NULL,
    changed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_history_complaint ON complaint_status_history(complaint_id);
