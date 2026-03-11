-- ============================================================
-- Seed script for agentic_node database
-- Tables: departments, employees, salaries, projects, sales
-- ============================================================

-- Departments
CREATE TABLE IF NOT EXISTS departments (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    location VARCHAR(100) NOT NULL,
    budget NUMERIC(15, 2) NOT NULL
);

-- Employees
CREATE TABLE IF NOT EXISTS employees (
    id SERIAL PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    department_id INTEGER REFERENCES departments(id),
    job_title VARCHAR(100) NOT NULL,
    hire_date DATE NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'active'
);

-- Salaries (history)
CREATE TABLE IF NOT EXISTS salaries (
    id SERIAL PRIMARY KEY,
    employee_id INTEGER REFERENCES employees(id),
    amount NUMERIC(12, 2) NOT NULL,
    effective_date DATE NOT NULL,
    salary_type VARCHAR(20) NOT NULL DEFAULT 'annual'
);

-- Projects
CREATE TABLE IF NOT EXISTS projects (
    id SERIAL PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    department_id INTEGER REFERENCES departments(id),
    start_date DATE NOT NULL,
    end_date DATE,
    budget NUMERIC(15, 2),
    status VARCHAR(20) NOT NULL DEFAULT 'active'
);

-- Project assignments (many-to-many)
CREATE TABLE IF NOT EXISTS project_assignments (
    id SERIAL PRIMARY KEY,
    employee_id INTEGER REFERENCES employees(id),
    project_id INTEGER REFERENCES projects(id),
    role VARCHAR(50) NOT NULL,
    assigned_date DATE NOT NULL
);

-- Monthly sales
CREATE TABLE IF NOT EXISTS sales (
    id SERIAL PRIMARY KEY,
    employee_id INTEGER REFERENCES employees(id),
    product VARCHAR(100) NOT NULL,
    region VARCHAR(50) NOT NULL,
    amount NUMERIC(12, 2) NOT NULL,
    quantity INTEGER NOT NULL,
    sale_date DATE NOT NULL
);

-- ============================================================
-- Seed data
-- ============================================================

-- Departments
INSERT INTO departments (name, location, budget) VALUES
    ('Engineering',      'New York',      1500000.00),
    ('Human Resources',  'Chicago',        450000.00),
    ('Sales',            'San Francisco', 1200000.00),
    ('Marketing',        'Los Angeles',    800000.00),
    ('Finance',          'New York',       600000.00),
    ('Operations',       'Chicago',        700000.00),
    ('Customer Support', 'Austin',         500000.00)
ON CONFLICT (name) DO NOTHING;

-- Employees
INSERT INTO employees (first_name, last_name, email, department_id, job_title, hire_date, status) VALUES
    ('Alice',   'Johnson',  'alice.johnson@company.com',   1, 'Senior Software Engineer',  '2020-03-15', 'active'),
    ('Bob',     'Smith',    'bob.smith@company.com',       1, 'Software Engineer',          '2021-07-01', 'active'),
    ('Carol',   'Williams', 'carol.williams@company.com',  1, 'Engineering Manager',        '2019-01-10', 'active'),
    ('David',   'Brown',    'david.brown@company.com',     1, 'DevOps Engineer',            '2022-02-20', 'active'),
    ('Eva',     'Davis',    'eva.davis@company.com',       2, 'HR Manager',                 '2018-06-01', 'active'),
    ('Frank',   'Miller',   'frank.miller@company.com',    2, 'HR Specialist',              '2021-09-15', 'active'),
    ('Grace',   'Wilson',   'grace.wilson@company.com',    3, 'Sales Director',             '2019-04-20', 'active'),
    ('Henry',   'Moore',    'henry.moore@company.com',     3, 'Sales Representative',       '2020-11-10', 'active'),
    ('Ivy',     'Taylor',   'ivy.taylor@company.com',      3, 'Sales Representative',       '2021-03-05', 'active'),
    ('Jack',    'Anderson', 'jack.anderson@company.com',   3, 'Account Manager',            '2022-06-15', 'active'),
    ('Karen',   'Thomas',   'karen.thomas@company.com',    4, 'Marketing Manager',          '2020-01-20', 'active'),
    ('Leo',     'Jackson',  'leo.jackson@company.com',     4, 'Content Strategist',         '2021-05-10', 'active'),
    ('Mia',     'White',    'mia.white@company.com',       4, 'SEO Specialist',             '2022-08-01', 'active'),
    ('Nathan',  'Harris',   'nathan.harris@company.com',   5, 'Finance Director',           '2018-03-01', 'active'),
    ('Olivia',  'Martin',   'olivia.martin@company.com',   5, 'Financial Analyst',          '2021-10-20', 'active'),
    ('Peter',   'Garcia',   'peter.garcia@company.com',    6, 'Operations Manager',         '2019-07-15', 'active'),
    ('Quinn',   'Martinez', 'quinn.martinez@company.com',  6, 'Logistics Coordinator',      '2022-01-10', 'active'),
    ('Rachel',  'Robinson', 'rachel.robinson@company.com', 7, 'Support Team Lead',          '2020-05-01', 'active'),
    ('Sam',     'Clark',    'sam.clark@company.com',       7, 'Support Agent',              '2021-12-01', 'active'),
    ('Tina',    'Lewis',    'tina.lewis@company.com',      7, 'Support Agent',              '2023-02-15', 'active'),
    ('Uma',     'Lee',      'uma.lee@company.com',         1, 'Junior Developer',           '2023-06-01', 'active'),
    ('Victor',  'Walker',   'victor.walker@company.com',   3, 'Sales Representative',       '2023-01-15', 'active'),
    ('Wendy',   'Hall',     'wendy.hall@company.com',      4, 'Graphic Designer',           '2022-11-01', 'active'),
    ('Xander',  'Allen',    'xander.allen@company.com',    5, 'Accountant',                 '2023-04-10', 'active'),
    ('Yara',    'Young',    'yara.young@company.com',      1, 'QA Engineer',                '2022-09-01', 'active')
ON CONFLICT (email) DO NOTHING;

-- Salaries
INSERT INTO salaries (employee_id, amount, effective_date) VALUES
    (1,  135000, '2024-01-01'), (1,  125000, '2022-01-01'), (1,  115000, '2020-03-15'),
    (2,  105000, '2024-01-01'), (2,   95000, '2022-01-01'),
    (3,  155000, '2024-01-01'), (3,  145000, '2021-01-01'),
    (4,  120000, '2024-01-01'),
    (5,  110000, '2024-01-01'), (5,  100000, '2020-01-01'),
    (6,   75000, '2024-01-01'),
    (7,  145000, '2024-01-01'), (7,  130000, '2021-01-01'),
    (8,   85000, '2024-01-01'),
    (9,   82000, '2024-01-01'),
    (10,  90000, '2024-01-01'),
    (11, 120000, '2024-01-01'),
    (12,  88000, '2024-01-01'),
    (13,  78000, '2024-01-01'),
    (14, 160000, '2024-01-01'), (14, 150000, '2020-01-01'),
    (15,  95000, '2024-01-01'),
    (16, 115000, '2024-01-01'),
    (17,  72000, '2024-01-01'),
    (18,  92000, '2024-01-01'),
    (19,  65000, '2024-01-01'),
    (20,  62000, '2024-01-01'),
    (21,  80000, '2024-01-01'),
    (22,  78000, '2024-01-01'),
    (23,  85000, '2024-01-01'),
    (24,  82000, '2024-01-01'),
    (25,  95000, '2024-01-01');

-- Projects
INSERT INTO projects (name, department_id, start_date, end_date, budget, status) VALUES
    ('Platform Redesign',       1, '2024-01-15', '2024-12-31', 450000, 'active'),
    ('Mobile App v2',           1, '2024-03-01', '2024-09-30', 300000, 'active'),
    ('Employee Wellness',       2, '2024-02-01', '2024-08-31', 50000,  'completed'),
    ('Q1 Sales Campaign',       3, '2024-01-01', '2024-03-31', 150000, 'completed'),
    ('Brand Refresh',           4, '2024-04-01', '2024-10-31', 200000, 'active'),
    ('Annual Audit',            5, '2024-01-01', '2024-06-30', 80000,  'completed'),
    ('Warehouse Automation',    6, '2024-05-01', NULL,         500000, 'active'),
    ('Help Desk Migration',     7, '2024-03-15', '2024-07-31', 75000,  'completed'),
    ('AI Integration',          1, '2024-06-01', NULL,         600000, 'active'),
    ('Summer Marketing Push',   4, '2024-06-01', '2024-08-31', 180000, 'completed')
ON CONFLICT DO NOTHING;

-- Project assignments
INSERT INTO project_assignments (employee_id, project_id, role, assigned_date) VALUES
    (1,  1, 'Tech Lead',    '2024-01-15'),
    (2,  1, 'Developer',    '2024-01-15'),
    (4,  1, 'DevOps',       '2024-02-01'),
    (25, 1, 'QA',           '2024-02-01'),
    (1,  2, 'Developer',    '2024-03-01'),
    (21, 2, 'Developer',    '2024-03-01'),
    (3,  2, 'Manager',      '2024-03-01'),
    (5,  3, 'Lead',         '2024-02-01'),
    (6,  3, 'Coordinator',  '2024-02-01'),
    (7,  4, 'Director',     '2024-01-01'),
    (8,  4, 'Representative','2024-01-01'),
    (9,  4, 'Representative','2024-01-01'),
    (11, 5, 'Lead',         '2024-04-01'),
    (12, 5, 'Content',      '2024-04-01'),
    (23, 5, 'Designer',     '2024-04-15'),
    (14, 6, 'Lead',         '2024-01-01'),
    (15, 6, 'Analyst',      '2024-01-01'),
    (16, 7, 'Manager',      '2024-05-01'),
    (17, 7, 'Coordinator',  '2024-05-15'),
    (18, 8, 'Lead',         '2024-03-15'),
    (19, 8, 'Agent',        '2024-03-15'),
    (1,  9, 'Tech Lead',    '2024-06-01'),
    (2,  9, 'Developer',    '2024-06-15'),
    (4,  9, 'DevOps',       '2024-06-15'),
    (11, 10,'Lead',         '2024-06-01'),
    (13, 10,'SEO',          '2024-06-01');

-- Monthly sales data (2024)
INSERT INTO sales (employee_id, product, region, amount, quantity, sale_date) VALUES
    (7,  'Enterprise Plan', 'West',      45000, 3,  '2024-01-15'),
    (8,  'Pro Plan',        'East',      12000, 8,  '2024-01-20'),
    (9,  'Pro Plan',        'West',      10500, 7,  '2024-01-22'),
    (10, 'Starter Plan',    'Midwest',    4500, 15, '2024-01-25'),
    (22, 'Pro Plan',        'South',      9000, 6,  '2024-01-28'),
    (7,  'Enterprise Plan', 'West',      60000, 4,  '2024-02-10'),
    (8,  'Pro Plan',        'East',      15000, 10, '2024-02-14'),
    (9,  'Starter Plan',    'West',       6000, 20, '2024-02-18'),
    (10, 'Pro Plan',        'Midwest',   13500, 9,  '2024-02-22'),
    (22, 'Enterprise Plan', 'South',     30000, 2,  '2024-02-26'),
    (7,  'Enterprise Plan', 'West',      75000, 5,  '2024-03-05'),
    (8,  'Pro Plan',        'East',      18000, 12, '2024-03-10'),
    (9,  'Pro Plan',        'West',      16500, 11, '2024-03-15'),
    (10, 'Starter Plan',    'Midwest',    7500, 25, '2024-03-20'),
    (22, 'Pro Plan',        'South',     12000, 8,  '2024-03-25'),
    (7,  'Enterprise Plan', 'West',      52500, 3,  '2024-04-08'),
    (8,  'Starter Plan',    'East',       5400, 18, '2024-04-12'),
    (9,  'Pro Plan',        'West',      13500, 9,  '2024-04-16'),
    (10, 'Enterprise Plan', 'Midwest',   45000, 3,  '2024-04-20'),
    (22, 'Pro Plan',        'South',     10500, 7,  '2024-04-24'),
    (7,  'Enterprise Plan', 'West',      90000, 6,  '2024-05-03'),
    (8,  'Pro Plan',        'East',      21000, 14, '2024-05-08'),
    (9,  'Pro Plan',        'West',      19500, 13, '2024-05-13'),
    (10, 'Starter Plan',    'Midwest',    9000, 30, '2024-05-18'),
    (22, 'Enterprise Plan', 'South',     45000, 3,  '2024-05-23'),
    (7,  'Enterprise Plan', 'West',      67500, 4,  '2024-06-05'),
    (8,  'Pro Plan',        'East',      24000, 16, '2024-06-10'),
    (9,  'Starter Plan',    'West',       8400, 28, '2024-06-15'),
    (10, 'Pro Plan',        'Midwest',   16500, 11, '2024-06-20'),
    (22, 'Pro Plan',        'South',     15000, 10, '2024-06-25'),
    (7,  'Enterprise Plan', 'West',      82500, 5,  '2024-07-03'),
    (8,  'Pro Plan',        'East',      19500, 13, '2024-07-09'),
    (9,  'Pro Plan',        'West',      22500, 15, '2024-07-14'),
    (10, 'Enterprise Plan', 'Midwest',   60000, 4,  '2024-07-19'),
    (22, 'Starter Plan',    'South',      6000, 20, '2024-07-24'),
    (7,  'Enterprise Plan', 'West',      97500, 6,  '2024-08-02'),
    (8,  'Pro Plan',        'East',      27000, 18, '2024-08-07'),
    (9,  'Pro Plan',        'West',      25500, 17, '2024-08-12'),
    (10, 'Starter Plan',    'Midwest',   10500, 35, '2024-08-17'),
    (22, 'Enterprise Plan', 'South',     52500, 3,  '2024-08-22');
