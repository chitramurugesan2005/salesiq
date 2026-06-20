from flask import Blueprint, request, jsonify, Response
from models import db, Customer, Sale, Product
from sqlalchemy import func
from datetime import datetime, timedelta
import pandas as pd
import io

customers_bp = Blueprint('customers', __name__)

# ── Helper: get date range ──
def get_date_range(period):
    today = datetime.today().date()
    if period == 'week':
        start = today - timedelta(days=7)
    elif period == 'month':
        start = today - timedelta(days=30)
    elif period == 'quarter':
        start = today - timedelta(days=90)
    elif period == 'year':
        start = today - timedelta(days=365)
    else:
        start = today - timedelta(days=30)
    return start, today


# ── Get all customers ──
@customers_bp.route('/', methods=['GET'])
def get_customers():
    period  = request.args.get('period', 'month')
    segment = request.args.get('segment', '')
    search  = request.args.get('search', '')
    start, end = get_date_range(period)

    # Query customers
    query = Customer.query
    if segment:
        query = query.filter(Customer.segment == segment)
    if search:
        query = query.filter(
            Customer.name.ilike(f'%{search}%') |
            Customer.email.ilike(f'%{search}%')
        )

    customers = query.order_by(Customer.total_spend.desc()).all()

    result = []
    for c in customers:
        result.append({
            'id'           : c.id,
            'name'         : c.name,
            'email'        : c.email,
            'region'       : c.region,
            'segment'      : c.segment,
            'total_orders' : c.total_orders,
            'total_spend'  : float(c.total_spend),
            'avg_spend'    : float(c.avg_spend),
            'ltv'          : float(c.ltv),
            'active_period': True
    })

    # Sort by period spend
    result.sort(key=lambda x: x['total_spend'], reverse=True)

    return jsonify(result), 200


# ── Get single customer ──
@customers_bp.route('/<int:customer_id>', methods=['GET'])
def get_customer(customer_id):
    customer = Customer.query.get_or_404(customer_id)

    return jsonify({
        'id'           : customer.id,
        'name'         : customer.name,
        'email'        : customer.email,
        'region'       : customer.region,
        'segment'      : customer.segment,
        'total_orders' : customer.total_orders,
        'total_spend'  : float(customer.total_spend),
        'avg_spend'    : float(customer.avg_spend),
        'ltv'          : float(customer.ltv)
    }), 200


# ── Add new customer ──
@customers_bp.route('/', methods=['POST'])
def add_customer():
    data  = request.get_json()
    name  = data.get('name')
    email = data.get('email')
    region = data.get('region')

    if not all([name, email, region]):
        return jsonify({'error': 'All fields are required'}), 400

    existing = Customer.query.filter_by(email=email).first()
    if existing:
        return jsonify({'error': 'Email already exists'}), 409

    new_customer = Customer(
        name   = name,
        email  = email,
        region = region
    )

    db.session.add(new_customer)
    db.session.commit()

    return jsonify({'message': 'Customer added successfully'}), 201


# ── Update customer ──
@customers_bp.route('/<int:customer_id>', methods=['PUT'])
def update_customer(customer_id):
    customer = Customer.query.get_or_404(customer_id)
    data     = request.get_json()

    customer.name    = data.get('name', customer.name)
    customer.email   = data.get('email', customer.email)
    customer.region  = data.get('region', customer.region)
    customer.segment = data.get('segment', customer.segment)

    db.session.commit()

    return jsonify({'message': 'Customer updated successfully'}), 200


# ── Delete customer ──
@customers_bp.route('/<int:customer_id>', methods=['DELETE'])
def delete_customer(customer_id):
    customer = Customer.query.get_or_404(customer_id)
    db.session.delete(customer)
    db.session.commit()

    return jsonify({'message': 'Customer deleted successfully'}), 200


# ── Get KPI summary ──
@customers_bp.route('/kpis', methods=['GET'])
def get_kpis():
    period     = request.args.get('period', 'month')
    start, end = get_date_range(period)

    # Total customers
    total = Customer.query.count()

    # New customers this period
    new_customers = Customer.query.filter(
        Customer.created_at >= start,
        Customer.created_at <= end
    ).count()

    # Returning customers
    returning = Customer.query.filter(
        Customer.total_orders > 1
    ).count()

    # Average LTV
    avg_ltv = db.session.query(
        func.avg(Customer.ltv)
    ).scalar() or 0

    # Segment counts
    champions = Customer.query.filter_by(
        segment='Champions'
    ).count()

    regular = Customer.query.filter_by(
        segment='Regular'
    ).count()

    one_time = Customer.query.filter_by(
        segment='One-Time'
    ).count()

    return jsonify({
        'total'         : total,
        'new'           : new_customers,
        'returning'     : returning,
        'avg_ltv'       : round(float(avg_ltv), 2),
        'champions'     : champions,
        'regular'       : regular,
        'one_time'      : one_time
    }), 200


# ── Get segment summary ──
@customers_bp.route('/segments', methods=['GET'])
def get_segments():
    segments = db.session.query(
        Customer.segment,
        func.count(Customer.id).label('count'),
        func.avg(Customer.avg_spend).label('avg_spend'),
        func.avg(Customer.total_orders).label('avg_orders'),
        func.avg(Customer.ltv).label('avg_ltv')
    ).group_by(
        Customer.segment
    ).all()

    result = []
    for row in segments:
        result.append({
            'segment'    : row[0],
            'count'      : int(row[1] or 0),
            'avg_spend'  : round(float(row[2] or 0), 2),
            'avg_orders' : round(float(row[3] or 0), 1),
            'avg_ltv'    : round(float(row[4] or 0), 2)
        })

    return jsonify(result), 200


# ── Get top customers ──
@customers_bp.route('/top', methods=['GET'])
def get_top_customers():
    limit = int(request.args.get('limit', 10))

    customers = Customer.query.order_by(
        Customer.total_spend.desc()
    ).limit(limit).all()

    result = []
    for c in customers:
        result.append({
            'id'           : c.id,
            'name'         : c.name,
            'email'        : c.email,
            'segment'      : c.segment,
            'total_orders' : c.total_orders,
            'total_spend'  : float(c.total_spend),
            'ltv'          : float(c.ltv)
        })

    return jsonify(result), 200


# ── Get new vs returning ──
@customers_bp.route('/new-vs-returning', methods=['GET'])
def new_vs_returning():
    new_count = Customer.query.filter(
        Customer.total_orders <= 1
    ).count()

    returning_count = Customer.query.filter(
        Customer.total_orders > 1
    ).count()

    return jsonify({
        'new'       : new_count,
        'returning' : returning_count
    }), 200


# ── Export customers CSV ──
@customers_bp.route('/export', methods=['GET'])
def export_customers():
    customers = Customer.query.order_by(
        Customer.total_spend.desc()
    ).all()

    data = []
    for c in customers:
        data.append({
            'ID'           : c.id,
            'Name'         : c.name,
            'Email'        : c.email,
            'Region'       : c.region,
            'Segment'      : c.segment,
            'Total Orders' : c.total_orders,
            'Total Spend'  : c.total_spend,
            'Avg Spend'    : c.avg_spend,
            'LTV'          : c.ltv
        })

    df     = pd.DataFrame(data)
    output = io.StringIO()
    df.to_csv(output, index=False)

    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={
            'Content-Disposition':
                'attachment; filename=salesiq_customers.csv'
        }
    )