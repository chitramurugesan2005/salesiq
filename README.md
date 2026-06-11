## Updated README.md

Here is the complete README for the project. Create or replace the existing `README.md` in the root folder:

```markdown
# SalesIQ — Sales Analytics Dashboard
> A full-stack sales analytics platform built with Flask, MySQL and HTML/CSS/JS

---

## 👥 Team & Phases

| Phase | Description | Status |
|-------|-------------|--------|
| Phase 1 | Frontend UI Design | ✅ Done |
| Phase 2 | Backend & Database | ✅ Done |
| Phase 3 | Frontend & Backend Integration | ✅ Done |
| Phase 4 | Authentication & Role Management | ✅ Done |
| Phase 5 | AI & ML Integration | ⏳ Pending |
| Phase 6 | Testing & Documentation | ⏳ Pending |
| Phase 7 | Submission & Presentation | ⏳ Pending |

---

## 🗂️ Project Structure

```
salesiq/
├── frontend/
│   ├── auth.css
│   ├── auth-guard.js
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── sales-data.html
│   ├── trends.html
│   ├── products.html
│   ├── customers.html
│   ├── regional.html
│   ├── forecasting.html
│   ├── segmentation.html
│   └── reports.html
├── backend/
│   ├── app.py
│   ├── config.py
│   ├── models.py
│   ├── requirements.txt
│   └── routes/
│       ├── __init__.py
│       ├── auth.py
│       ├── sales.py
│       ├── dashboard.py
│       ├── products.py
│       ├── customers.py
│       ├── regional.py
│       └── reports.py
└── database/
    └── salesiq.sql
```

---

## ⚙️ Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | HTML, CSS, JavaScript, Chart.js |
| Backend | Python, Flask, Flask-SQLAlchemy |
| Database | MySQL |
| Auth | Werkzeug password hashing, Flask session |
| Reports | ReportLab (PDF), OpenPyXL (Excel) |
| AI/ML | Scikit-learn (pending) |

---

## 🚀 Setup Instructions

### Prerequisites
- Python 3.10
- MySQL (Workbench or XAMPP)
- pip

---

### Step 1 — Clone or Extract the Project
Extract the zip folder to your desired location.

---

### Step 2 — Install Python Packages
```bash
cd salesiq/backend
pip install -r requirements.txt
```

---

### Step 3 — Configure Database

Open `backend/config.py` and update with your MySQL password:

```python
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:YourPasswordHere@localhost/salesiq'
```

If you have no MySQL password:
```python
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:@localhost/salesiq'
```

---

### Step 4 — Create Database Tables

Run the Flask app once to auto-create all tables:
```bash
cd salesiq/backend
python app.py
```

You should see:
```
✅ Database tables created successfully
* Running on http://127.0.0.1:5000
```

---

### Step 5 — Load Sample Data

- Open MySQL Workbench
- Open a new query tab
- File → Open SQL Script → select `database/salesiq.sql`
- Click the lightning bolt to run it

---

### Step 6 — Generate Password Hashes

Open Python terminal:
```bash
python
```

Then run:
```python
from werkzeug.security import generate_password_hash
print(generate_password_hash('Admin@1234'))
print(generate_password_hash('User@1234'))
```

Copy the outputs and run this in MySQL Workbench:
```sql
USE salesiq;
UPDATE users SET password = 'PASTE_ADMIN_HASH_HERE'
WHERE email = 'admin@salesiq.com';
UPDATE users SET password = 'PASTE_USER_HASH_HERE'
WHERE email = 'user@salesiq.com';
```

---

### Step 7 — Run the Application

```bash
cd salesiq/backend
python app.py
```

Open `frontend/login.html` in your browser.

---

## 🔐 Demo Credentials

| Role | Email | Password | Extra |
|------|-------|----------|-------|
| Admin | admin@salesiq.com | Admin@1234 | Admin Key: ADMIN-SECRET-KEY |
| User | user@salesiq.com | User@1234 | — |

---

## 📡 API Routes

### Authentication
| Method | Route | Description |
|--------|-------|-------------|
| POST | /api/auth/register | Register new account |
| POST | /api/auth/login | Login |
| POST | /api/auth/logout | Logout |
| GET | /api/auth/me | Get current user |

### Sales
| Method | Route | Description |
|--------|-------|-------------|
| GET | /api/sales/ | Get all sales |
| POST | /api/sales/ | Add sale record |
| PUT | /api/sales/int:id | Update sale |
| DELETE | /api/sales/int:id | Delete sale |
| POST | /api/sales/bulk-delete | Delete multiple |
| POST | /api/sales/bulk-import | Import CSV/Excel |
| GET | /api/sales/export | Export CSV |

### Dashboard
| Method | Route | Description |
|--------|-------|-------------|
| GET | /api/dashboard/kpis | KPI summary |
| GET | /api/dashboard/trend | Revenue trend |
| GET | /api/dashboard/categories | Category breakdown |
| GET | /api/dashboard/top-products | Top 5 products |
| GET | /api/dashboard/activity | Recent activity |

### Products
| Method | Route | Description |
|--------|-------|-------------|
| GET | /api/products/ | All products |
| POST | /api/products/ | Add product |
| PUT | /api/products/int:id | Update product |
| DELETE | /api/products/int:id | Delete product |
| GET | /api/products/categories/summary | Category summary |
| GET | /api/products/underperforming | Low performers |
| GET | /api/products/export | Export CSV |

### Customers
| Method | Route | Description |
|--------|-------|-------------|
| GET | /api/customers/ | All customers |
| POST | /api/customers/ | Add customer |
| PUT | /api/customers/int:id | Update customer |
| DELETE | /api/customers/int:id | Delete customer |
| GET | /api/customers/kpis | Customer KPIs |
| GET | /api/customers/segments | Segment breakdown |
| GET | /api/customers/top | Top customers |
| GET | /api/customers/export | Export CSV |

### Regional
| Method | Route | Description |
|--------|-------|-------------|
| GET | /api/regional/ | All regions |
| GET | /api/regional/cities | Top cities |
| GET | /api/regional/trend | Region trend |
| GET | /api/regional/share | Revenue share |
| GET | /api/regional/heatmap | Heatmap data |
| GET | /api/regional/export | Export CSV |

### Reports
| Method | Route | Description |
|--------|-------|-------------|
| GET | /api/reports/pdf | Download PDF |
| GET | /api/reports/excel | Download Excel |
| GET | /api/reports/csv | Download CSV |
| GET | /api/reports/history | Report history |

---

## ⚠️ Important Notes for Team Members

- Always use `python` not `py` to run the app
- Update `config.py` with your own MySQL password
- Never commit your password to the zip file
- Always run `python app.py` before opening any HTML page
- Flask must be running on port 5000 for the frontend to work

---

## 🐛 Common Errors & Fixes

| Error | Fix |
|-------|-----|
| No module named flask | Run `pip install flask` |
| Access denied for root | Update password in config.py |
| Table doesn't exist | Run `python app.py` to create tables |
| PDF/Excel corrupted | Use blob fetch in frontend |
| py not found | Use `python` instead of `py` |

---

## 📌 Current Known Issues

- Phase 5 AI/ML endpoints not yet connected
- Forecasting and Segmentation pages use static demo data

---

*SalesIQ — Team Project · 2026*
```
