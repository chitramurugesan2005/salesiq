# Smart Sales Analytics Dashboard — Final Project Report (Phase 6)

## 1. Introduction
The **Smart Sales Analytics Dashboard** is a full-stack application that helps small-to-medium businesses analyze sales performance, understand customer and regional trends, and generate reports for decision-making. The system also integrates machine learning features for:
- **Sales forecasting** using **Linear Regression**
- **Customer segmentation** using **K-Means clustering**

The application provides a unified dashboard experience by combining a Flask backend, a MySQL database, interactive frontend pages, and AI/ML modules.

---

## 2. Objectives
- Enable users to manage sales, products, and customers through web interfaces.
- Provide KPI dashboards for revenue/orders/units and sales trends.
- Support regional analysis including growth, revenue share, and heatmap-style intensity.
- Generate downloadable reports in **PDF**, **Excel**, and **CSV** formats.
- Implement forecasting and segmentation using Scikit-learn.
- Ensure the system is testable and documented for internship/project submission.

---

## 3. System Architecture
### 3.1 High-level Architecture
- **Frontend (HTML/CSS/JavaScript)**
  - Renders dashboard pages, charts, tables, and report links.
  - Communicates with backend via HTTP requests.

- **Backend (Flask)**
  - Exposes REST-like API endpoints under `/api/*`.
  - Handles database operations using SQLAlchemy.
  - Generates reports using ReportLab (PDF) and OpenPyXL (Excel).
  - Hosts AI/ML endpoints for forecasting and segmentation.

- **Database (MySQL)**
  - Stores users, products, sales records, customers, and regions.

- **Machine Learning (Scikit-learn)**
  - Linear Regression for forecasting monthly revenue.
  - K-Means for clustering customers into segments.

### 3.2 Data Flow (Summary)
1. User interactions on frontend trigger API calls.
2. Backend validates inputs and queries the database.
3. Backend returns JSON responses to update UI.
4. For reports, backend generates files and returns them as downloads.
5. For AI modules, backend calculates features from DB tables and produces predictions/clusters.

---

## 4. Modules Description
This project is structured into ten functional modules:

### Module 1: Login & Registration
- User account creation with hashed passwords.
- Admin registration protected using a secret admin key.
- Session-based authentication.

### Module 2: Dashboard KPI Cards
- Summarizes revenue, orders, and units for a selected time period.
- Includes percentage changes vs prior period.

### Module 3: Sales Trend Analysis
- Shows revenue and order counts over time.
- Uses daily aggregation from sales records.

### Module 4: Product Performance
- Product-level revenue and units aggregation.
- Category summaries and underperforming product identification.
- Product CRUD management and CSV export.

### Module 5: Customer Analytics
- Customer list, KPIs, segment breakdown, and top customers.
- Customer CRUD management and export.

### Module 6: Regional Sales
- Regional summaries with growth vs prior periods.
- Regional trend, revenue share, and heatmap intensity.

### Module 7: Report Generation (PDF & Excel)
- Produces downloadable reports for a selected period.
- PDF includes KPI summary, top products, and regional breakdown.
- Excel includes multiple sheets including raw sales data.

### Module 8: Authentication & Role Management
- Session management with role tracking (`admin`/`user`).
- Role checking helper available for protected endpoints.

### Module 9: Sales Forecasting (Linear Regression)
- Trains Linear Regression on monthly revenue data.
- Produces a 6-month future forecast.
- Returns historical series and forecast metrics.

### Module 10: Customer Segmentation (K-Means)
- Builds feature vectors from customer metrics.
- Uses K-Means to cluster customers into 3 segments.
- Outputs customer-to-cluster mapping and summary statistics.

---

## 5. Database Design
### 5.1 Entities
- **users**: stores account information and roles
- **products**: product metadata including category and price
- **sales**: transactional sales data linked to products
- **customers**: customer data and computed marketing attributes
- **regions**: regional attributes (revenue/orders/growth)

### 5.2 Key Relationships
- `sales.product_id` references `products.id`
- `sales` contain revenue and units; analytics queries join `sales` with `products`.

### 5.3 Constraints
- Unique email for users and customers.
- Enum constraints for roles and sales status.

> Include ER diagram screenshot in final submission if available.

---

## 6. AI/ML Implementation
### 6.1 Sales Forecasting (Linear Regression)
- **Input data**: monthly revenue grouped by year/month from `sales`
- **Model**: `sklearn.linear_model.LinearRegression`
- **Training**: sequence index as the independent variable and monthly revenue as target
- **Output**:
  - `historical`: monthly totals
  - `forecast`: 6 future months
  - `r_squared`: goodness-of-fit score

### 6.2 Customer Segmentation (K-Means)
- **Input data**: customer features from `customers` table (total_spend, total_orders, avg_spend, ltv)
- **Model**: `sklearn.cluster.KMeans`
- **Preprocessing**: `StandardScaler`
- **Clustering strategy**:
  - number of clusters: `k = min(3, number_of_customers)`
  - clusters remapped by average spend to assign:
    - low → One-Time
    - mid → Regular
    - high → Champions

---

## 7. Testing Results
### 7.1 Testing Approach
Testing was performed according to:
- Module-wise validation (API contract + expected JSON/file outputs)
- Integration tests (data flow across modules)
- System tests (end-to-end UI behavior)
- UAT scenarios (acceptance with realistic user goals)

### 7.2 Summary Table (Fill after execution)
- Total Test Cases Planned: ___
- Total Passed: ___
- Total Failed: ___

### 7.3 Failed Test Cases / Bugs
- Major Bugs Identified:
  - Bug IDs: ___
  - Evidence: screenshots/log links ___

> **Note:** Refer to `TESTING_DOCUMENT.md` to fill Actual Result and Pass/Fail for each test case.

---

## 8. Future Enhancements
- Add automated test suite using `pytest` for backend APIs.
- Add stronger authorization enforcement on all sensitive routes.
- Improve validation and error handling for numeric casting and file parsing.
- Enhance reporting with charts and better filtering.
- Improve ML forecasting with time-series models (e.g., ARIMA/Prophet) and confidence intervals.
- Add UI improvements for AI sections (scenario controls should map to real API retraining).

---

## 9. Conclusion
The Smart Sales Analytics Dashboard delivers a complete end-to-end analytics solution that supports sales tracking, KPI dashboards, reporting, and AI-based forecasting/segmentation. The Phase 6 work includes a full testing plan (module-wise, integration, system, and UAT) and professional documentation to support submission and evaluation.

---

## Appendix (Optional)
- Screenshots: login, dashboard, charts, report downloads, AI outputs.
- Database ER diagram.

