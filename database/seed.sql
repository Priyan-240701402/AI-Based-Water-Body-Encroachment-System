-- =====================================================================
-- Seed Data for Water Body Encroachment Complaint System
-- PostgreSQL 13+ Compatible
-- Realistic sample records for demonstration and AI evaluation
-- =====================================================================

-- 1. Default Users (passwords hashed using werkzeug.security generate_password_hash: 'Password@123')
INSERT INTO users (id, name, email, password_hash, role, phone) VALUES
(1, 'System Administrator', 'admin@waterbodies.gov.in', 'scrypt:32768:8:1$7f3z8uL79T8N2Q1h$0bc3a0f781df5dfaa1ec85c5b46299b1a51c4a04d30c50cf0f7cbca20e2ef5b1e42bfa1aa081702f23b7e7c48fa8869c4f74d0084f0c4bb277d337fa254ff72e', 'admin', '+91-9876543210'),
(2, 'Chief Revenue Officer Ramesh Kumar', 'officer.revenue@waterbodies.gov.in', 'scrypt:32768:8:1$7f3z8uL79T8N2Q1h$0bc3a0f781df5dfaa1ec85c5b46299b1a51c4a04d30c50cf0f7cbca20e2ef5b1e42bfa1aa081702f23b7e7c48fa8869c4f74d0084f0c4bb277d337fa254ff72e', 'authority', '+91-9876543211'),
(3, 'Municipal Engineer Priya Sharma', 'officer.municipal@waterbodies.gov.in', 'scrypt:32768:8:1$7f3z8uL79T8N2Q1h$0bc3a0f781df5dfaa1ec85c5b46299b1a51c4a04d30c50cf0f7cbca20e2ef5b1e42bfa1aa081702f23b7e7c48fa8869c4f74d0084f0c4bb277d337fa254ff72e', 'authority', '+91-9876543212'),
(4, 'Water Resources Executive Ananya Roy', 'officer.water@waterbodies.gov.in', 'scrypt:32768:8:1$7f3z8uL79T8N2Q1h$0bc3a0f781df5dfaa1ec85c5b46299b1a51c4a04d30c50cf0f7cbca20e2ef5b1e42bfa1aa081702f23b7e7c48fa8869c4f74d0084f0c4bb277d337fa254ff72e', 'authority', '+91-9876543213'),
(5, 'Demo Citizen Ravi', 'citizen@example.com', 'scrypt:32768:8:1$7f3z8uL79T8N2Q1h$0bc3a0f781df5dfaa1ec85c5b46299b1a51c4a04d30c50cf0f7cbca20e2ef5b1e42bfa1aa081702f23b7e7c48fa8869c4f74d0084f0c4bb277d337fa254ff72e', 'citizen', '+91-9876500001')
ON CONFLICT (id) DO UPDATE SET 
    name = EXCLUDED.name,
    email = EXCLUDED.email,
    password_hash = EXCLUDED.password_hash;

SELECT setval('users_id_seq', (SELECT COALESCE(MAX(id), 1) FROM users));

-- 2. Water Bodies (Demo Coordinates lat: ~12.97, lng: ~77.59)
INSERT INTO water_bodies (id, name, type, district, boundary_data, status, center_latitude, center_longitude) VALUES
(1, 'Demo Bellandur Lake', 'LAKE', 'East Zone', '{"type":"Polygon","coordinates":[[[77.660,12.930],[77.685,12.930],[77.685,12.945],[77.660,12.945],[77.660,12.930]]]}', 'CRITICAL', 12.9375, 77.6725),
(2, 'Demo Sankey Tank', 'POND', 'North Zone', '{"type":"Polygon","coordinates":[[[77.568,13.004],[77.575,13.004],[77.575,13.012],[77.568,13.012],[77.568,13.004]]]}', 'PROTECTED', 13.0080, 77.5715),
(3, 'Demo Varthur Lake', 'LAKE', 'East Zone', '{"type":"Polygon","coordinates":[[[77.730,12.940],[77.755,12.940],[77.755,12.960],[77.730,12.960],[77.730,12.940]]]}', 'UNDER_THREAT', 12.9500, 77.7425),
(4, 'Demo Rajakaluve Main Canal', 'CANAL', 'Central Zone', '{"type":"LineString","coordinates":[[77.600,12.965],[77.620,12.970],[77.640,12.975]]}', 'UNDER_THREAT', 12.9700, 77.6200),
(5, 'Demo Ulsoor Lake', 'LAKE', 'Central Zone', '{"type":"Polygon","coordinates":[[[77.618,12.980],[77.628,12.980],[77.628,12.989],[77.618,12.989],[77.618,12.980]]]}', 'PROTECTED', 12.9845, 77.6230),
(6, 'Demo Hebbal Lake', 'LAKE', 'North Zone', '{"type":"Polygon","coordinates":[[[77.585,13.040],[77.599,13.040],[77.599,13.052],[77.585,13.052],[77.585,13.040]]]}', 'PROTECTED', 13.0460, 77.5920)
ON CONFLICT (id) DO UPDATE SET 
    name = EXCLUDED.name,
    type = EXCLUDED.type,
    district = EXCLUDED.district;

SELECT setval('water_bodies_id_seq', (SELECT COALESCE(MAX(id), 1) FROM water_bodies));

-- 3. Authorities
INSERT INTO authorities (id, name, department, jurisdiction, contact, email, status, max_active_cases) VALUES
(1, 'North Zone Municipal Encroachment Cell', 'MUNICIPAL', 'North Zone', '+91-80-22220001', 'north.municipal@waterbodies.gov.in', 'ACTIVE', 15),
(2, 'East Zone Municipal Water Directorate', 'MUNICIPAL', 'East Zone', '+91-80-22220002', 'east.municipal@waterbodies.gov.in', 'ACTIVE', 20),
(3, 'Central Zone Revenue & Survey Department', 'REVENUE', 'Central Zone', '+91-80-22220003', 'central.revenue@waterbodies.gov.in', 'ACTIVE', 12),
(4, 'East Zone Revenue & Survey Office', 'REVENUE', 'East Zone', '+91-80-22220004', 'east.revenue@waterbodies.gov.in', 'ACTIVE', 18),
(5, 'State Water Resources Department (Lakes & Canals)', 'WATER_RESOURCES', 'East Zone', '+91-80-22220005', 'wrd.east@waterbodies.gov.in', 'ACTIVE', 25),
(6, 'State Water Resources Department (Central)', 'WATER_RESOURCES', 'Central Zone', '+91-80-22220006', 'wrd.central@waterbodies.gov.in', 'ACTIVE', 25),
(7, 'State Pollution Control & Wetland Authority', 'ENVIRONMENTAL', 'North Zone', '+91-80-22220007', 'env.north@waterbodies.gov.in', 'ACTIVE', 10)
ON CONFLICT (id) DO UPDATE SET 
    name = EXCLUDED.name,
    department = EXCLUDED.department,
    jurisdiction = EXCLUDED.jurisdiction;

SELECT setval('authorities_id_seq', (SELECT COALESCE(MAX(id), 1) FROM authorities));

-- 4. Rules for Propositional Knowledge Base
INSERT INTO rules (id, rule_name, description, conditions, conclusion, priority, active) VALUES
(1, 'R001_CONSTRUCTION_INSIDE_BOUNDARY', 'Construction activity inside or abutting mapped boundary indicates possible encroachment', 
 '{"has_construction": true, "inside_boundary": true}'::jsonb, 
 'POSSIBLE_ENCROACHMENT', 1, TRUE),

(2, 'R002_NO_PERMISSION_VERIFICATION', 'Possible encroachment without verified permission warrants official field verification', 
 '{"POSSIBLE_ENCROACHMENT": true, "has_permission": false}'::jsonb, 
 'REQUIRES_OFFICIAL_VERIFICATION', 2, TRUE),

(3, 'R003_HIGH_IMPACT_PRIORITY', 'Encroachment in protected lake or high affected area elevates priority to HIGH', 
 '{"REQUIRES_OFFICIAL_VERIFICATION": true, "affected_area_level": "HIGH"}'::jsonb, 
 'PRIORITY_HIGH', 3, TRUE),

(4, 'R004_CANAL_FLOW_OBSTRUCTION', 'Any construction along canal path raises immediate critical water flow threat', 
 '{"water_body_type": "CANAL", "has_construction": true}'::jsonb, 
 'FLOW_OBSTRUCTION_RISK', 2, TRUE),

(5, 'R005_INSUFFICIENT_EVIDENCE', 'Complaint lacking location boundary match or clear evidence flags insufficient information', 
 '{"inside_boundary": false, "has_construction": false}'::jsonb, 
 'NO_PRELIMINARY_INDICATOR', 1, TRUE)
ON CONFLICT (id) DO UPDATE SET 
    rule_name = EXCLUDED.rule_name,
    conditions = EXCLUDED.conditions,
    conclusion = EXCLUDED.conclusion;

SELECT setval('rules_id_seq', (SELECT COALESCE(MAX(id), 1) FROM rules));
