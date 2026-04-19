from flask import Flask, jsonify, request, session
from flask_cors import CORS
import psycopg2
import psycopg2.extras
import os
from functools import wraps
from dotenv import load_dotenv
load_dotenv()
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "ev_secret_change_in_prod")
CORS(app, supports_credentials=True)   # ← supports_credentials required for cookie-based auth

# ── DB Connection ──────────────────────────────────────────────────────────────
DB_CONFIG = {
    "host":     os.environ.get("DB_HOST", "localhost"),
    "port":     int(os.environ.get("DB_PORT", 5432)),
    "dbname":   os.environ.get("DB_NAME", "EV_BATTERY_V2"),
    "user":     os.environ.get("DB_USER", "postgres"),
    "password": os.environ.get("DB_PASSWORD", ""),   # set via env var, never hardcode
}

def get_db():
    conn = psycopg2.connect(**DB_CONFIG)
    conn.autocommit = True
    return conn

def query(sql, params=None, fetchall=True):
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute(sql, params or ())
    result = cur.fetchall() if fetchall else cur.fetchone()
    cur.close(); conn.close()
    return result

# ── Auth helpers ───────────────────────────────────────────────────────────────
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user" not in session:
            return jsonify({"error": "Unauthorized"}), 401
        return f(*args, **kwargs)
    return decorated

def role_required(*roles):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if session.get("role") not in roles:
                return jsonify({"error": "Forbidden"}), 403
            return f(*args, **kwargs)
        return decorated
    return decorator

# ── Auth ───────────────────────────────────────────────────────────────────────
@app.route("/api/login", methods=["POST"])
def login():
    data = request.json
    row = query(
        "SELECT user_id, username, role, owner_id "
        "FROM app_users WHERE username = %s AND password = crypt(%s, password)",
        (data["username"], data["password"]),
        fetchall=False
    )
    if not row:
        return jsonify({"error": "Invalid credentials"}), 401
    session["user"]     = row["username"]
    session["role"]     = row["role"]
    session["owner_id"] = row["owner_id"]
    return jsonify({"username": row["username"], "role": row["role"], "owner_id": row["owner_id"]})

@app.route("/api/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"message": "Logged out"})

# ── Fleet / Battery Health ─────────────────────────────────────────────────────
@app.route("/api/fleet-summary")
@login_required
def fleet_summary():
    return jsonify(query("SELECT * FROM mv_fleet_health_summary ORDER BY soh ASC"))

@app.route("/api/battery-health/<int:vehicle_id>")
@login_required
def battery_health(vehicle_id):
    return jsonify(query(
        "SELECT record_date, soh, degradation FROM battery_health "
        "WHERE vehicle_id = %s ORDER BY record_date",
        (vehicle_id,)
    ))

@app.route("/api/battery-readings/<int:vehicle_id>")
@login_required
def battery_readings(vehicle_id):
    # FIX: column is 'current' not 'current_amp' in the actual schema
    return jsonify(query(
        "SELECT reading_time, voltage, current AS current_amp, temperature, soc "
        "FROM battery_readings WHERE vehicle_id = %s "
        "ORDER BY reading_time DESC LIMIT 30",
        (vehicle_id,)
    ))

# ── Battery Updates (admin / technician only) ────────────────────────────────
@app.route("/api/battery-health/<int:vehicle_id>", methods=["POST"])
@login_required
@role_required("admin", "technician")
def update_battery_health(vehicle_id):
    """Insert a new battery health record for a vehicle."""
    data = request.json or {}
    try:
        soh         = float(data["soh"])
        degradation = float(data["degradation"])
        record_date = data.get("record_date")  # optional; defaults to today
    except (KeyError, ValueError) as e:
        return jsonify({"error": f"Invalid payload: {e}"}), 400

    if not (0 <= soh <= 100):
        return jsonify({"error": "soh must be between 0 and 100"}), 400
    if not (0 <= degradation <= 100):
        return jsonify({"error": "degradation must be between 0 and 100"}), 400

    conn = get_db()
    cur  = conn.cursor()
    if record_date:
        cur.execute(
            "INSERT INTO battery_health (vehicle_id, soh, degradation, record_date) "
            "VALUES (%s, %s, %s, %s)",
            (vehicle_id, soh, degradation, record_date)
        )
    else:
        cur.execute(
            "INSERT INTO battery_health (vehicle_id, soh, degradation, record_date) "
            "VALUES (%s, %s, %s, CURRENT_DATE)",
            (vehicle_id, soh, degradation)
        )
    cur.close()
    conn.close()
    return jsonify({"message": "Battery health record added", "vehicle_id": vehicle_id,
                    "soh": soh, "degradation": degradation}), 201


@app.route("/api/battery-readings/<int:vehicle_id>", methods=["POST"])
@login_required
@role_required("admin", "technician")
def add_battery_reading(vehicle_id):
    """Insert a live battery sensor reading for a vehicle."""
    data = request.json or {}
    try:
        voltage     = float(data["voltage"])
        current     = float(data["current"])
        temperature = float(data["temperature"])
        soc         = float(data["soc"])
    except (KeyError, ValueError) as e:
        return jsonify({"error": f"Invalid payload: {e}"}), 400

    conn = get_db()
    cur  = conn.cursor()
    cur.execute(
        "INSERT INTO battery_readings (vehicle_id, voltage, current, temperature, soc, reading_time) "
        "VALUES (%s, %s, %s, %s, %s, NOW())",
        (vehicle_id, voltage, current, temperature, soc)
    )
    cur.close()
    conn.close()
    return jsonify({"message": "Battery reading added", "vehicle_id": vehicle_id}), 201


@app.route("/api/maintenance/<int:maintenance_id>/complete", methods=["POST"])
@login_required
@role_required("admin", "technician")
def complete_maintenance(maintenance_id):
    conn = get_db()
    cur  = conn.cursor()
    cur.execute(
        "UPDATE maintenance_schedule SET is_completed = TRUE WHERE maintenance_id = %s",
        (maintenance_id,)
    )
    cur.close()
    conn.close()
    return jsonify({"message": "Maintenance marked complete"})


# ── Alerts ─────────────────────────────────────────────────────────────────────
@app.route("/api/alerts")
@login_required
def alerts():
    return jsonify(query(
        "SELECT a.alert_id, v.vehicle_number, a.alert_message, a.alert_type AS severity, "
        "a.is_resolved, a.created_at "
        "FROM alerts a JOIN vehicles v ON a.vehicle_id = v.vehicle_id "
        "ORDER BY a.created_at DESC LIMIT 50"
    ))

@app.route("/api/alerts/<int:alert_id>/resolve", methods=["POST"])
@login_required
@role_required("admin", "technician")
def resolve_alert(alert_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "UPDATE alerts SET is_resolved = TRUE WHERE alert_id = %s",
        (alert_id,)
    )
    cur.close(); conn.close()
    return jsonify({"message": "Alert resolved"})

# ── Owners ─────────────────────────────────────────────────────────────────────
@app.route("/api/owners")
@login_required
@role_required("admin", "technician")
def owners():
    return jsonify(query(
        "SELECT o.owner_id, o.owner_name, o.email, "
        "COUNT(v.vehicle_id) AS vehicle_count "
        "FROM owners o LEFT JOIN vehicles v ON o.owner_id = v.owner_id "
        "GROUP BY o.owner_id, o.owner_name, o.email ORDER BY o.owner_id"
    ))

@app.route("/api/vehicles")
@login_required
def vehicles():
    owner_id = session.get("owner_id")
    if session["role"] == "ev_owner" and owner_id:
        return jsonify(query(
            # FIX: include battery_capacity_kwh in vehicles query
            "SELECT v.vehicle_id, v.vehicle_number, v.model, v.purchase_date, "
            "v.battery_capacity_kwh, o.owner_name, o.owner_id "
            "FROM vehicles v "
            "JOIN owners o ON v.owner_id = o.owner_id "
            "WHERE v.owner_id = %s", (owner_id,)
        ))
    return jsonify(query(
        "SELECT v.vehicle_id, v.vehicle_number, v.model, v.purchase_date, "
        "v.battery_capacity_kwh, o.owner_name, o.owner_id "
        "FROM vehicles v "
        "JOIN owners o ON v.owner_id = o.owner_id ORDER BY v.vehicle_id"
    ))

# ── Owner Analysis ─────────────────────────────────────────────────────────────
@app.route("/api/owner-analysis/<int:owner_id>")
@login_required
def owner_analysis(owner_id):
    battery_trend = query(
        """
        SELECT bh.record_date,
               bh.soh,
               bh.degradation,
               v.vehicle_number,
               AVG(bh.soh) OVER (
                   PARTITION BY bh.vehicle_id
                   ORDER BY bh.record_date
                   ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
               ) AS soh_moving_avg
        FROM battery_health bh
        JOIN vehicles v ON bh.vehicle_id = v.vehicle_id
        WHERE v.owner_id = %s
        ORDER BY bh.record_date
        """, (owner_id,)
    )

    # FIX: column is 'energy_kwh' not 'energy_delivered_kwh'
    charging_stats = query(
        """
        SELECT v.vehicle_number,
               COUNT(cs.session_id)                            AS total_charges,
               ROUND(AVG(cs.energy_kwh)::numeric, 2)          AS avg_energy_kwh,
               SUM(CASE WHEN cs.charge_type = 'fast' THEN 1 ELSE 0 END) AS fast_charge_count,
               SUM(CASE WHEN cs.charge_type = 'slow' THEN 1 ELSE 0 END) AS slow_charge_count
        FROM charging_sessions cs
        JOIN vehicles v ON cs.vehicle_id = v.vehicle_id
        WHERE v.owner_id = %s
        GROUP BY v.vehicle_id, v.vehicle_number
        """, (owner_id,)
    )

    health_distribution = query(
        """
        SELECT
            COUNT(CASE WHEN bh.soh >= 90 THEN 1 END) AS excellent,
            COUNT(CASE WHEN bh.soh >= 80 AND bh.soh < 90 THEN 1 END) AS good,
            COUNT(CASE WHEN bh.soh >= 70 AND bh.soh < 80 THEN 1 END) AS fair,
            COUNT(CASE WHEN bh.soh < 70 THEN 1 END) AS critical
        FROM battery_health bh
        JOIN vehicles v ON bh.vehicle_id = v.vehicle_id
        WHERE v.owner_id = %s
        """, (owner_id,)
    )

    return jsonify({
        "battery_trend":      [dict(r) for r in battery_trend],
        "charging_stats":     [dict(r) for r in charging_stats],
        "health_distribution": dict(health_distribution[0]) if health_distribution else {}
    })

# ── Car Recommendation ─────────────────────────────────────────────────────────
@app.route("/api/recommend/<int:vehicle_id>", methods=["GET", "POST"])
@login_required
def recommend(vehicle_id):
    # ── Read user preferences from POST body (or fall back to defaults) ────────
    prefs = request.json or {}
    budget_inr    = float(prefs.get("budget_inr", 10_000_000))   # default: no cap (1 crore)
    daily_km      = float(prefs.get("daily_km", 60))
    use_case      = prefs.get("use_case", "Mixed Use")
    charging_pref = prefs.get("charging_pref", "No Preference")  # "Fast Charge (DC)" / "Slow / Home Charge (AC)" / "No Preference"
    priority      = prefs.get("priority", "Max Range")           # "Max Range" / "Low Price" / "Large Battery Capacity" / "Brand Reputation"

    # Map UI labels → DB values
    charge_filter_map = {
        "Fast Charge (DC)":        "fast",
        "Slow / Home Charge (AC)": "slow",
        "No Preference":           None,
    }
    charge_filter = charge_filter_map.get(charging_pref, None)

    # Minimum range: 2× daily km so the car covers two days without a recharge
    min_range_km = daily_km * 2

    # ── Battery data ───────────────────────────────────────────────────────────
    bh = query(
        "SELECT soh, degradation FROM battery_health "
        "WHERE vehicle_id = %s ORDER BY record_date DESC LIMIT 1",
        (vehicle_id,), fetchall=False
    )

    charging = query(
        """
        SELECT
            COUNT(*) AS total_sessions,
            SUM(CASE WHEN charge_type = 'fast' THEN 1 ELSE 0 END)::float
              / NULLIF(COUNT(*), 0) * 100 AS fast_charge_pct,
            AVG(energy_kwh) AS avg_energy_kwh
        FROM charging_sessions WHERE vehicle_id = %s
        """,
        (vehicle_id,), fetchall=False
    )

    vehicle = query(
        "SELECT v.model, v.battery_capacity_kwh, o.owner_name "
        "FROM vehicles v JOIN owners o ON v.owner_id = o.owner_id "
        "WHERE v.vehicle_id = %s",
        (vehicle_id,), fetchall=False
    )

    if not bh or not vehicle:
        return jsonify({"error": "Vehicle not found"}), 404

    soh            = float(bh["soh"])
    degradation    = float(bh["degradation"])
    fast_pct       = float(charging["fast_charge_pct"] or 0) if charging else 0
    avg_energy_kwh = float(charging["avg_energy_kwh"] or 0) if charging else 0

    # ── Rule engine: urgency + reasons ────────────────────────────────────────
    reasons = []
    urgency_levels  = ["Low", "High", "Critical"]
    upgrade_urgency = "Low"

    if soh < 70:
        reasons.append("Battery SOH is critically low (< 70%) — immediate upgrade advised")
        upgrade_urgency = "Critical"
    elif soh < 80:
        reasons.append("Battery SOH is below 80% — upgrade recommended within 6 months")
        upgrade_urgency = "High"

    if degradation > 20:
        reasons.append(f"Battery has degraded {degradation:.1f}% from original capacity")
        if urgency_levels.index("High") > urgency_levels.index(upgrade_urgency):
            upgrade_urgency = "High"

    if fast_pct > 60:
        reasons.append(f"{fast_pct:.0f}% of charges are fast — accelerates battery wear")

    if budget_inr < 10_000_000:
        reasons.append(f"Filtering cars within your budget of ₹{budget_inr/100000:.0f}L")

    if daily_km > 0:
        reasons.append(f"Showing cars with ≥ {min_range_km:.0f} km range (2× your {daily_km:.0f} km/day)")

    if use_case in ("Highway / Long Distance", "Ride Sharing / Commercial"):
        reasons.append(f"Use case '{use_case}' — prioritising long range and large battery")

    # ── Minimum battery capacity ───────────────────────────────────────────────
    # Use avg_energy_kwh from history, but also enforce range-based floor
    min_capacity_from_usage = avg_energy_kwh * 5 if avg_energy_kwh > 0 else 30

    # For highway / commercial push to larger batteries — but only if budget allows
    # (budget < 25L → no car has 60kWh, so don't set an impossible floor)
    if use_case in ("Highway / Long Distance", "Ride Sharing / Commercial"):
        if budget_inr >= 2_500_000:
            min_capacity_from_usage = max(min_capacity_from_usage, 60)
        else:
            min_capacity_from_usage = max(min_capacity_from_usage, 30)
    elif use_case == "City Commuting":
        min_capacity_from_usage = max(min_capacity_from_usage, 20)

    # ── Priority → ORDER BY expression ────────────────────────────────────────
    order_sql = {
        "Max Range":               "range_km DESC, battery_capacity_kwh DESC",
        "Low Price":               "price_inr ASC, range_km DESC",
        "Large Battery Capacity":  "battery_capacity_kwh DESC, range_km DESC",
        "Brand Reputation":        "range_km DESC, price_inr DESC",   # proxy: premium = pricier + longer range
    }.get(priority, "range_km DESC")

    # ── Build WHERE clauses dynamically ───────────────────────────────────────
    where_clauses = [
        "battery_capacity_kwh >= %s",
        "range_km >= %s",
        "price_inr <= %s",
    ]
    params = [min_capacity_from_usage, min_range_km, budget_inr]

    if charge_filter:
        where_clauses.append("(charge_type_supported = 'both' OR charge_type_supported = %s)")
        params.append(charge_filter)
    else:
        # No preference — accept all charge types
        where_clauses.append("charge_type_supported IN ('fast', 'slow', 'both')")

    # Critical SOH → boost battery capacity only if budget allows
    if soh < 70 and budget_inr >= 2_500_000:
        where_clauses.append("battery_capacity_kwh >= 60")

    where_str = " AND ".join(where_clauses)

    recommended = query(
        f"""
        SELECT car_name, brand, range_km, battery_capacity_kwh,
               charge_type_supported, price_inr,
               CASE
                   WHEN battery_capacity_kwh >= 75 THEN 'Long Range'
                   WHEN battery_capacity_kwh >= 50 THEN 'Mid Range'
                   ELSE 'City'
               END AS category
        FROM car_catalog
        WHERE {where_str}
        ORDER BY {order_sql}
        LIMIT 5
        """,
        tuple(params)
    )

    # ── If strict filters return nothing, relax capacity/range but KEEP budget ──
    if not recommended:
        reasons.append("No exact matches — relaxing battery size & range filters slightly")
        # Keep: price_inr <= budget_inr  (NEVER remove this)
        relaxed_params = [budget_inr]
        relaxed_where  = ["price_inr <= %s"]
        if charge_filter:
            relaxed_where.append("(charge_type_supported = 'both' OR charge_type_supported = %s)")
            relaxed_params.append(charge_filter)
        recommended = query(
            f"""
            SELECT car_name, brand, range_km, battery_capacity_kwh,
                   charge_type_supported, price_inr,
                   CASE
                       WHEN battery_capacity_kwh >= 75 THEN 'Long Range'
                       WHEN battery_capacity_kwh >= 50 THEN 'Mid Range'
                       ELSE 'City'
                   END AS category
            FROM car_catalog
            WHERE {" AND ".join(relaxed_where)}
            ORDER BY {order_sql}
            LIMIT 5
            """,
            tuple(relaxed_params)
        )
        # If still nothing (budget truly too low for any car), return empty with a clear message
        if not recommended:
            reasons.append(f"⚠️ No EVs found within ₹{budget_inr/100000:.0f}L budget in our catalog. Consider increasing your budget.")

    return jsonify({
        "vehicle":         dict(vehicle),
        "current_soh":     soh,
        "degradation":     degradation,
        "fast_charge_pct": round(fast_pct, 1),
        "upgrade_urgency": upgrade_urgency,
        "reasons":         reasons if reasons else ["Battery health is good. No immediate upgrade needed."],
        "recommendations": [dict(r) for r in recommended],
        "filters_applied": {
            "budget_inr":    budget_inr,
            "min_range_km":  min_range_km,
            "charging_pref": charging_pref,
            "priority":      priority,
            "use_case":      use_case,
        }
    })

# ── Admin: RBAC demo ───────────────────────────────────────────────────────────
@app.route("/api/admin/users")
@login_required
@role_required("admin")
def admin_users():
    return jsonify(query(
        "SELECT user_id, username, role, owner_id FROM app_users ORDER BY user_id"
    ))

@app.route("/api/admin/audit-trail")
@login_required
@role_required("admin")
def audit_trail():
    return jsonify(query(
        "SELECT * FROM audit_trail ORDER BY changed_at DESC LIMIT 100"
    ))

# ── Maintenance ────────────────────────────────────────────────────────────────
@app.route("/api/maintenance")
@login_required
def maintenance():
    return jsonify(query(
        "SELECT ms.*, v.vehicle_number FROM maintenance_schedule ms "
        "JOIN vehicles v ON ms.vehicle_id = v.vehicle_id "
        "ORDER BY ms.scheduled_date DESC"
    ))

if __name__ == "__main__":
    app.run(debug=True, port=5000)