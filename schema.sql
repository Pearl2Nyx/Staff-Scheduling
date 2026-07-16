PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS departments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    unit_type TEXT NOT NULL CHECK (unit_type IN ('general_ward','icu','ot','emergency','opd','other'))
);

CREATE TABLE IF NOT EXISTS staff (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    employee_code TEXT NOT NULL UNIQUE,
    full_name TEXT NOT NULL,
    role TEXT NOT NULL CHECK (role IN ('nurse','resident','technician','consultant','dept_head')),
    department_id INTEGER NOT NULL REFERENCES departments(id),
    employment_type TEXT NOT NULL DEFAULT 'permanent' CHECK (employment_type IN ('permanent','contract','locum')),
    active INTEGER NOT NULL DEFAULT 1 CHECK (active IN (0,1))
);

CREATE TABLE IF NOT EXISTS skills (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS staff_skills (
    staff_id INTEGER NOT NULL REFERENCES staff(id),
    skill_id INTEGER NOT NULL REFERENCES skills(id),
    PRIMARY KEY (staff_id, skill_id)
);

CREATE TABLE IF NOT EXISTS credentials (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    staff_id INTEGER NOT NULL REFERENCES staff(id),
    credential_type TEXT NOT NULL CHECK (credential_type IN
        ('nmc_registration','nursing_council','bls','acls','pharmacist_licence')),
    credential_no TEXT NOT NULL,
    expiry_date TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'valid' CHECK (status IN ('valid','expiring_soon','expired')),
    verified INTEGER NOT NULL DEFAULT 0 CHECK (verified IN (0,1))
);

CREATE TABLE IF NOT EXISTS shift_templates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    department_id INTEGER NOT NULL REFERENCES departments(id),
    name TEXT NOT NULL,
    shift_type TEXT NOT NULL CHECK (shift_type IN ('morning','evening','night','on_call')),
    start_time TEXT NOT NULL,
    end_time TEXT NOT NULL,
    duration_hours REAL NOT NULL,
    min_staff_required INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS roster_versions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    department_id INTEGER NOT NULL REFERENCES departments(id),
    week_start_date TEXT NOT NULL,
    version_number INTEGER NOT NULL,
    published_at TEXT,
    is_locked INTEGER NOT NULL DEFAULT 0 CHECK (is_locked IN (0,1))
);

CREATE TABLE IF NOT EXISTS roster_entries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    staff_id INTEGER NOT NULL REFERENCES staff(id),
    shift_template_id INTEGER NOT NULL REFERENCES shift_templates(id),
    roster_version_id INTEGER NOT NULL REFERENCES roster_versions(id),
    shift_date TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'assigned' CHECK (status IN ('assigned','cancelled'))
);

CREATE TABLE IF NOT EXISTS leave_types (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    max_days_per_year INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS leave_balances (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    staff_id INTEGER NOT NULL REFERENCES staff(id),
    leave_type_id INTEGER NOT NULL REFERENCES leave_types(id),
    year INTEGER NOT NULL,
    allocated_days REAL NOT NULL,
    used_days REAL NOT NULL DEFAULT 0,
    UNIQUE (staff_id, leave_type_id, year)
);

CREATE TABLE IF NOT EXISTS leave_requests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    staff_id INTEGER NOT NULL REFERENCES staff(id),
    leave_type_id INTEGER NOT NULL REFERENCES leave_types(id),
    start_date TEXT NOT NULL,
    end_date TEXT NOT NULL,
    reason TEXT,
    status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending','approved','rejected'))
);

CREATE TABLE IF NOT EXISTS notifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    staff_id INTEGER NOT NULL REFERENCES staff(id),
    roster_entry_id INTEGER REFERENCES roster_entries(id),
    channel TEXT NOT NULL CHECK (channel IN ('app','whatsapp','sms')),
    status TEXT NOT NULL DEFAULT 'sent' CHECK (status IN ('sent','failed')),
    message TEXT
);

CREATE INDEX IF NOT EXISTS idx_staff_department ON staff(department_id);
CREATE INDEX IF NOT EXISTS idx_credentials_staff ON credentials(staff_id);
CREATE INDEX IF NOT EXISTS idx_roster_entries_staff_date ON roster_entries(staff_id, shift_date);
CREATE INDEX IF NOT EXISTS idx_roster_entries_version ON roster_entries(roster_version_id);
