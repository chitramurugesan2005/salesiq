from flask import Blueprint, request, jsonify
from models import db, Sale, Product, Customer, Region
from sqlalchemy import func
from datetime import datetime, timedelta

dashboard_bp = Blueprint('dashboard', __name__)

# ── Helper: get date range based on period ──
def get_date_range(period):
    today = datetime.today().date()
    if period == '7d':
        start = today - timedelta(days=7)
    elif period == '30d':
        start = today - timedelta(days=30)
    elif period == '90d':
        start = today - timedelta(days=90)
    elif period == '1y':
        start = today - timedelta(days=365)
    else:
        start = today - timedelta(days=30)
    return start, today


# ── KPI Summary ──
@dashboard_bp.route('/kpis', methods=['GET'])
def get_kpis():
    period = request.args.get('period', '30d')
    start, end = get_date_range(period)

    # Current period
    current = db.session.query(
        func.sum(Sale.revenue),
        func.count(Sale.id),
        func.sum(Sale.units)
    ).filter(
        Sale.sale_date >= start,
        Sale.sale_date <= end
    ).first()

    # Prior period for comparison
    diff        = end - start
    prior_start = start - diff
    prior_end   = start

    prior = db.session.query(
        func.sum(Sale.revenue),
        func.count(Sale.id)
    ).filter(
        Sale.sale_date >= prior_start,
        Sale.sale_date <= prior_end
    ).first()

    current_revenue = float(current[0] or 0)
    current_orders  = int(current[1] or 0)
    prior_revenue   = float(prior[0] or 0)
    prior_orders    = int(prior[1] or 0)

    # Calculate percentage changes
    rev_change = 0
    ord_change = 0

    if prior_revenue > 0:
        rev_change = round(
            ((current_revenue - prior_revenue) / prior_revenue) * 100, 1
        )
    if prior_orders > 0:
        ord_change = round(
            ((current_orders - prior_orders) / prior_orders) * 100, 1
        )

    return jsonify({
        'revenue'        : current_revenue,
        'orders'         : current_orders,
        'revenue_change' : rev_change,
        'orders_change'  : ord_change,
        'period'         : period
    }), 200


# ── Revenue Trend ──
@dashboard_bp.route('/trend', methods=['GET'])
def get_trend():
    period    = request.args.get('period', '30d')
    date_from = request.args.get('from', None)
    date_to   = request.args.get('to', None)

    # If custom date range provided, use it
    if date_from and date_to:
        try:
            start = datetime.strptime(date_from, '%Y-%m-%d').date()
            end   = datetime.strptime(date_to,   '%Y-%m-%d').date()
        except ValueError:
            start, end = get_date_range(period)
    else:
        start, end = get_date_range(period)

    results = db.session.query(
        Sale.sale_date,
        func.sum(Sale.revenue),
        func.count(Sale.id)
    ).filter(
        Sale.sale_date >= start,
        Sale.sale_date <= end
    ).group_by(
        Sale.sale_date
    ).order_by(
        Sale.sale_date
    ).all()

    labels  = []
    revenue = []
    orders  = []

    for row in results:
        labels.append(row[0].strftime('%d %b'))
        revenue.append(float(row[1] or 0))
        orders.append(int(row[2] or 0))

    return jsonify({
        'labels'  : labels,
        'revenue' : revenue,
        'orders'  : orders
    }), 200


# ── Revenue by Category ──
@dashboard_bp.route('/categories', methods=['GET'])
def get_categories():
    period = request.args.get('period', '30d')
    start, end = get_date_range(period)

    results = db.session.query(
        Product.category,
        func.sum(Sale.revenue)
    ).join(
        Sale, Sale.product_id == Product.id
    ).filter(
        Sale.sale_date >= start,
        Sale.sale_date <= end
    ).group_by(
        Product.category
    ).all()

    categories = []
    values     = []

    for row in results:
        categories.append(row[0])
        values.append(float(row[1] or 0))

    return jsonify({
        'categories' : categories,
        'values'     : values
    }), 200


# ── Top Products ──
@dashboard_bp.route('/top-products', methods=['GET'])
def get_top_products():
    period = request.args.get('period', '30d')
    start, end = get_date_range(period)

    results = db.session.query(
        Product.name,
        Product.category,
        func.sum(Sale.revenue),
        func.sum(Sale.units)
    ).join(
        Sale, Sale.product_id == Product.id
    ).filter(
        Sale.sale_date >= start,
        Sale.sale_date <= end
    ).group_by(
        Product.id,
        Product.name,
        Product.category
    ).order_by(
        func.sum(Sale.revenue).desc()
    ).limit(5).all()

    products = []
    max_rev  = float(results[0][2]) if results else 1

    for row in results:
        rev = float(row[2] or 0)
        products.append({
            'name'     : row[0],
            'category' : row[1],
            'revenue'  : rev,
            'units'    : int(row[3] or 0),
            'pct'      : round((rev / max_rev) * 100)
        })

    return jsonify(products), 200


# ── Recent Activity ──
@dashboard_bp.route('/activity', methods=['GET'])
def get_activity():
    recent = Sale.query.order_by(
        Sale.created_at.desc()
    ).limit(5).all()

    activity = []
    for s in recent:
        activity.append({
            'id'       : s.id,
            'product'  : s.product.name,
            'units'    : s.units,
            'revenue'  : s.revenue,
            'status'   : s.status,
            'region'   : s.region,
            'date'     : s.sale_date.strftime('%Y-%m-%d')
        })

    return jsonify(activity), 200