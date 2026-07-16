"""
P6 - Clinical Staff Scheduling (PRD-06) - Phase 1 MVP
Flask + SQLite. Run: python app.py  ->  http://127.0.0.1:5000

Implements FR-1, FR-2, FR-3, FR-6, FR-14 plus the two Phase-1 rule checks:
  - Ratio rule   : min staff required per shift (warns while editing, blocks at publish)
  - Hour rule    : minimum 8h rest between two shifts for the same staff member
"""

import os
import sqlite3
from datetime import datetime, timedelta, date

from flask import Flask, g, render_template, request, redirect, url_for, flash

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "roster.db")
SCHEMA_PATH = os.path.join(BASE_DIR, "schema.sql")
SEED_PATH = os.path.join(BASE_DIR, "seed.sql")

MIN_REST_HOURS = 8

app = Flask(__name__)
app.secret_key = "dev-secret-key-for-demo-only"


# ---------------------------------------------------------------- database --

def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


@app.teardown_appcontext
def close_db(exception=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    fresh = not os.path.exists(DB_PATH)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    with open(SCHEMA_PATH) as f:
        conn.executescript(f.read())
    if fresh:
        with open(SEED_PATH) as f:
            conn.executescript(f.read())
        conn.commit()
    conn.close()


# ------------------------------------------------------------ small helpers --

def parse_time(hhmm):
    return datetime.strptime(hhmm, "%H:%M").time()


def shift_datetimes(shift_date_str, start_time_str, end_time_str):
    """Return (start_dt, end_dt) handling overnight shifts (end <= start -> +1 day)."""
    d = datetime.strptime(shift_date_str, "%Y-%m-%d").date()
    start_dt = datetime.combine(d, parse_time(start_time_str))
    end_dt = datetime.combine(d, parse_time(end_time_str))
    if end_dt <= start_dt:
        end_dt += timedelta(days=1)
    return start_dt, end_dt


def monday_of(d: date) -> date:
    return d - timedelta(days=d.weekday())


def week_dates(week_start: date):
    return [week_start + timedelta(days=i) for i in range(7)]


def get_or_create_draft_version(db, department_id, week_start_str):
    row = db.execute(
        """SELECT * FROM roster_versions
           WHERE department_id=? AND week_start_date=? AND is_locked=0
           ORDER BY version_number DESC LIMIT 1""",
        (department_id, week_start_str),
    ).fetchone()
    if row:
        return row
    last = db.execute(
        """SELECT MAX(version_number) AS v FROM roster_versions
           WHERE department_id=? AND week_start_date=?""",
        (department_id, week_start_str),
    ).fetchone()
    next_version = (last["v"] or 0) + 1
    cur = db.execute(
        "INSERT INTO roster_versions (department_id, week_start_date, version_number) VALUES (?,?,?)",
        (department_id, week_start_str, next_version),
    )
    db.commit()
    return db.execute("SELECT * FROM roster_versions WHERE id=?", (cur.lastrowid,)).fetchone()


# --------------------------------------------------------------- rule checks --

def staff_is_credential_blocked(db, staff_id):
    """FR-2: any expired mandatory credential blocks new roster assignment."""
    row = db.execute(
        "SELECT credential_type, expiry_date FROM credentials WHERE staff_id=? AND status='expired' LIMIT 1",
        (staff_id,),
    ).fetchone()
    return row


def check_rest_hour_rule(db, staff_id, shift_template_id, shift_date_str, exclude_entry_id=None):
    """Hard rule: >=8h rest required between adjacent shifts for the same staff member."""
    new_template = db.execute("SELECT * FROM shift_templates WHERE id=?", (shift_template_id,)).fetchone()
    new_start, new_end = shift_datetimes(shift_date_str, new_template["start_time"], new_template["end_time"])

    d = datetime.strptime(shift_date_str, "%Y-%m-%d").date()
    window = [(d - timedelta(days=1)).isoformat(), d.isoformat(), (d + timedelta(days=1)).isoformat()]

    q = """SELECT re.id, re.shift_date, st.start_time, st.end_time, st.name
           FROM roster_entries re JOIN shift_templates st ON st.id = re.shift_template_id
           WHERE re.staff_id=? AND re.status='assigned' AND re.shift_date IN (?,?,?)"""
    params = [staff_id] + window
    if exclude_entry_id:
        q += " AND re.id != ?"
        params.append(exclude_entry_id)
    rows = db.execute(q, params).fetchall()

    for r in rows:
        ex_start, ex_end = shift_datetimes(r["shift_date"], r["start_time"], r["end_time"])
        if ex_start == new_start and ex_end == new_end:
            continue  # same slot, ignore
        gap1 = (new_start - ex_end).total_seconds() / 3600.0
        gap2 = (ex_start - new_end).total_seconds() / 3600.0
        gap = gap1 if gap1 >= 0 else (gap2 if gap2 >= 0 else None)
        if gap is not None and gap < MIN_REST_HOURS:
            return f"Only {gap:.1f}h rest between this shift and '{r['name']}' on {r['shift_date']} (minimum {MIN_REST_HOURS}h required)"
    return None  # OK


def ratio_status_for_shift(db, shift_template_id, shift_date_str, roster_version_id):
    template = db.execute("SELECT * FROM shift_templates WHERE id=?", (shift_template_id,)).fetchone()
    count = db.execute(
        """SELECT COUNT(*) AS c FROM roster_entries
           WHERE shift_template_id=? AND shift_date=? AND roster_version_id=? AND status='assigned'""",
        (shift_template_id, shift_date_str, roster_version_id),
    ).fetchone()["c"]
    return count, template["min_staff_required"]


def credential_badge(status):
    return {"valid": "ok", "expiring_soon": "warn", "expired": "danger"}.get(status, "")


app.jinja_env.filters["credential_badge"] = credential_badge


# -------------------------------------------------------------------- views --

@app.route("/")
def home():
    db = get_db()
    staff_count = db.execute("SELECT COUNT(*) c FROM staff WHERE active=1").fetchone()["c"]
    expired = db.execute("SELECT COUNT(*) c FROM credentials WHERE status='expired'").fetchone()["c"]
    expiring = db.execute("SELECT COUNT(*) c FROM credentials WHERE status='expiring_soon'").fetchone()["c"]
    pending_leave = db.execute("SELECT COUNT(*) c FROM leave_requests WHERE status='pending'").fetchone()["c"]
    departments = db.execute("SELECT * FROM departments").fetchall()
    return render_template(
        "home.html",
        staff_count=staff_count,
        expired=expired,
        expiring=expiring,
        pending_leave=pending_leave,
        departments=departments,
    )


# ---- Staff registry (FR-1) --------------------------------------------------

@app.route("/staff")
def staff_list():
    db = get_db()
    department_id = request.args.get("department_id", type=int)
    role = request.args.get("role", "")
    q = """SELECT s.*, d.name AS department_name FROM staff s JOIN departments d ON d.id=s.department_id
           WHERE s.active=1"""
    params = []
    if department_id:
        q += " AND s.department_id=?"
        params.append(department_id)
    if role:
        q += " AND s.role=?"
        params.append(role)
    q += " ORDER BY s.full_name"
    staff = db.execute(q, params).fetchall()
    departments = db.execute("SELECT * FROM departments").fetchall()
    return render_template("staff_list.html", staff=staff, departments=departments,
                            department_id=department_id, role=role)


@app.route("/staff/add", methods=["GET", "POST"])
def staff_add():
    db = get_db()
    departments = db.execute("SELECT * FROM departments").fetchall()
    if request.method == "POST":
        employee_code = request.form["employee_code"].strip()
        full_name = request.form["full_name"].strip()
        role = request.form["role"]
        department_id = request.form["department_id"]
        employment_type = request.form.get("employment_type", "permanent")

        if not employee_code or not full_name or not department_id:
            flash("Employee code, name, and department are required.", "error")
            return render_template("staff_add.html", departments=departments, form=request.form)

        existing = db.execute("SELECT id FROM staff WHERE employee_code=?", (employee_code,)).fetchone()
        if existing:
            flash(f"Employee code '{employee_code}' already exists.", "error")
            return render_template("staff_add.html", departments=departments, form=request.form)

        db.execute(
            """INSERT INTO staff (employee_code, full_name, role, department_id, employment_type)
               VALUES (?,?,?,?,?)""",
            (employee_code, full_name, role, department_id, employment_type),
        )
        db.commit()
        flash(f"Staff member '{full_name}' added.", "success")
        return redirect(url_for("staff_list"))

    return render_template("staff_add.html", departments=departments, form={})


# ---- Credential registry (FR-2) --------------------------------------------

@app.route("/staff/<int:staff_id>")
def staff_profile(staff_id):
    db = get_db()
    staff = db.execute(
        """SELECT s.*, d.name AS department_name FROM staff s JOIN departments d ON d.id=s.department_id
           WHERE s.id=?""", (staff_id,)).fetchone()
    if not staff:
        flash("Staff member not found.", "error")
        return redirect(url_for("staff_list"))
    credentials = db.execute(
        "SELECT * FROM credentials WHERE staff_id=? ORDER BY expiry_date", (staff_id,)
    ).fetchall()
    blocked = staff_is_credential_blocked(db, staff_id)
    return render_template("staff_profile.html", staff=staff, credentials=credentials, blocked=blocked)


@app.route("/staff/<int:staff_id>/credentials/add", methods=["POST"])
def credential_add(staff_id):
    db = get_db()
    credential_type = request.form["credential_type"]
    credential_no = request.form["credential_no"].strip()
    expiry_date_str = request.form["expiry_date"]

    if not credential_no or not expiry_date_str:
        flash("Credential number and expiry date are required.", "error")
        return redirect(url_for("staff_profile", staff_id=staff_id))

    expiry = datetime.strptime(expiry_date_str, "%Y-%m-%d").date()
    today = date.today()
    days_left = (expiry - today).days
    if days_left < 0:
        status = "expired"
    elif days_left <= 60:
        status = "expiring_soon"
    else:
        status = "valid"

    db.execute(
        """INSERT INTO credentials (staff_id, credential_type, credential_no, expiry_date, status, verified)
           VALUES (?,?,?,?,?,0)""",
        (staff_id, credential_type, credential_no, expiry_date_str, status),
    )
    db.commit()
    flash(f"Credential added ({status.replace('_',' ')}).", "success" if status == "valid" else "warning")
    return redirect(url_for("staff_profile", staff_id=staff_id))


# ---- Shift templates (FR-3) -------------------------------------------------

@app.route("/shift-templates")
def shift_template_list():
    db = get_db()
    department_id = request.args.get("department_id", type=int)
    departments = db.execute("SELECT * FROM departments").fetchall()
    if not department_id and departments:
        department_id = departments[0]["id"]
    templates = db.execute(
        "SELECT * FROM shift_templates WHERE department_id=? ORDER BY shift_type", (department_id,)
    ).fetchall() if department_id else []
    return render_template("shift_templates.html", templates=templates, departments=departments,
                            department_id=department_id)


@app.route("/shift-templates/add", methods=["POST"])
def shift_template_add():
    db = get_db()
    department_id = request.form["department_id"]
    name = request.form["name"].strip()
    shift_type = request.form["shift_type"]
    start_time = request.form["start_time"]
    end_time = request.form["end_time"]
    min_staff_required = int(request.form.get("min_staff_required", 1))

    start_dt, end_dt = shift_datetimes("2000-01-01", start_time, end_time)
    duration_hours = round((end_dt - start_dt).total_seconds() / 3600.0, 1)

    db.execute(
        """INSERT INTO shift_templates (department_id, name, shift_type, start_time, end_time,
           duration_hours, min_staff_required) VALUES (?,?,?,?,?,?,?)""",
        (department_id, name, shift_type, start_time, end_time, duration_hours, min_staff_required),
    )
    db.commit()
    flash(f"Shift template '{name}' created ({duration_hours}h).", "success")
    return redirect(url_for("shift_template_list", department_id=department_id))


# ---- Roster grid + publish (FR-14) -----------------------------------------

@app.route("/roster")
def roster_grid():
    db = get_db()
    departments = db.execute("SELECT * FROM departments").fetchall()
    department_id = request.args.get("department_id", type=int) or (departments[0]["id"] if departments else None)

    week_start_param = request.args.get("week_start")
    if week_start_param:
        week_start = datetime.strptime(week_start_param, "%Y-%m-%d").date()
    else:
        week_start = monday_of(date.today())
    week_start_str = week_start.isoformat()
    days = week_dates(week_start)

    version = get_or_create_draft_version(db, department_id, week_start_str) if department_id else None

    staff = db.execute(
        "SELECT * FROM staff WHERE department_id=? AND active=1 ORDER BY full_name", (department_id,)
    ).fetchall() if department_id else []
    templates = db.execute(
        "SELECT * FROM shift_templates WHERE department_id=? ORDER BY shift_type", (department_id,)
    ).fetchall() if department_id else []

    entries = db.execute(
        """SELECT re.*, st.name AS shift_name, st.shift_type FROM roster_entries re
           JOIN shift_templates st ON st.id = re.shift_template_id
           WHERE re.roster_version_id=? AND re.status='assigned'""",
        (version["id"],),
    ).fetchall() if version else []

    grid = {}
    for e in entries:
        grid[(e["staff_id"], e["shift_date"])] = e

    # ratio status per (template, date) for the warning banner
    ratio_issues = []
    for t in templates:
        for d in days:
            count, minimum = ratio_status_for_shift(db, t["id"], d.isoformat(), version["id"]) if version else (0, t["min_staff_required"])
            if count < minimum:
                ratio_issues.append({"date": d.isoformat(), "shift": t["name"], "count": count, "min": minimum})

    return render_template(
        "roster_grid.html",
        departments=departments, department_id=department_id,
        week_start=week_start_str, prev_week=(week_start - timedelta(days=7)).isoformat(),
        next_week=(week_start + timedelta(days=7)).isoformat(),
        days=days, staff=staff, templates=templates, grid=grid, version=version,
        ratio_issues=ratio_issues,
    )


@app.route("/roster/entries/add", methods=["POST"])
def roster_entry_add():
    db = get_db()
    staff_id = int(request.form["staff_id"])
    shift_template_id = int(request.form["shift_template_id"])
    shift_date = request.form["shift_date"]
    department_id = request.form["department_id"]
    week_start = request.form["week_start"]

    redirect_url = url_for("roster_grid", department_id=department_id, week_start=week_start)

    # 1. Credential hard block (FR-2)
    blocked = staff_is_credential_blocked(db, staff_id)
    if blocked:
        flash(f"BLOCKED: staff has an expired {blocked['credential_type'].upper()} "
              f"(expired {blocked['expiry_date']}) — cannot be assigned until renewed.", "error")
        return redirect(redirect_url)

    # 2. Rest-hour hard block
    rest_violation = check_rest_hour_rule(db, staff_id, shift_template_id, shift_date)
    if rest_violation:
        flash(f"BLOCKED (rest-hour rule): {rest_violation}", "error")
        return redirect(redirect_url)

    # existing same-slot duplicate guard
    version = get_or_create_draft_version(db, department_id, week_start)
    dup = db.execute(
        """SELECT id FROM roster_entries WHERE staff_id=? AND shift_template_id=? AND shift_date=?
           AND roster_version_id=? AND status='assigned'""",
        (staff_id, shift_template_id, shift_date, version["id"]),
    ).fetchone()
    if dup:
        flash("This staff member is already assigned to that shift on that date.", "error")
        return redirect(redirect_url)

    db.execute(
        """INSERT INTO roster_entries (staff_id, shift_template_id, roster_version_id, shift_date, status)
           VALUES (?,?,?,?,'assigned')""",
        (staff_id, shift_template_id, version["id"], shift_date),
    )
    db.commit()

    # 3. Ratio soft warning (non-blocking here; hard-blocks only at publish)
    count, minimum = ratio_status_for_shift(db, shift_template_id, shift_date, version["id"])
    if count < minimum:
        flash(f"Saved, but shift still understaffed: {count}/{minimum} assigned (ratio rule).", "warning")
    else:
        flash("Shift assigned.", "success")
    return redirect(redirect_url)


@app.route("/roster/entries/<int:entry_id>/remove", methods=["POST"])
def roster_entry_remove(entry_id):
    db = get_db()
    entry = db.execute("SELECT * FROM roster_entries WHERE id=?", (entry_id,)).fetchone()
    if not entry:
        flash("Entry not found.", "error")
        return redirect(url_for("roster_grid"))
    version = db.execute("SELECT * FROM roster_versions WHERE id=?", (entry["roster_version_id"],)).fetchone()
    if version["is_locked"]:
        flash("Cannot remove — this roster is published and locked.", "error")
    else:
        db.execute("DELETE FROM roster_entries WHERE id=?", (entry_id,))
        db.commit()
        flash("Shift entry removed.", "success")
    return redirect(url_for("roster_grid", department_id=version["department_id"], week_start=version["week_start_date"]))


@app.route("/roster/versions/<int:version_id>/publish", methods=["POST"])
def roster_publish(version_id):
    db = get_db()
    version = db.execute("SELECT * FROM roster_versions WHERE id=?", (version_id,)).fetchone()
    if not version:
        flash("Roster version not found.", "error")
        return redirect(url_for("roster_grid"))
    if version["is_locked"]:
        flash("This roster is already published.", "warning")
        return redirect(url_for("roster_grid", department_id=version["department_id"], week_start=version["week_start_date"]))

    templates = db.execute("SELECT * FROM shift_templates WHERE department_id=?", (version["department_id"],)).fetchall()
    days = week_dates(datetime.strptime(version["week_start_date"], "%Y-%m-%d").date())

    shortfalls = []
    for t in templates:
        for d in days:
            count, minimum = ratio_status_for_shift(db, t["id"], d.isoformat(), version_id)
            if count < minimum:
                shortfalls.append(f"{d.isoformat()} — {t['name']}: {count}/{minimum} staff")

    if shortfalls:
        flash("BLOCKED — cannot publish, understaffed shifts remain: " + "; ".join(shortfalls), "error")
        return redirect(url_for("roster_grid", department_id=version["department_id"], week_start=version["week_start_date"]))

    db.execute(
        "UPDATE roster_versions SET is_locked=1, published_at=? WHERE id=?",
        (datetime.now().isoformat(timespec="seconds"), version_id),
    )
    # notify each assigned staff member (FR-14)
    staff_ids = db.execute(
        "SELECT DISTINCT staff_id FROM roster_entries WHERE roster_version_id=? AND status='assigned'",
        (version_id,),
    ).fetchall()
    for row in staff_ids:
        db.execute(
            "INSERT INTO notifications (staff_id, channel, status, message) VALUES (?,?,?,?)",
            (row["staff_id"], "app", "sent", f"Your roster for week of {version['week_start_date']} has been published."),
        )
    db.commit()
    flash("Roster published and locked. Staff notified.", "success")
    return redirect(url_for("roster_grid", department_id=version["department_id"], week_start=version["week_start_date"]))


# ---- Leave management (FR-6) ------------------------------------------------

@app.route("/leave")
def leave_list():
    db = get_db()
    requests_ = db.execute(
        """SELECT lr.*, s.full_name, lt.code AS leave_code FROM leave_requests lr
           JOIN staff s ON s.id = lr.staff_id
           JOIN leave_types lt ON lt.id = lr.leave_type_id
           ORDER BY lr.id DESC"""
    ).fetchall()
    return render_template("leave_list.html", requests=requests_)


@app.route("/leave/add", methods=["GET", "POST"])
def leave_add():
    db = get_db()
    staff = db.execute("SELECT * FROM staff WHERE active=1 ORDER BY full_name").fetchall()
    leave_types = db.execute("SELECT * FROM leave_types").fetchall()

    if request.method == "POST":
        staff_id = int(request.form["staff_id"])
        leave_type_id = int(request.form["leave_type_id"])
        start_date = request.form["start_date"]
        end_date = request.form["end_date"]
        reason = request.form.get("reason", "").strip()

        if end_date < start_date:
            flash("End date cannot be before start date.", "error")
            return render_template("leave_add.html", staff=staff, leave_types=leave_types, form=request.form)

        overlap = db.execute(
            """SELECT re.shift_date, rv.is_locked FROM roster_entries re
               JOIN roster_versions rv ON rv.id = re.roster_version_id
               WHERE re.staff_id=? AND re.status='assigned' AND rv.is_locked=1
                 AND re.shift_date BETWEEN ? AND ?""",
            (staff_id, start_date, end_date),
        ).fetchall()

        db.execute(
            """INSERT INTO leave_requests (staff_id, leave_type_id, start_date, end_date, reason, status)
               VALUES (?,?,?,?,?, 'pending')""",
            (staff_id, leave_type_id, start_date, end_date, reason),
        )
        db.commit()

        if overlap:
            dates = ", ".join(r["shift_date"] for r in overlap)
            flash(f"Leave request submitted — WARNING: overlaps published shift(s) on {dates}.", "warning")
        else:
            flash("Leave request submitted.", "success")
        return redirect(url_for("leave_list"))

    return render_template("leave_add.html", staff=staff, leave_types=leave_types, form={})


@app.route("/leave/<int:request_id>/<decision>", methods=["POST"])
def leave_decide(request_id, decision):
    db = get_db()
    if decision not in ("approve", "reject"):
        flash("Invalid decision.", "error")
        return redirect(url_for("leave_list"))

    lr = db.execute("SELECT * FROM leave_requests WHERE id=?", (request_id,)).fetchone()
    if not lr:
        flash("Leave request not found.", "error")
        return redirect(url_for("leave_list"))

    new_status = "approved" if decision == "approve" else "rejected"
    db.execute("UPDATE leave_requests SET status=? WHERE id=?", (new_status, request_id))

    if new_status == "approved":
        start = datetime.strptime(lr["start_date"], "%Y-%m-%d").date()
        end = datetime.strptime(lr["end_date"], "%Y-%m-%d").date()
        days = (end - start).days + 1
        year = start.year
        bal = db.execute(
            "SELECT * FROM leave_balances WHERE staff_id=? AND leave_type_id=? AND year=?",
            (lr["staff_id"], lr["leave_type_id"], year),
        ).fetchone()
        if bal:
            db.execute(
                "UPDATE leave_balances SET used_days = used_days + ? WHERE id=?",
                (days, bal["id"]),
            )
        else:
            db.execute(
                """INSERT INTO leave_balances (staff_id, leave_type_id, year, allocated_days, used_days)
                   VALUES (?,?,?,0,?)""",
                (lr["staff_id"], lr["leave_type_id"], year, days),
            )

    db.commit()
    flash(f"Leave request #{request_id} {new_status}.", "success")
    return redirect(url_for("leave_list"))


# ------------------------------------------------------------------- runner --

if __name__ == "__main__":
    init_db()
    app.run(debug=True, port=5000)
