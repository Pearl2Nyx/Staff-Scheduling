INSERT INTO departments (name, unit_type) VALUES
    ('ICU', 'icu'),
    ('General Ward', 'general_ward');

INSERT INTO skills (name) VALUES
    ('ICU-trained'), ('dialysis'), ('scrub');

INSERT INTO staff (employee_code, full_name, role, department_id, employment_type) VALUES
    ('N-1042', 'A. Sharma', 'nurse', 1, 'permanent'),
    ('N-1043', 'R. Iyer',   'nurse', 1, 'permanent'),
    ('N-1044', 'K. Nair',   'nurse', 1, 'contract'),
    ('N-2001', 'P. Verma',  'nurse', 2, 'permanent'),
    ('N-2002', 'S. Rao',    'nurse', 2, 'permanent');

INSERT INTO staff_skills (staff_id, skill_id) VALUES (1, 1), (2, 1), (3, 2);

-- A. Sharma (staff_id 1) has a deliberately EXPIRED ACLS credential -> roster-blocked, for the demo
INSERT INTO credentials (staff_id, credential_type, credential_no, expiry_date, status, verified) VALUES
    (1, 'bls',  'BLS-88213', '2026-09-01', 'valid', 1),
    (1, 'acls', 'AC-11029',  '2026-06-30', 'expired', 1),
    (2, 'bls',  'BLS-88214', '2026-08-05', 'expiring_soon', 1),
    (3, 'bls',  'BLS-88215', '2027-01-10', 'valid', 1),
    (4, 'bls',  'BLS-88216', '2026-10-01', 'valid', 1);

-- ICU Morning deliberately needs 3 staff (ratio rule will trigger with fewer assigned)
INSERT INTO shift_templates (department_id, name, shift_type, start_time, end_time, duration_hours, min_staff_required) VALUES
    (1, 'ICU Morning', 'morning', '07:00', '15:00', 8.0, 3),
    (1, 'ICU Night',   'night',   '22:00', '06:00', 8.0, 2),
    (2, 'Ward Morning','morning', '08:00', '16:00', 8.0, 2),
    (2, 'Ward Night',  'night',   '20:00', '08:00', 12.0, 1);

INSERT INTO leave_types (code, name, max_days_per_year) VALUES
    ('EL', 'Earned Leave', 21),
    ('CL', 'Casual Leave', 12),
    ('SL', 'Sick Leave', 12),
    ('ML', 'Maternity Leave', 182);

INSERT INTO leave_balances (staff_id, leave_type_id, year, allocated_days, used_days) VALUES
    (1, 1, 2026, 21, 13), (1, 2, 2026, 12, 4),
    (2, 1, 2026, 21, 5),  (2, 2, 2026, 12, 2),
    (3, 1, 2026, 21, 0),  (3, 2, 2026, 12, 1);
