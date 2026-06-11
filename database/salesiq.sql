-- ── Create and use database ──
CREATE DATABASE IF NOT EXISTS salesiq;
USE salesiq;

-- ── Users ──
INSERT INTO users 
(first_name, last_name, email, password, role, created_at)
VALUES
('Admin', 'User', 'admin@salesiq.com',
'pbkdf2:sha256:260000$rq8YhCmJzN2kX3Lp$8a9b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b',
'admin', NOW()),
('John', 'Doe', 'user@salesiq.com',
'pbkdf2:sha256:260000$rq8YhCmJzN2kX3Lp$8a9b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b',
'user', NOW());

-- ── Products ──
INSERT INTO products (name, category, price, stock)
VALUES
('Wireless Earbuds Pro',   'Electronics',   89.00,  82),
('Linen Shirt Slate',      'Clothing',       49.00, 210),
('Smart LED Desk Lamp',    'Home & Living',  65.00,  18),
('Vitamin C Serum',        'Beauty',         29.00, 145),
('Running Shoes X3',       'Sports',        110.00,  68),
('Mechanical Keyboard',    'Electronics',   129.00,   0),
('Data Science Handbook',  'Books',          35.00, 200),
('Yoga Mat Pro',           'Sports',         45.00,  90),
('Smart Watch Series 4',   'Electronics',   199.00,   3),
('Moisturiser SPF50',      'Beauty',         22.00, 175),
('Denim Jacket',           'Clothing',       89.00,  50),
('Coffee Table Oak',       'Home & Living', 249.00,  12),
('Bluetooth Speaker',      'Electronics',    75.00,  60),
('Casual Sneakers',        'Clothing',       65.00,  80),
('Desk Organiser',         'Home & Living',  35.00,  40),
('Face Mask Pack',         'Beauty',         18.00, 200),
('Python Cookbook',        'Books',          40.00, 150),
('Gym Gloves',             'Sports',         28.00, 100),
('USB C Hub',              'Electronics',    55.00,  45),
('Linen Trousers',         'Clothing',       72.00,  35);

-- ── Sales ──
INSERT INTO sales
(product_id, units, revenue, region, status, notes, sale_date, created_at)
VALUES
(1,  42, 3738.00, 'North',   'Completed', '',               '2026-05-01', NOW()),
(2,  60, 2940.00, 'South',   'Completed', '',               '2026-05-02', NOW()),
(3,  18, 1170.00, 'East',    'Pending',   'Low stock',      '2026-05-03', NOW()),
(4,  95, 2755.00, 'West',    'Completed', '',               '2026-05-04', NOW()),
(5,  12, 1548.00, 'Central', 'Completed', '',               '2026-05-05', NOW()),
(6,  34, 3740.00, 'North',   'Completed', '',               '2026-05-06', NOW()),
(7,  78, 2730.00, 'South',   'Completed', '',               '2026-05-07', NOW()),
(8,  22, 4378.00, 'East',    'Refunded',  'Customer request','2026-05-08', NOW()),
(9,  55, 2475.00, 'West',    'Completed', '',               '2026-05-09', NOW()),
(10, 88, 1936.00, 'Central', 'Completed', '',               '2026-05-10', NOW()),
(11, 30, 2670.00, 'North',   'Pending',   '',               '2026-05-11', NOW()),
(12,  8, 1992.00, 'South',   'Completed', '',               '2026-05-12', NOW()),
(13, 25, 1875.00, 'East',    'Completed', '',               '2026-05-13', NOW()),
(14, 40, 2600.00, 'West',    'Completed', '',               '2026-05-13', NOW()),
(15, 15,  525.00, 'Central', 'Completed', '',               '2026-05-14', NOW()),
(16, 80, 1440.00, 'North',   'Completed', '',               '2026-05-14', NOW()),
(17, 60, 2400.00, 'South',   'Completed', '',               '2026-05-15', NOW()),
(18, 45, 1260.00, 'East',    'Completed', '',               '2026-05-15', NOW()),
(19, 32, 1760.00, 'West',    'Completed', '',               '2026-05-16', NOW()),
(20, 28, 2016.00, 'Central', 'Completed', '',               '2026-05-16', NOW()),
(1,  38, 3382.00, 'South',   'Completed', '',               '2026-04-01', NOW()),
(2,  55, 2695.00, 'North',   'Completed', '',               '2026-04-02', NOW()),
(3,  20, 1300.00, 'West',    'Completed', '',               '2026-04-03', NOW()),
(4,  80, 2320.00, 'Central', 'Completed', '',               '2026-04-04', NOW()),
(5,  15, 1650.00, 'East',    'Completed', '',               '2026-04-05', NOW()),
(6,  28, 3612.00, 'North',   'Completed', '',               '2026-04-06', NOW()),
(7,  65, 2275.00, 'South',   'Completed', '',               '2026-04-07', NOW()),
(8,  18, 3582.00, 'West',    'Completed', '',               '2026-04-08', NOW()),
(9,  48, 2160.00, 'Central', 'Completed', '',               '2026-04-09', NOW()),
(10, 75, 1650.00, 'East',    'Completed', '',               '2026-04-10', NOW()),
(1,  50, 4450.00, 'North',   'Completed', '',               '2026-03-01', NOW()),
(2,  70, 3430.00, 'South',   'Completed', '',               '2026-03-02', NOW()),
(3,  25, 1625.00, 'East',    'Completed', '',               '2026-03-03', NOW()),
(4, 100, 2900.00, 'West',    'Completed', '',               '2026-03-04', NOW()),
(5,  20, 2200.00, 'Central', 'Completed', '',               '2026-03-05', NOW()),
(6,  40, 5160.00, 'North',   'Completed', '',               '2026-03-06', NOW()),
(7,  90, 3150.00, 'South',   'Completed', '',               '2026-03-07', NOW()),
(8,  30, 5970.00, 'East',    'Completed', '',               '2026-03-08', NOW()),
(9,  60, 2700.00, 'West',    'Completed', '',               '2026-03-09', NOW()),
(10, 95, 2090.00, 'Central', 'Completed', '',               '2026-03-10', NOW());

-- ── Customers ──
INSERT INTO customers
(name, email, region, segment, total_orders,
total_spend, avg_spend, ltv, created_at)
VALUES
('Arjun Mehta',    'arjun.m@email.com',   'North',   'Champions', 24, 6240.00, 520.00, 4368.00, NOW()),
('Priya Sharma',   'priya.s@email.com',   'South',   'Champions', 21, 5880.00, 495.00, 3960.00, NOW()),
('Rahul Verma',    'rahul.v@email.com',   'East',    'Champions', 19, 5460.00, 478.00, 3346.00, NOW()),
('Sneha Nair',     'sneha.n@email.com',   'West',    'Champions', 17, 4990.00, 442.00, 2884.00, NOW()),
('Karthik Raja',   'karthik.r@email.com', 'Central', 'Champions', 15, 4320.00, 398.00, 2394.00, NOW()),
('Divya Krishnan', 'divya.k@email.com',   'North',   'Regular',    9, 2880.00, 210.00,  518.00, NOW()),
('Amar Singh',     'amar.s@email.com',    'South',   'Regular',    8, 2560.00, 195.00,  460.00, NOW()),
('Lakshmi Patel',  'lakshmi.p@email.com', 'East',    'Regular',    7, 2240.00, 182.00,  392.00, NOW()),
('Vijay Kumar',    'vijay.k@email.com',   'West',    'Regular',    6, 1920.00, 168.00,  320.00, NOW()),
('Riya Desai',     'riya.d@email.com',    'Central', 'One-Time',   1,  420.00,  62.00,   62.00, NOW()),
('Meera Iyer',     'meera.i@email.com',   'North',   'One-Time',   1,  380.00,  58.00,   58.00, NOW()),
('Suresh Pillai',  'suresh.p@email.com',  'South',   'One-Time',   1,  290.00,  45.00,   45.00, NOW());