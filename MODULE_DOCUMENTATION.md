# Module-wise Documentation (Phase 6)

This document describes each of the **10 modules** in the Smart Sales Analytics Dashboard project. It is written for college internship submission and aligns with the implemented Flask routes and frontend pages.

---

## Module 1: Login & Registration

### Purpose
Allow users to create accounts and authenticate into the system.

### Frontend Pages
- `backend/frontend/login.html`
- `backend/frontend/register.html`

### Backend Routes
- `POST /api/auth/register` (register new user)
- `POST /api/auth/login` (login and create session)
- `POST /api/auth/logout` (clear session)
- `GET /api/auth/me` (fetch current logged-in user)

### Key Concepts
- Passwords are stored as hashed values.
- Roles: `admin` and `user`.
- Admin registration/login requires a secret admin key.

---

## Module 2: Dashboard KPI Cards

### Purpose
Display KPI cards summarizing revenue, orders, and units for selectable time ranges.

### Frontend Pages
- `backend/frontend/dashboard.html`

### Backend Route
- `GET /api/dashboard/kpis?period=<7d|30d|90d|1y>`

### Output (JSON)
- `revenue`, `orders`, `revenue_change`, `orders_change`, `period`

### Notes
- Percentage changes compare current period with a prior period of the same duration.

---

## Module 3: Sales Trend Analysis

### Purpose
Visualize sales trend over time (revenue and order counts).

### Frontend Pages
- `backend/frontend/trends.html`
- `backend/frontend/sales-data.html` (as supporting UI)

### Backend Route
- `GET /api/dashboard/trend?period=<7d|30d|90d|1y>`

### Output (JSON)
- `labels[]` formatted as `DD Mon`
- `revenue[]` (sum of revenue per day)
- `orders[]` (count of sales per day)

---

## Module 4: Product Performance

### Purpose
Provide product-level analytics and management.

### Frontend Pages
- `backend/frontend/products.html`

### Backend Routes
- `GET /api/products/?period=&category=&metric=`
- `GET /api/products/<product_id>`
- `POST /api/products/` (add product)
- `PUT /api/products/<product_id>` (update product)
- `DELETE /api/products/<product_id>` (delete only if no sales)
- `GET /api/products/categories/summary?period=`
- `GET /api/products/underperforming?period=&threshold=`
- `GET /api/products/export` (CSV export)

### Output Highlights
- Revenue and units are aggregated from `sales` joined with `products`.

---

## Module 5: Customer Analytics

### Purpose
Track customers, compute KPIs, segment information, and enable customer management.

### Frontend Pages
- `backend/frontend/customers.html`

### Backend Routes
- `GET /api/customers/?period=&segment=&search=`
- `GET /api/customers/<customer_id>`
- `POST /api/customers/`
- `PUT /api/customers/<customer_id>`
- `DELETE /api/customers/<customer_id>`
- `GET /api/customers/kpis?period=`
- `GET /api/customers/segments`
- `GET /api/customers/top?limit=`
- `GET /api/customers/new-vs-returning`
- `GET /api/customers/export` (CSV export)

### Output Highlights
- KPI includes total customers, new customers, returning customers, average LTV, and segment counts.

---

## Module 6: Regional Sales

### Purpose
Show regional distribution of sales (revenue, orders, growth), plus regional visualizations.

### Frontend Pages
- `backend/frontend/regional.html`

### Backend Routes
- `GET /api/regional/?period=&metric=`
- `GET /api/regional/cities?period=&limit=` (implemented using `region` as a proxy)
- `GET /api/regional/trend?period=`
- `GET /api/regional/share?period=`
- `GET /api/regional/heatmap?period=`
- `GET /api/regional/export?period=`

### Output Highlights
- Heatmap uses a normalized intensity score.

---

## Module 7: Report Generation (PDF & Excel)

### Purpose
Generate downloadable analytics reports.

### Frontend Pages
- `backend/frontend/reports.html`

### Backend Routes
- `GET /api/reports/pdf?period=&title=&prepared_by=`
- `GET /api/reports/excel?period=`
- `GET /api/reports/csv?period=`
- `GET /api/reports/history` (static list)

### Report Contents (Excel)
- Sheet 1: KPI Summary
- Sheet 2: Top Products
- Sheet 3: Regional
- Sheet 4: Raw Sales Data

### Report Contents (PDF)
- Title + prepared-by + period
- KPI summary table
- Top products table
- Regional breakdown table

---

## Module 8: Authentication & Role Management

### Purpose
Enforce authenticated access patterns and differentiate admin vs user behavior.

### Backend Role Logic
- `require_role(*roles)` helper exists in `backend/routes/auth.py`.

### Backend Auth Utilities
- `session['user_id']`, `session['role']`, and session-based auth in `/api/auth/me`.

### Key Testing Focus
- Ensure protected routes are accessible/blocked as intended.

---

## Module 9: Sales Forecasting (Linear Regression)

### Purpose
Predict future sales revenue using a Linear Regression model trained on historical monthly revenue.

### Frontend Pages
- `backend/frontend/forecasting.html`

### Backend ML Implementation
- `GET /api/ai/forecast`

### Data/Model Notes
- Monthly totals are calculated from the `sales` table grouped by year and month.
- Model: `sklearn.linear_model.LinearRegression`
- Forecast horizon: 6 future months.
- Response includes `historical`, `forecast`, and `r_squared`.

---

## Module 10: Customer Segmentation (K-Means)

### Purpose
Cluster customers into segments using K-Means clustering based on customer spending and purchase behavior.

### Frontend Pages
- `backend/frontend/segmentation.html`

### Backend ML Implementation
- `GET /api/ai/segment`

### Data/Model Notes
- Feature dataset derived from customer table fields: `total_spend`, `total_orders`, `avg_spend`, `ltv`.
- Model: `sklearn.cluster.KMeans`
- Clusters: `k = min(3, number_of_customers)`
- Clusters remapped by average spend into:
  - One-Time (low)
  - Regular (mid)
  - Champions (high)

---

## End of Module Documentation

