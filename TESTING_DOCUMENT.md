# Phase 6 — Testing & Documentation (Smart Sales Analytics Dashboard)

## 1. Test Document Overview
This document covers testing for the **Smart Sales Analytics Dashboard** project (Flask + MySQL + Scikit-learn). It includes:
- Module-wise test cases for all **10 modules**
- Integration test scenarios
- System test scenarios
- User Acceptance Testing (UAT) scenarios
- Bug report template

> **How to use:** For each Test Case, fill **Actual Result** and **Status (Pass/Fail)** after executing the steps.

---

## 2. Test Strategy
### 2.1 Scope
- Backend API endpoints under `/api/*`
- Frontend page behavior for dashboard pages and AI modules
- Database interactions (CRUD, aggregates)
- Reporting outputs (PDF/Excel/CSV)
- AI/ML endpoints: forecasting (Linear Regression) and segmentation (K-Means)

### 2.2 Out of Scope (for this phase)
- Full security hardening review (beyond role/authorization behavior testing)
- Performance benchmarking with load tools

### 2.3 Environments
- Local dev environment: `Flask` running on `http://127.0.0.1:5000`
- MySQL database: `salesiq` (schema created via app startup)

---

## 3. Module-wise Test Cases (10 Modules)

### Legend
- **Actual Result**: what you observed
- **Status**: Pass / Fail

> Note: IDs are unique and follow `TC-<Module#>-<n>` format.

---

## Module 1: Login & Registration

| Test Case ID | Module Name | Test Scenario | Test Steps | Expected Result | Actual Result | Status (Pass/Fail) |
|---|---|---|---|---|---|---|
| TC-1-1 | Login & Registration | Register as user with valid data | 1) Call POST `/api/auth/register` with valid `first_name,last_name,email,password,role='user'` (and no/empty admin_key). 2) Observe response. | HTTP 201 with message `Account created successfully`. |  |  |
| TC-1-2 | Login & Registration | Register as admin with valid admin key | 1) POST `/api/auth/register` with role=`admin` and `admin_key='ADMIN-SECRET-KEY'`. 2) Observe response. | HTTP 201 success. |  |  |
| TC-1-3 | Login & Registration | Register with missing required fields | 1) POST `/api/auth/register` with empty `email` or `password`. | HTTP 400 `All fields are required`. |  |  |
| TC-1-4 | Login & Registration | Register with invalid role | 1) POST `/api/auth/register` with role=`manager`. | HTTP 400 `Invalid role`. |  |  |
| TC-1-5 | Login & Registration | Register admin with invalid admin key | 1) POST `/api/auth/register` with role=`admin` but wrong `admin_key`. | HTTP 403 `Invalid admin secret key`. |  |  |
| TC-1-6 | Login & Registration | Register duplicate email | 1) Register once with an email. 2) Register again using same email. | HTTP 409 `Email already registered`. |  |  |
| TC-1-7 | Login & Registration | Login with correct credentials (user) | 1) POST `/api/auth/login` with correct email/password and role='user'. | HTTP 200 `Login successful` and session fields set. |  |  |
| TC-1-8 | Login & Registration | Login with wrong password | 1) POST `/api/auth/login` with correct email but wrong password. | HTTP 401 `Invalid email or password`. |  |  |
| TC-1-9 | Login & Registration | Login with wrong role | 1) Login using email of a user but set role='admin' in request. | HTTP 401 `This account is not registered as admin`. |  |  |
| TC-1-10 | Login & Registration | Login admin without correct admin key | 1) POST `/api/auth/login` with admin account and role='admin' but wrong `admin_key`. | HTTP 401 `Invalid admin secret key`. |  |  |
| TC-1-11 | Login & Registration | Login missing email/password | 1) POST `/api/auth/login` without email or password. | HTTP 400 `Email and password are required`. |  |  |
| TC-1-12 | Login & Registration | Get current user when not authenticated | 1) GET `/api/auth/me` without session. | HTTP 401 `Not authenticated`. |  |  |
| TC-1-13 | Login & Registration | Get current user when authenticated | 1) Login successfully. 2) GET `/api/auth/me`. | HTTP 200 with user fields including role/email/name. |  |  |
| TC-1-14 | Login & Registration | Logout clears session | 1) Login. 2) POST `/api/auth/logout`. 3) GET `/api/auth/me`. | Logout returns 200 and subsequent `/me` returns 401. |  |  |

---

## Module 2: Dashboard KPI Cards

| Test Case ID | Module Name | Test Scenario | Test Steps | Expected Result | Actual Result | Status (Pass/Fail) |
|---|---|---|---|---|---|---|
| TC-2-1 | Dashboard KPI Cards | KPI for default period | 1) GET `/api/dashboard/kpis` without query params. | HTTP 200; JSON contains revenue/orders and changes. |  |  |
| TC-2-2 | Dashboard KPI Cards | KPI for supported period '7d' | 1) GET `/api/dashboard/kpis?period=7d`. | HTTP 200 with valid numbers (no crash). |  |  |
| TC-2-3 | Dashboard KPI Cards | KPI for unsupported period value | 1) GET `/api/dashboard/kpis?period=xyz`. | System uses else branch; returns valid KPI JSON. |  |  |
| TC-2-4 | Dashboard KPI Cards | KPI when no sales exist | 1) Clear sales data (or query empty range). 2) GET for period with no records. | Revenue/orders/units = 0 and changes = 0. |  |  |
| TC-2-5 | Dashboard KPI Cards | Percentage change calculation | 1) Seed sales for current and prior ranges with known sums. 2) Compare `revenue_change` and `orders_change`. | Changes computed correctly and rounded (1 decimal). |  |  |

---

## Module 3: Sales Trend Analysis

| Test Case ID | Module Name | Test Scenario | Test Steps | Expected Result | Actual Result | Status (Pass/Fail) |
|---|---|---|---|---|---|---|
| TC-3-1 | Sales Trend Analysis | Trend labels and lengths | 1) GET `/api/dashboard/trend?period=30d`. | HTTP 200; response contains `labels`,`revenue`,`orders` arrays of same length. |  |  |
| TC-3-2 | Sales Trend Analysis | Trend with empty dataset | 1) Ensure no sales within range. 2) GET `/api/dashboard/trend`. | HTTP 200 with empty arrays (or arrays of zero length). |  |  |
| TC-3-3 | Sales Trend Analysis | Date formatting | 1) Seed sales with known dates. 2) GET trend. | Labels follow format `'%d %b'` (e.g., `05 Jun`). |  |  |
| TC-3-4 | Sales Trend Analysis | Revenue sums per day | 1) Seed multiple sales same date. 2) GET trend. | For each date, revenue equals sum of revenue. |  |  |

---

## Module 4: Product Performance

| Test Case ID | Module Name | Test Scenario | Test Steps | Expected Result | Actual Result | Status (Pass/Fail) |
|---|---|---|---|---|---|---|
| TC-4-1 | Product Performance | Get products for default period | 1) GET `/api/products/`. | HTTP 200; list of products with revenue/units (may be 0). |  |  |
| TC-4-2 | Product Performance | Filter by category | 1) GET `/api/products/?category=<existing-category>`. | Returned items only from that category. |  |  |
| TC-4-3 | Product Performance | Sort by revenue (default) | 1) Seed multiple products with different revenues. 2) GET `/api/products/`. | List sorted by total revenue desc. |  |  |
| TC-4-4 | Product Performance | Sort by units | 1) GET `/api/products/?metric=units`. | Sorted by total units desc. |  |  |
| TC-4-5 | Product Performance | Add product successfully | 1) POST `/api/products/` with name/category/price/stock. | HTTP 201 success. Product exists in DB. |  |  |
| TC-4-6 | Product Performance | Add product with missing fields | 1) POST with empty `price`. | HTTP 400 `All fields are required`. |  |  |
| TC-4-7 | Product Performance | Add duplicate product (same name+category) | 1) Add once. 2) Add again same values. | HTTP 409 `Product already exists`. |  |  |
| TC-4-8 | Product Performance | Update product | 1) PUT `/api/products/<id>` with new price/stock. | HTTP 200 and updated values persisted. |  |  |
| TC-4-9 | Product Performance | Delete product without sales | 1) Ensure product has 0 sales. 2) DELETE `/api/products/<id>`. | HTTP 200 deleted successfully. |  |  |
| TC-4-10 | Product Performance | Delete product with sales | 1) Ensure product has at least 1 sale. 2) DELETE. | HTTP 400 `Cannot delete — product has ... sales records`. |  |  |
| TC-4-11 | Product Performance | Category summary generation | 1) GET `/api/products/categories/summary?period=quarter`. | HTTP 200 with category list and metrics. |  |  |
| TC-4-12 | Product Performance | Underperforming threshold | 1) GET `/api/products/underperforming?threshold=2000`. | Returns products where total_revenue<threshold. |  |  |
| TC-4-13 | Product Performance | Export products CSV | 1) GET `/api/products/export`. | HTTP 200 with CSV download headers. |  |  |

---

## Module 5: Customer Analytics

| Test Case ID | Module Name | Test Scenario | Test Steps | Expected Result | Actual Result | Status (Pass/Fail) |
|---|---|---|---|---|---|---|
| TC-5-1 | Customer Analytics | Get customers default | 1) GET `/api/customers/`. | HTTP 200 with customer list containing required fields. |  |  |
| TC-5-2 | Customer Analytics | Search customers by name/email | 1) GET `/api/customers/?search=<term>`. | Only customers matching term returned. |  |  |
| TC-5-3 | Customer Analytics | Filter customers by segment | 1) GET `/api/customers/?segment=Champions`. | Only customers with segment Champions returned. |  |  |
| TC-5-4 | Customer Analytics | Add customer success | 1) POST `/api/customers/` with name/email/region. | HTTP 201 success; record created. |  |  |
| TC-5-5 | Customer Analytics | Add customer duplicate email | 1) POST with existing email. | HTTP 409 `Email already exists`. |  |  |
| TC-5-6 | Customer Analytics | Update customer fields | 1) PUT `/api/customers/<id>` change region/segment. | HTTP 200; changes persisted. |  |  |
| TC-5-7 | Customer Analytics | Delete customer | 1) DELETE `/api/customers/<id>`. | HTTP 200; customer removed. |  |  |
| TC-5-8 | Customer Analytics | Customer KPI values | 1) GET `/api/customers/kpis`. | HTTP 200; contains total/new/returning/avg_ltv and segment counts. |  |  |
| TC-5-9 | Customer Analytics | Segment summary output | 1) GET `/api/customers/segments`. | HTTP 200; each segment includes count/avg_spend/avg_orders/avg_ltv. |  |  |
| TC-5-10 | Customer Analytics | Top customers limit | 1) GET `/api/customers/top?limit=5`. | Exactly 5 entries (or less if dataset smaller). |  |  |
| TC-5-11 | Customer Analytics | New vs returning counts | 1) Seed customers with total_orders <=1 and >1. 2) GET `/api/customers/new-vs-returning`. | JSON correct for new/returning. |  |  |
| TC-5-12 | Customer Analytics | Export customers CSV | 1) GET `/api/customers/export`. | HTTP 200 with CSV download headers. |  |  |

---

## Module 6: Regional Sales

| Test Case ID | Module Name | Test Scenario | Test Steps | Expected Result | Actual Result | Status (Pass/Fail) |
|---|---|---|---|---|---|---|
| TC-6-1 | Regional Sales | Get regions for default period | 1) GET `/api/regional/?period=quarter`. | HTTP 200; list of regions with revenue/orders/growth. |  |  |
| TC-6-2 | Regional Sales | Sort by revenue (default) | 1) Seed multiple regions. 2) Call endpoint without metric param. | Output sorted by revenue desc. |  |  |
| TC-6-3 | Regional Sales | Sort by orders | 1) GET `/api/regional/?metric=orders`. | Sorted by orders desc. |  |  |
| TC-6-4 | Regional Sales | Sort by growth | 1) GET `/api/regional/?metric=growth`. | Sorted by growth desc. |  |  |
| TC-6-5 | Regional Sales | Revenue share percentages | 1) GET `/api/regional/share`. | Returns pct values; sums approx 100 when data exists. |  |  |
| TC-6-6 | Regional Sales | Heatmap intensity scaling | 1) GET `/api/regional/heatmap`. | intensity values between 0..1 range (rounded). |  |  |
| TC-6-7 | Regional Sales | Heatmap when all revenues are 0 | 1) Seed zero revenues. 2) GET heatmap. | intensity does not crash; uses max_rev default=1. |  |  |
| TC-6-8 | Regional Sales | Regional trend dataset structure | 1) GET `/api/regional/trend`. | Response includes labels and datasets; datasets have arrays length = labels length. |  |  |
| TC-6-9 | Regional Sales | Export regional CSV | 1) GET `/api/regional/export`. | HTTP 200 with CSV download headers. |  |  |

---

## Module 7: Report Generation (PDF & Excel)

| Test Case ID | Module Name | Test Scenario | Test Steps | Expected Result | Actual Result | Status (Pass/Fail) |
|---|---|---|---|---|---|---|
| TC-7-1 | Report Generation (PDF & Excel) | Generate PDF default period | 1) GET `/api/reports/pdf`. | HTTP 200; Content-Type application/pdf; file downloadable. |  |  |
| TC-7-2 | Report Generation (PDF & Excel) | Generate PDF with period=year | 1) GET `/api/reports/pdf?period=year`. | HTTP 200; PDF includes period header. |  |  |
| TC-7-3 | Report Generation (PDF & Excel) | PDF handles empty summary | 1) Ensure no sales in date range. 2) GET `/api/reports/pdf`. | PDF generated with zeros; no exceptions. |  |  |
| TC-7-4 | Report Generation (PDF & Excel) | Generate Excel default | 1) GET `/api/reports/excel`. | HTTP 200; Content-Type xlsx; workbook with sheets present. |  |  |
| TC-7-5 | Report Generation (PDF & Excel) | Excel includes KPI/Top/Regional/Raw sheets | 1) Generate excel. 2) Open file and verify sheet names. | Sheets: KPI Summary, Top Products, Regional, Raw Sales Data. |  |  |
| TC-7-6 | Report Generation (PDF & Excel) | Excel handles empty dataset | 1) No sales in range. 2) GET `/api/reports/excel`. | Workbook still downloads; cells show 0/default. |  |  |
| TC-7-7 | Report Generation (PDF & Excel) | Generate CSV report | 1) GET `/api/reports/csv`. | HTTP 200; CSV content returned with correct headers. |  |  |
| TC-7-8 | Report Generation (PDF & Excel) | Report history endpoint | 1) GET `/api/reports/history`. | HTTP 200; returns static list of report entries. |  |  |

---

## Module 8: Authentication & Role Management

| Test Case ID | Module Name | Test Scenario | Test Steps | Expected Result | Actual Result | Status (Pass/Fail) |
|---|---|---|---|---|---|---|
| TC-8-1 | Authentication & Role Management | `/api/auth/me` requires session | 1) Without login, GET `/api/auth/me`. | HTTP 401 Not authenticated. |  |  |
| TC-8-2 | Authentication & Role Management | Admin login requires admin_key | 1) Login with admin role wrong key. | HTTP 401 invalid admin secret key. |  |  |
| TC-8-3 | Authentication & Role Management | Role mismatch rejected on login | 1) Use user account but send role=admin. | HTTP 401 role mismatch error. |  |  |
| TC-8-4 | Authentication & Role Management | Protected route behavior (require_role usage) | 1) Identify endpoints that call `require_role` (if any). 2) Test access with user and admin sessions. | Admin-only endpoints allow admin; others return 403. |  |  |
| TC-8-5 | Authentication & Role Management | Unauthorized access to data APIs | 1) Call data endpoints without login. | Expected: either 401/403 or documented public access. Record actual behavior. |  |  |

> This module is especially important because not all route files currently enforce `require_role`. Capture findings in Actual Result.

---

## Module 9: Sales Forecasting (Linear Regression)

| Test Case ID | Module Name | Test Scenario | Test Steps | Expected Result | Actual Result | Status (Pass/Fail) |
|---|---|---|---|---|---|---|
| TC-9-1 | Sales Forecasting (Linear Regression) | Forecast API returns valid structure | 1) Seed enough monthly sales data. 2) GET `/api/ai/forecast`. | HTTP 200; JSON contains `historical`, `forecast`, `r_squared`. |  |  |
| TC-9-2 | Sales Forecasting (Linear Regression) | Forecast not executed with insufficient data | 1) Ensure fewer than 2 monthly revenue groups in DB. 2) GET `/api/ai/forecast`. | HTTP 400 with error `Not enough sales data to forecast.` |  |  |
| TC-9-3 | Sales Forecasting (Linear Regression) | Historical length matches query groups | 1) Seed N distinct months. 2) GET forecast. | `historical.length == N`. |  |  |
| TC-9-4 | Sales Forecasting (Linear Regression) | Forecast length is 6 months | 1) With adequate data. 2) GET forecast. | `forecast.length == 6`. |  |  |
| TC-9-5 | Sales Forecasting (Linear Regression) | Forecast values are non-negative | 1) Seed data with possible low values. 2) GET forecast. | Each forecast `value >= 0` due to max(.,0). |  |  |
| TC-9-6 | Sales Forecasting (Linear Regression) | UI loads and renders chart | 1) Open `backend/frontend/forecasting.html` served by Flask. 2) Verify chart & table render after API call. | Forecast chart and table display without console errors. |  |  |

---

## Module 10: Customer Segmentation (K-Means)

| Test Case ID | Module Name | Test Scenario | Test Steps | Expected Result | Actual Result | Status (Pass/Fail) |
|---|---|---|---|---|---|---|
| TC-10-1 | Customer Segmentation (K-Means) | Segmentation API returns valid JSON | 1) Seed at least 3 customers with `total_spend > 0`. 2) GET `/api/ai/segment`. | HTTP 200; JSON contains `customers`, `summary`, `centers`, `k`. |  |  |
| TC-10-2 | Customer Segmentation (K-Means) | Not enough data handling | 1) Seed fewer than 3 customers with `total_spend > 0`. 2) GET `/api/ai/segment`. | HTTP 400 with error `Not enough customer data to segment.` |  |  |
| TC-10-3 | Customer Segmentation (K-Means) | Cluster count respects dataset size | 1) Seed exactly 3 customers. 2) GET `/api/ai/segment`. | `k == min(3, len(rows))` and `summary` keys match segments. |  |  |
| TC-10-4 | Customer Segmentation (K-Means) | Segment assignment matches cluster ordering | 1) Seed customers with distinct spend tiers. 2) Run segmentation. | Higher spend cluster maps to `Champions`, middle to `Regular`, low to `One-Time` (as per sort by avg spend). |  |  |
| TC-10-5 | Customer Segmentation (K-Means) | UI renders segmentation results | 1) Open `backend/frontend/segmentation.html`. 2) Verify results table/cards after API call. | Segmentation visualization renders without errors. |  |  |

---

## 4. Integration Testing Scenarios

| IT Case ID | Scenario | Modules/Components | Test Steps | Expected Result |
|---|---|---|---|---|
| IT-1 | Auth + Dashboard access | Auth + Dashboard KPIs | 1) Register/login. 2) Call `/api/dashboard/kpis` and render dashboard page. | KPI API responds with correct JSON; page updates. |
| IT-2 | Sales CRUD -> Dashboard KPIs | Sales + Dashboard | 1) Add product + add sales via `/api/sales/`. 2) Call `/api/dashboard/kpis` for matching period. | KPI revenue/orders/units reflect newly inserted sales. |
| IT-3 | Sales import -> Product performance | Sales bulk import + Products | 1) Upload CSV/Excel via `/api/sales/bulk-import`. 2) Call `/api/products/?period=...` and `/api/products/categories/summary`. | Imported sales affect product aggregation metrics. |
| IT-4 | Reports depend on Sales data | Reports + Sales | 1) Insert sales data. 2) Generate `/api/reports/pdf` and `/api/reports/excel`. | Files download successfully and include correct totals. |
| IT-5 | Regional endpoints depend on Sales | Sales + Regional | 1) Seed sales across regions. 2) Call `/api/regional/`, `/api/regional/trend`, `/api/regional/share`. | All endpoints return consistent numbers based on sales. |
| IT-6 | Customers endpoints depend on customer table | Customers + AI Segmentation | 1) Seed customers with spend & orders fields. 2) Run `/api/ai/segment`. 3) Open customers segment view. | Segmentation output aligns with customers dataset. |
| IT-7 | Forecasting depends on sales revenue by month | Sales + AI Forecast | 1) Insert sales across at least 2 months. 2) Call `/api/ai/forecast`. 3) Validate forecast length and R² present. | Forecast returns historical + 6 month forecast. |
| IT-8 | Export endpoints generate valid files | Sales/Products/Customers/Regional + Export | 1) Call export endpoints for each module. | CSV downloads are produced and contain expected columns. |

---

## 5. System Testing Scenarios

| ST Case ID | Scenario | Test Steps | Expected Result |
|---|---|---|---|
| ST-1 | End-to-end user flow | 1) Register/Login. 2) Navigate to dashboard pages. 3) Verify charts/tables render. | UI pages render without JS errors; data displayed. |
| ST-2 | Reports generation during active session | 1) Login (optional). 2) Generate PDF/Excel/CSV for different periods. | Downloads succeed for all formats and periods. |
| ST-3 | AI modules full run | 1) Open forecasting.html and segmentation.html. 2) Verify charts and tables populate after API fetch. | AI results appear; no broken UI elements. |
| ST-4 | Date range edge cases | 1) Test period values close to present date. 2) Verify no server errors. | Returns valid responses; empty datasets handled gracefully. |
| ST-5 | Invalid input robustness | 1) Send invalid numeric values to sales/customer/product update endpoints. 2) Observe responses. | API returns error or fails gracefully (no crash). |

---

## 6. User Acceptance Testing (UAT) Scenarios

| UAT Case ID | Scenario | Test Steps | Expected Result |
|---|---|---|---|
| UAT-1 | User can create account and login | 1) Register as user. 2) Login. 3) Confirm `/me` works. | Users can access dashboard after login. |
| UAT-2 | Admin can register admin account | 1) Register admin using correct key. | Admin account created successfully. |
| UAT-3 | Dashboard accuracy | 1) Add known sales records. 2) Verify KPIs and trends match expectations. | Dashboard numbers match inserted data. |
| UAT-4 | Products & Customers usability | 1) Add/update/delete products/customers. | Changes reflect in analytics pages immediately after refresh. |
| UAT-5 | Reports usefulness | 1) Generate PDF and Excel for a period. 2) Validate key sections exist (KPIs, top products, raw data). | Reports are complete and readable. |
| UAT-6 | Forecast/Segmentation credibility | 1) Run AI modules on seeded dataset. 2) Verify outputs are consistent and interpretable. | Forecast shows 6 month projection; segmentation creates meaningful clusters. |

---

## 7. Bug Report Template

Copy/paste this template for any issue found.

### Bug Report
- **Bug ID**: 
- **Title**: 
- **Module**: (e.g., Sales API, Dashboard KPI, Forecasting, Reports)
- **Severity**: (Critical / High / Medium / Low)
- **Priority**: (P0 / P1 / P2 / P3)
- **Environment**: (OS, Browser, Flask mode, DB status)
- **Preconditions**: (seed data, logged-in status, role)
- **Steps to Reproduce**:
  1. 
  2. 
  3. 
- **Expected Result**: 
- **Actual Result**: 
- **Reproducibility**: (Always / Often / Sometimes / Rare)
- **Screenshots/Logs**: 
- **Workaround (if any)**: 
- **Notes**: 

---

## 8. Testing Results Summary (Fill after execution)
- Total Test Cases Planned: ___
- Total Passed: ___
- Total Failed: ___
- Major Bugs Identified: ___ (list Bug IDs)

### Notes
- Attach screenshots/evidence per failed test cases.
- Record failures in the **Actual Result** column.

