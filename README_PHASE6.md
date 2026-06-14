# SalesIQ — Phase 6 (Testing & Documentation)

This README is prepared for **Phase 6: Testing & Documentation** of the *Smart Sales Analytics Dashboard* project.

---

## 1. What’s Included in Phase 6
- **Testing Document** with:
  - Module-wise test cases (10 modules)
  - Integration testing scenarios
  - System testing scenarios
  - UAT scenarios
  - Bug report template
- **Module-wise documentation** describing each module
- **Final Project Report** skeleton (with testing results placeholders)

Files:
- `TESTING_DOCUMENT.md`
- `MODULE_DOCUMENTATION.md`
- `FINAL_PROJECT_REPORT.md`

---

## 2. How to Run the Project (Local)
1. Start the Flask backend:
   - `cd backend`
   - `python app.py`
2. Open the web pages via the Flask server:
   - Backend serves static frontend files under `backend/frontend/`.
3. Ensure MySQL is reachable and tables exist (the app creates tables on startup).

---

## 3. How to Execute Testing (Practical)
### 3.1 Backend API Testing
Use one of the following:
- Browser network tab (for pages)
- Postman / Insomnia (for API requests)

Follow `TESTING_DOCUMENT.md` test cases and fill:
- **Actual Result**
- **Status (Pass/Fail)**

### 3.2 Reporting Validation
Validate:
- PDF downloads correctly
- Excel workbook contains expected sheets and values
- CSV exports contain expected headers

### 3.3 AI/ML Validation
Forecasting:
- Verify `/api/ai/forecast` returns `historical`, `forecast` (6 items), and `r_squared`

Segmentation:
- Verify `/api/ai/segment` returns `customers`, `summary`, `centers`, and `k`

---

## 4. What to Submit for Phase 6
- `TESTING_DOCUMENT.md`
- `MODULE_DOCUMENTATION.md`
- `FINAL_PROJECT_REPORT.md`

> Add screenshots/evidence for all failed test cases and link them in the testing document.

---

## 5. Known Notes
- Some UI pages may show static demo values before API fetch completes.
- Role enforcement on all routes should be validated during integration/system testing.

