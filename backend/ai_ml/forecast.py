import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error
from datetime import date
from models import db
from sqlalchemy import text


def get_monthly_sales():
    query = text("""
        SELECT 
            YEAR(sale_date)  AS yr,
            MONTH(sale_date) AS mo,
            SUM(revenue)     AS total
        FROM sales
        GROUP BY YEAR(sale_date), MONTH(sale_date)
        ORDER BY yr, mo
    """)
    return db.session.execute(query).fetchall()


def run_forecast():
    rows = get_monthly_sales()

    if len(rows) < 2:
        return None, "Not enough sales data to forecast."

    X = np.array(range(1, len(rows) + 1)).reshape(-1, 1)
    y = np.array([float(row.total) for row in rows])

    model = LinearRegression()
    model.fit(X, y)

    # ── Predictions on training data for accuracy metrics ──
    y_pred_train = model.predict(X)

    mae  = mean_absolute_error(y, y_pred_train)
    mse  = mean_squared_error(y, y_pred_train)
    rmse = np.sqrt(mse)

    # MAPE — avoid division by zero
    mape = np.mean(
        np.abs((y - y_pred_train) / y)
    ) * 100

    # ── Future predictions ──
    future_X = np.array(
        range(len(rows) + 1, len(rows) + 7)
    ).reshape(-1, 1)
    predictions = model.predict(future_X)

    last_yr = int(rows[-1].yr)
    last_mo = int(rows[-1].mo)

    def next_label(yr, mo, offset):
        mo = mo + offset
        while mo > 12:
            mo -= 12
            yr += 1
        return date(yr, mo, 1).strftime("%b %Y")

    historical = [
        {"label": date(int(r.yr), int(r.mo), 1).strftime("%b %Y"),
         "value": round(float(r.total), 2)}
        for r in rows
    ]

    forecast = [
        {"label": next_label(last_yr, last_mo, i + 1),
         "value": round(max(float(predictions[i]), 0), 2)}
        for i in range(6)
    ]

    return {
        "historical": historical,
        "forecast":   forecast,
        "r_squared":  round(model.score(X, y), 4),
        "mae":        round(float(mae), 2),
        "rmse":       round(float(rmse), 2),
        "mape":       round(float(mape), 2),
        "coefficient": round(float(model.coef_[0]), 2),
        "intercept":   round(float(model.intercept_), 2),
        "samples":     len(rows)
    }, None