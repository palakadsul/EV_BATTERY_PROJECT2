-- ============================================================
-- EV BATTERY HEALTH MONITORING SYSTEM
-- Complete ADBMS SQL File
-- Covers: Schema, RLS, RBAC, Indexing, Triggers, Partitioning,
--         Audit Trail, Materialized Views, XML
-- ============================================================


-- ============================================================
-- SECTION 1: SCHEMA CREATION
-- ============================================================
SET search_path TO public;

SELECT table_name, table_schema 
FROM information_schema.tables 
WHERE table_name = 'owners';

CREATE TABLE owners (
    owner_id   SERIAL PRIMARY KEY,
    username   VARCHAR(50) UNIQUE NOT NULL,
    owner_name VARCHAR(50),
    email      VARCHAR(100)
);

CREATE TABLE vehicles (
    vehicle_id     SERIAL PRIMARY KEY,
    owner_id       INT REFERENCES owners(owner_id) ON DELETE CASCADE,
    vehicle_number VARCHAR(20) UNIQUE NOT NULL,
    model          VARCHAR(50),
    purchase_date  DATE DEFAULT CURRENT_DATE
);

-- Partitioned table for time-series readings (range by month)
CREATE TABLE battery_readings (
    reading_id   SERIAL,
    vehicle_id   INT REFERENCES vehicles(vehicle_id) ON DELETE CASCADE,
    voltage      FLOAT,
    current      FLOAT,
    temperature  FLOAT,
    soc          FLOAT,   -- State of Charge (%)
    reading_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (reading_id, reading_time)
) PARTITION BY RANGE (reading_time);

-- Partitions (add more as needed)
CREATE TABLE battery_readings_2024_q1 PARTITION OF battery_readings
    FOR VALUES FROM ('2024-01-01') TO ('2024-04-01');

CREATE TABLE battery_readings_2024_q2 PARTITION OF battery_readings
    FOR VALUES FROM ('2024-04-01') TO ('2024-07-01');

CREATE TABLE battery_readings_2024_q3 PARTITION OF battery_readings
    FOR VALUES FROM ('2024-07-01') TO ('2024-10-01');

CREATE TABLE battery_readings_2024_q4 PARTITION OF battery_readings
    FOR VALUES FROM ('2024-10-01') TO ('2025-01-01');

CREATE TABLE battery_readings_2025_q1 PARTITION OF battery_readings
    FOR VALUES FROM ('2025-01-01') TO ('2025-04-01');

CREATE TABLE battery_readings_2025_q2 PARTITION OF battery_readings
    FOR VALUES FROM ('2025-04-01') TO ('2025-07-01');

-- Default partition to catch anything outside defined ranges
CREATE TABLE battery_readings_default PARTITION OF battery_readings DEFAULT;


CREATE TABLE battery_health (
    health_id   SERIAL PRIMARY KEY,
    vehicle_id  INT REFERENCES vehicles(vehicle_id) ON DELETE CASCADE,
    soh         FLOAT,         -- State of Health (%)
    degradation FLOAT,         -- Degradation (%)
    record_date DATE DEFAULT CURRENT_DATE
);

CREATE TABLE alerts (
    alert_id      SERIAL PRIMARY KEY,
    vehicle_id    INT REFERENCES vehicles(vehicle_id) ON DELETE CASCADE,
    alert_type    VARCHAR(30) DEFAULT 'GENERAL',  -- LOW_SOC, HIGH_TEMP, LOW_SOH, VOLTAGE
    alert_message TEXT,
    is_resolved   BOOLEAN DEFAULT FALSE,
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE charging_sessions (
    session_id    SERIAL PRIMARY KEY,
    vehicle_id    INT REFERENCES vehicles(vehicle_id) ON DELETE CASCADE,
    start_time    TIMESTAMP,
    end_time      TIMESTAMP,
    energy_kwh    FLOAT,
    start_soc     FLOAT,
    end_soc       FLOAT
);

CREATE TABLE maintenance_schedule (
    maintenance_id   SERIAL PRIMARY KEY,
    vehicle_id       INT REFERENCES vehicles(vehicle_id) ON DELETE CASCADE,
    scheduled_date   DATE,
    reason           TEXT,
    is_completed     BOOLEAN DEFAULT FALSE,
    created_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Audit trail for all sensitive changes
CREATE TABLE audit_trail (
    audit_id    SERIAL PRIMARY KEY,
    table_name  TEXT,
    action      TEXT,        -- INSERT / UPDATE / DELETE
    changed_by  TEXT DEFAULT current_user,
    changed_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    old_data    JSONB,
    new_data    JSONB
);

-- app_users for login (hashed password via pgcrypto)
CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE app_users (
    user_id    SERIAL PRIMARY KEY,
    username   TEXT UNIQUE NOT NULL,
    password   TEXT NOT NULL,   -- store crypt(password, gen_salt('bf'))
    role       TEXT NOT NULL,   -- 'admin' | 'technician' | 'ev_owner'
    owner_id   INT REFERENCES owners(owner_id)
);


-- ============================================================
-- SECTION 2: SAMPLE DATA
-- ============================================================

INSERT INTO owners (username, owner_name, email) VALUES
('owner1', 'Amit Shah',   'amit@gmail.com'),
('owner2', 'Riya Verma',  'riya@gmail.com'),
('owner3', 'Rahul Das',   'rahul@gmail.com'),
('owner4', 'Neha Patel',  'neha@gmail.com'),
('owner5', 'Karan Singh', 'karan@gmail.com'),
('owner6', 'Sneha Iyer',  'sneha@gmail.com');

INSERT INTO vehicles (owner_id, vehicle_number, model, purchase_date) VALUES
(1, 'MH12AB1111', 'Tata Nexon EV',   '2022-06-01'),
(2, 'KA01CD2222', 'MG ZS EV',        '2021-11-15'),
(3, 'WB09EF3333', 'Mahindra XUV400', '2023-01-20'),
(4, 'GJ05GH4444', 'Tata Tiago EV',   '2023-05-10'),
(5, 'DL08JK5555', 'Hyundai Kona EV', '2020-08-22'),
(6, 'TN10LM6666', 'BYD Atto 3',      '2022-03-18');

INSERT INTO battery_readings (vehicle_id, voltage, current, temperature, soc, reading_time) VALUES
(1, 48.5, 12.3, 34.6, 82, '2025-01-15 10:00:00'),
(2, 47.9, 11.8, 36.1, 78, '2025-01-15 10:05:00'),
(3, 49.2, 13.0, 33.8, 88, '2025-01-15 10:10:00'),
(4, 46.8, 10.9, 37.4, 72, '2025-01-15 10:15:00'),
(5, 50.1, 13.4, 32.6, 90, '2025-01-15 10:20:00'),
(6, 48.0, 12.1, 35.8, 80, '2025-01-15 10:25:00'),
-- extra readings for trend
(1, 47.8, 11.9, 35.2, 79, '2025-02-10 09:00:00'),
(1, 47.1, 11.5, 36.0, 75, '2025-03-05 08:30:00'),
(2, 47.0, 11.2, 38.5, 70, '2025-02-20 11:00:00');

INSERT INTO battery_health (vehicle_id, soh, degradation, record_date) VALUES
(1, 93, 7,  '2025-01-15'),
(2, 86, 14, '2025-01-15'),
(3, 90, 10, '2025-01-15'),
(4, 82, 18, '2025-01-15'),
(5, 95, 5,  '2025-01-15'),
(6, 88, 12, '2025-01-15');

INSERT INTO alerts (vehicle_id, alert_type, alert_message) VALUES
(2, 'HIGH_TEMP',  'Battery temperature slightly high'),
(4, 'LOW_SOC',    'Battery SOC low — charge soon'),
(6, 'LOW_SOH',    'Battery health degrading — maintenance advised'),
(3, 'VOLTAGE',    'Voltage fluctuation detected'),
(1, 'GENERAL',    'Normal operation'),
(5, 'GENERAL',    'Battery performing optimally');

INSERT INTO charging_sessions (vehicle_id, start_time, end_time, energy_kwh, start_soc, end_soc) VALUES
(1, '2025-01-14 22:00', '2025-01-15 01:30', 18.5, 30, 90),
(2, '2025-01-14 21:00', '2025-01-15 00:45', 15.2, 25, 80),
(5, '2025-01-13 23:00', '2025-01-14 02:00', 22.0, 20, 95);


-- ============================================================
-- SECTION 3: TRIGGERS
-- ============================================================

-- 3a: Alert on low SOH or high degradation
CREATE OR REPLACE FUNCTION fn_battery_health_alert()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.soh < 80 THEN
        INSERT INTO alerts (vehicle_id, alert_type, alert_message)
        VALUES (NEW.vehicle_id, 'LOW_SOH',
                FORMAT('Critical: SOH dropped to %.1f%% — immediate maintenance required', NEW.soh));
    ELSIF NEW.degradation > 20 THEN
        INSERT INTO alerts (vehicle_id, alert_type, alert_message)
        VALUES (NEW.vehicle_id, 'HIGH_DEGRADATION',
                FORMAT('Warning: Battery degradation at %.1f%%', NEW.degradation));
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_battery_health_alert
AFTER INSERT OR UPDATE ON battery_health
FOR EACH ROW EXECUTE FUNCTION fn_battery_health_alert();


-- 3b: Alert on high temperature or low SOC from readings
CREATE OR REPLACE FUNCTION fn_battery_reading_alert()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.temperature > 45 THEN
        INSERT INTO alerts (vehicle_id, alert_type, alert_message)
        VALUES (NEW.vehicle_id, 'HIGH_TEMP',
                FORMAT('Danger: Battery temperature %.1f°C — risk of thermal runaway', NEW.temperature));
    END IF;

    IF NEW.soc < 15 THEN
        INSERT INTO alerts (vehicle_id, alert_type, alert_message)
        VALUES (NEW.vehicle_id, 'LOW_SOC',
                FORMAT('Critical: SOC at %.1f%% — charge immediately', NEW.soc));
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_battery_reading_alert
AFTER INSERT ON battery_readings
FOR EACH ROW EXECUTE FUNCTION fn_battery_reading_alert();


-- 3c: Auto-schedule maintenance when SOH < 80
CREATE OR REPLACE FUNCTION fn_auto_maintenance()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.soh < 80 THEN
        INSERT INTO maintenance_schedule (vehicle_id, scheduled_date, reason)
        VALUES (NEW.vehicle_id, CURRENT_DATE + INTERVAL '7 days',
                'Auto-scheduled: SOH below 80%');
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_auto_maintenance
AFTER INSERT OR UPDATE ON battery_health
FOR EACH ROW EXECUTE FUNCTION fn_auto_maintenance();


-- 3d: Audit trail trigger for battery_health changes
CREATE OR REPLACE FUNCTION fn_audit_battery_health()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'UPDATE' THEN
        INSERT INTO audit_trail (table_name, action, old_data, new_data)
        VALUES ('battery_health', 'UPDATE',
                row_to_json(OLD)::jsonb,
                row_to_json(NEW)::jsonb);
    ELSIF TG_OP = 'INSERT' THEN
        INSERT INTO audit_trail (table_name, action, old_data, new_data)
        VALUES ('battery_health', 'INSERT', NULL, row_to_json(NEW)::jsonb);
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_audit_battery_health
AFTER INSERT OR UPDATE ON battery_health
FOR EACH ROW EXECUTE FUNCTION fn_audit_battery_health();


-- ============================================================
-- SECTION 4: INDEXES
-- ============================================================

CREATE INDEX idx_vehicles_owner_id          ON vehicles(owner_id);
CREATE INDEX idx_battery_health_vehicle_id  ON battery_health(vehicle_id);
CREATE INDEX idx_battery_readings_vehicle_id ON battery_readings(vehicle_id);
CREATE INDEX idx_battery_health_soh         ON battery_health(soh);
CREATE INDEX idx_battery_readings_time      ON battery_readings(reading_time DESC);
CREATE INDEX idx_alerts_vehicle_id          ON alerts(vehicle_id);
CREATE INDEX idx_alerts_created_at          ON alerts(created_at DESC);
CREATE INDEX idx_alerts_unresolved          ON alerts(is_resolved) WHERE is_resolved = FALSE;



-- EXPLAIN ANALYZE before and after indexes
EXPLAIN ANALYZE
SELECT o.owner_name, v.vehicle_number, bh.soh, bh.degradation
FROM battery_health bh
JOIN vehicles v ON bh.vehicle_id = v.vehicle_id
JOIN owners o   ON v.owner_id   = o.owner_id;


-- ============================================================
-- SECTION 5: MATERIALIZED VIEW
-- ============================================================

-- Pre-aggregate fleet summary for dashboard fast load
CREATE MATERIALIZED VIEW mv_fleet_health_summary AS
SELECT
    o.owner_name,
    v.vehicle_number,
    v.model,
    bh.soh,
    bh.degradation,
    bh.record_date,
    CASE
        WHEN bh.soh >= 90 THEN 'Excellent'
        WHEN bh.soh >= 80 THEN 'Good'
        WHEN bh.soh >= 70 THEN 'Fair'
        ELSE 'Critical'
    END AS health_status
FROM battery_health bh
JOIN vehicles v ON bh.vehicle_id = v.vehicle_id
JOIN owners o   ON v.owner_id   = o.owner_id
WITH DATA;
SELECT * FROM mv_fleet_health_summary;
-- Refresh manually or via scheduled job
-- REFRESH MATERIALIZED VIEW mv_fleet_health_summary;

CREATE UNIQUE INDEX idx_mv_fleet_vehicle ON mv_fleet_health_summary(vehicle_number);


-- ============================================================
-- SECTION 6: RBAC — Roles & Privileges
-- ============================================================

CREATE ROLE admin_role;
CREATE ROLE technician_role;
CREATE ROLE ev_owner_role;

-- Admin: full access
GRANT ALL PRIVILEGES ON ALL TABLES    IN SCHEMA public TO admin_role;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO admin_role;

-- Technician: read/write readings and health, read alerts
GRANT SELECT, INSERT, UPDATE ON battery_readings     TO technician_role;
GRANT SELECT, UPDATE         ON battery_health       TO technician_role;
GRANT SELECT, INSERT         ON alerts               TO technician_role;
GRANT SELECT, INSERT, UPDATE ON maintenance_schedule TO technician_role;

-- EV Owner: read-only on their own data (enforced via RLS below)
GRANT SELECT ON vehicles         TO ev_owner_role;
GRANT SELECT ON battery_readings TO ev_owner_role;
GRANT SELECT ON battery_health   TO ev_owner_role;
GRANT SELECT ON alerts           TO ev_owner_role;
GRANT SELECT ON charging_sessions TO ev_owner_role;


-- ============================================================
-- SECTION 7: ROW-LEVEL SECURITY (RLS)
-- ============================================================

-- battery_health: owners only see their vehicle
ALTER TABLE battery_health    ENABLE ROW LEVEL SECURITY;
ALTER TABLE battery_health    FORCE  ROW LEVEL SECURITY;
ALTER TABLE battery_readings  ENABLE ROW LEVEL SECURITY;
ALTER TABLE battery_readings  FORCE  ROW LEVEL SECURITY;
ALTER TABLE alerts            ENABLE ROW LEVEL SECURITY;
ALTER TABLE alerts            FORCE  ROW LEVEL SECURITY;

-- Drop old policies if re-running
DROP POLICY IF EXISTS pol_owner_battery_health    ON battery_health;
DROP POLICY IF EXISTS pol_owner_battery_readings  ON battery_readings;
DROP POLICY IF EXISTS pol_owner_alerts            ON alerts;
DROP POLICY IF EXISTS pol_tech_battery_health     ON battery_health;
DROP POLICY IF EXISTS pol_tech_battery_readings   ON battery_readings;
DROP POLICY IF EXISTS pol_admin_all_health        ON battery_health;

-- Owner sees only their vehicles' data
CREATE POLICY pol_owner_battery_health
ON battery_health FOR SELECT TO ev_owner_role
USING (
    vehicle_id IN (
        SELECT v.vehicle_id FROM vehicles v
        JOIN owners o ON v.owner_id = o.owner_id
        WHERE o.username = current_user
    )
);

CREATE POLICY pol_owner_battery_readings
ON battery_readings FOR SELECT TO ev_owner_role
USING (
    vehicle_id IN (
        SELECT v.vehicle_id FROM vehicles v
        JOIN owners o ON v.owner_id = o.owner_id
        WHERE o.username = current_user
    )
);

CREATE POLICY pol_owner_alerts
ON alerts FOR SELECT TO ev_owner_role
USING (
    vehicle_id IN (
        SELECT v.vehicle_id FROM vehicles v
        JOIN owners o ON v.owner_id = o.owner_id
        WHERE o.username = current_user
    )
);

-- Technician can update battery_health and readings freely
CREATE POLICY pol_tech_battery_health
ON battery_health FOR ALL TO technician_role
USING (true) WITH CHECK (true);

CREATE POLICY pol_tech_battery_readings
ON battery_readings FOR ALL TO technician_role
USING (true) WITH CHECK (true);

-- Admin bypass
CREATE POLICY pol_admin_all_health
ON battery_health FOR ALL TO admin_role
USING (true) WITH CHECK (true);

SELECT current_database();
SET search_path TO public;
-- ============================================================
-- SECTION 8: VERIFY ACCESS CONTROL
-- ============================================================

-- Test as owner (should only see their vehicles' data)
SET ROLE owner1;
SELECT * FROM battery_health;    -- sees only vehicle_id=1
SELECT * FROM battery_readings;  -- sees only vehicle_id=1
RESET ROLE;

-- Test as technician
SET ROLE technician_role;
UPDATE battery_readings SET temperature = 38 WHERE vehicle_id = 1;
RESET ROLE;

-- Owner cannot update
SET ROLE owner1;
UPDATE battery_health SET soh = 99;  -- should be blocked by RLS
RESET ROLE;


-- ============================================================
-- SECTION 9: USEFUL ANALYTICAL QUERIES
-- ============================================================

-- Fleet overview
SELECT
    o.owner_name,
    v.vehicle_number,
    v.model,
    bh.soh,
    bh.degradation,
    CASE
        WHEN bh.soh >= 90 THEN 'Excellent'
        WHEN bh.soh >= 80 THEN 'Good'
        WHEN bh.soh >= 70 THEN 'Fair'
        ELSE 'Critical'
    END AS health_status
FROM battery_health bh
JOIN vehicles v ON bh.vehicle_id = v.vehicle_id
JOIN owners o   ON v.owner_id   = o.owner_id
ORDER BY bh.soh ASC;

-- Latest reading per vehicle
SELECT DISTINCT ON (vehicle_id)
    vehicle_id, voltage, current, temperature, soc, reading_time
FROM battery_readings
ORDER BY vehicle_id, reading_time DESC;

-- Unresolved alerts
SELECT a.alert_id, v.vehicle_number, a.alert_type, a.alert_message, a.created_at
FROM alerts a
JOIN vehicles v ON a.vehicle_id = v.vehicle_id
WHERE a.is_resolved = FALSE
ORDER BY a.created_at DESC;

-- Average SOH per model
SELECT v.model, ROUND(AVG(bh.soh)::NUMERIC, 2) AS avg_soh,
       COUNT(*) AS vehicles
FROM battery_health bh
JOIN vehicles v ON bh.vehicle_id = v.vehicle_id
GROUP BY v.model
ORDER BY avg_soh DESC;

-- SOH trend over time for a vehicle
SELECT record_date, soh, degradation
FROM battery_health
WHERE vehicle_id = 1
ORDER BY record_date;

-- Partition usage check
SELECT tableoid::regclass AS partition, COUNT(*) AS rows
FROM battery_readings
GROUP BY tableoid;

-- ============================================================
-- SECTION 10: RBAC SECURITY ADDITIONS
-- Safe to run on existing DB — all idempotent
-- ============================================================

-- ── 10a: Ensure roles exist (skip if already created) ──────
DO $$ BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'admin_role') THEN
        CREATE ROLE admin_role;
    END IF;
END $$;

DO $$ BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'technician_role') THEN
        CREATE ROLE technician_role;
    END IF;
END $$;

DO $$ BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'ev_owner_role') THEN
        CREATE ROLE ev_owner_role;
    END IF;
END $$;

-- ── 10b: REVOKE dangerous defaults from PUBLIC ──────────────
-- Prevents any logged-in user from accessing tables by default
REVOKE ALL ON ALL TABLES    IN SCHEMA public FROM PUBLIC;
REVOKE ALL ON ALL SEQUENCES IN SCHEMA public FROM PUBLIC;

-- ── 10c: GRANT correct permissions per role ─────────────────

-- Admin: full access to everything
GRANT ALL PRIVILEGES ON ALL TABLES    IN SCHEMA public TO admin_role;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO admin_role;

-- Technician: read most tables, update battery data, manage maintenance
GRANT SELECT          ON owners, vehicles, battery_readings,
                         battery_health, alerts, charging_sessions,
                         maintenance_schedule, car_catalog          TO technician_role;
GRANT INSERT, UPDATE  ON battery_readings                           TO technician_role;
GRANT UPDATE          ON battery_health                             TO technician_role;
GRANT INSERT          ON alerts                                     TO technician_role;
GRANT INSERT, UPDATE  ON maintenance_schedule                       TO technician_role;
GRANT USAGE, SELECT   ON ALL SEQUENCES IN SCHEMA public             TO technician_role;

-- EV Owner: read-only on select tables (RLS will filter to their rows)
GRANT SELECT ON vehicles, battery_readings, battery_health,
               alerts, charging_sessions, maintenance_schedule,
               owners, car_catalog                                  TO ev_owner_role;

-- ── 10d: DENY sensitive tables from non-admins ──────────────
REVOKE ALL ON audit_trail FROM technician_role, ev_owner_role;
REVOKE ALL ON app_users   FROM technician_role, ev_owner_role;

-- ── 10e: Row Level Security — already enabled in your file ──
-- These are extra policies for maintenance_schedule and charging_sessions
-- which were missing from your original RLS section.

ALTER TABLE maintenance_schedule ENABLE ROW LEVEL SECURITY;
ALTER TABLE maintenance_schedule FORCE  ROW LEVEL SECURITY;

ALTER TABLE charging_sessions    ENABLE ROW LEVEL SECURITY;
ALTER TABLE charging_sessions    FORCE  ROW LEVEL SECURITY;

DROP POLICY IF EXISTS pol_owner_maintenance    ON maintenance_schedule;
DROP POLICY IF EXISTS pol_tech_maintenance     ON maintenance_schedule;
DROP POLICY IF EXISTS pol_admin_maintenance    ON maintenance_schedule;
DROP POLICY IF EXISTS pol_owner_charging       ON charging_sessions;
DROP POLICY IF EXISTS pol_admin_charging       ON charging_sessions;

-- Owner sees only their vehicle's maintenance
CREATE POLICY pol_owner_maintenance
ON maintenance_schedule FOR SELECT TO ev_owner_role
USING (
    vehicle_id IN (
        SELECT v.vehicle_id FROM vehicles v
        JOIN owners o ON v.owner_id = o.owner_id
        WHERE o.username = current_user
    )
);

-- Technician sees and modifies all maintenance records
CREATE POLICY pol_tech_maintenance
ON maintenance_schedule FOR ALL TO technician_role
USING (true) WITH CHECK (true);

-- Admin has full access
CREATE POLICY pol_admin_maintenance
ON maintenance_schedule FOR ALL TO admin_role
USING (true) WITH CHECK (true);

-- Owner sees only their vehicle's charging sessions
CREATE POLICY pol_owner_charging
ON charging_sessions FOR SELECT TO ev_owner_role
USING (
    vehicle_id IN (
        SELECT v.vehicle_id FROM vehicles v
        JOIN owners o ON v.owner_id = o.owner_id
        WHERE o.username = current_user
    )
);

CREATE POLICY pol_admin_charging
ON charging_sessions FOR ALL TO admin_role
USING (true) WITH CHECK (true);

-- ── 10f: Grant roles to actual DB users ─────────────────────
-- Run these only if you have separate DB login users.
-- Your app currently uses a single 'postgres' superuser for all Flask queries,
-- which is fine for development. For production, create separate DB users:

-- GRANT admin_role      TO your_admin_db_user;
-- GRANT technician_role TO your_tech_db_user;
-- GRANT ev_owner_role   TO your_owner_db_user;

-- ── 10g: Verification queries ───────────────────────────────
-- Run these to confirm setup:

-- Check roles exist:
SELECT rolname FROM pg_roles
WHERE rolname IN ('admin_role', 'technician_role', 'ev_owner_role');

-- Check table grants:
SELECT grantee, table_name, privilege_type
FROM information_schema.role_table_grants
WHERE grantee IN ('admin_role', 'technician_role', 'ev_owner_role')
  AND table_name IN ('battery_health', 'alerts', 'maintenance_schedule', 'audit_trail', 'app_users')
ORDER BY grantee, table_name, privilege_type;

-- Check all RLS policies:
SELECT tablename, policyname, roles, cmd
FROM pg_policies
ORDER BY tablename;