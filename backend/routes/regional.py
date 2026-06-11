from flask import Blueprint, request, jsonify, Response
from models import db, Sale, Product, Region
from sqlalchemy import func
from datetime import datetime, timedelta
import pandas as pd
import io

regional_bp = Blueprint('regional', __name__)

# ── Helper: get date range ──
def get_date_range(period):
    today = datetime.today().date()
    if period == 'month':
        start = today - timedelta(days=30)
    elif period == 'quarter':
        start = today - timedelta(days=90)
    elif period == 'year':
        start = today - timedelta(days=365)
    else:
        start = today - timedelta(days=90)
    return start, today


# ── Get all regions summary ──
@regional_bp.route('/', methods=['GET'])
def get_regions():
    period     = request.args.get('period', 'quarter')
    metric     = request.args.get('metric', 'revenue')
    start, end = get_date_range(period)

    # Current period
    current = db.session.query(
        Sale.region,
        func.sum(Sale.revenue).label('revenue'),
        func.count(Sale.id).label('orders')
    ).filter(
        Sale.sale_date >= start,
        Sale.sale_date <= end
    ).group_by(
        Sale.region
    ).all()

    # Prior period for growth calculation
    diff        = end - start
    prior_start = start - diff
    prior_end   = start

    prior = db.session.query(
        Sale.region,
        func.sum(Sale.revenue).label('revenue')
    ).filter(
        Sale.sale_date >= prior_start,
        Sale.sale_date <= prior_end
    ).group_by(
        Sale.region
    ).all()

    # Build prior dict
    prior_dict = {}
    for row in prior:
        prior_dict[row[0]] = float(row[1] or 0)

    result = []
    for row in current:
        region       = row[0]
        revenue      = float(row[1] or 0)
        orders       = int(row[2] or 0)
        prior_rev    = prior_dict.get(region, 0)

        # Calculate growth
        growth = 0
        if prior_rev > 0:
            growth = round(
                ((revenue - prior_rev) / prior_rev) * 100, 1
            )

        result.append({
            'region'  : region,
            'revenue' : revenue,
            'orders'  : orders,
            'growth'  : growth
        })

    # Sort by selected metric
    if metric == 'orders':
        result.sort(key=lambda x: x['orders'], reverse=True)
    elif metric == 'growth':
        result.sort(key=lambda x: x['growth'], reverse=True)
    else:
        result.sort(key=lambda x: x['revenue'], reverse=True)

    return jsonify(result), 200


# ── Get top cities ──
@regional_bp.route('/cities', methods=['GET'])
def get_cities():
    period     = request.args.get('period', 'quarter')
    limit      = int(request.args.get('limit', 10))
    start, end = get_date_range(period)

    # Since cities are not in our model
    # we use region as city grouping
    results = db.session.query(
        Sale.region,
        func.sum(Sale.revenue).label('revenue'),
        func.count(Sale.id).label('orders')
    ).filter(
        Sale.sale_date >= start,
        Sale.sale_date <= end
    ).group_by(
        Sale.region
    ).order_by(
        func.sum(Sale.revenue).desc()
    ).limit(limit).all()

    cities = []
    for i, row in enumerate(results):
        cities.append({
            'rank'    : i + 1,
            'city'    : row[0],
            'region'  : row[0],
            'revenue' : float(row[1] or 0),
            'orders'  : int(row[2] or 0)
        })

    return jsonify(cities), 200


# ── Get region trend over months ──
@regional_bp.route('/trend', methods=['GET'])
def get_region_trend():
    period     = request.args.get('period', 'quarter')
    start, end = get_date_range(period)

    results = db.session.query(
        Sale.region,
        func.strftime('%Y-%m', Sale.sale_date).label('month'),
        func.sum(Sale.revenue).label('revenue')
    ).filter(
        Sale.sale_date >= start,
        Sale.sale_date <= end
    ).group_by(
        Sale.region,
        func.strftime('%Y-%m', Sale.sale_date)
    ).order_by(
        func.strftime('%Y-%m', Sale.sale_date)
    ).all()

    # Build structured data by region
    trend_data = {}
    months_set = set()

    for row in results:
        region  = row[0]
        month   = row[1]
        revenue = float(row[2] or 0)

        months_set.add(month)

        if region not in trend_data:
            trend_data[region] = {}
        trend_data[region][month] = revenue

    months = sorted(list(months_set))

    # Build datasets per region
    datasets = []
    for region, monthly in trend_data.items():
        datasets.append({
            'region' : region,
            'data'   : [monthly.get(m, 0) for m in months]
        })

    return jsonify({
        'labels'   : months,
        'datasets' : datasets
    }), 200


# ── Get revenue share per region ──
@regional_bp.route('/share', methods=['GET'])
def get_revenue_share():
    period     = request.args.get('period', 'quarter')
    start, end = get_date_range(period)

    results = db.session.query(
        Sale.region,
        func.sum(Sale.revenue).label('revenue')
    ).filter(
        Sale.sale_date >= start,
        Sale.sale_date <= end
    ).group_by(
        Sale.region
    ).all()

    total = sum(float(row[1] or 0) for row in results)

    share = []
    for row in results:
        revenue = float(row[1] or 0)
        share.append({
            'region'  : row[0],
            'revenue' : revenue,
            'pct'     : round(
                (revenue / total * 100) if total > 0 else 0, 1
            )
        })

    share.sort(key=lambda x: x['revenue'], reverse=True)

    return jsonify(share), 200


# ── Get heatmap data ──
@regional_bp.route('/heatmap', methods=['GET'])
def get_heatmap():
    period     = request.args.get('period', 'quarter')
    start, end = get_date_range(period)

    results = db.session.query(
        Sale.region,
        func.sum(Sale.revenue).label('revenue')
    ).filter(
        Sale.sale_date >= start,
        Sale.sale_date <= end
    ).group_by(
        Sale.region
    ).all()

    max_rev = max(
        (float(row[1] or 0) for row in results), default=1
    )

    heatmap = []
    for row in results:
        revenue   = float(row[1] or 0)
        intensity = round(revenue / max_rev, 2)
        heatmap.append({
            'region'    : row[0],
            'revenue'   : revenue,
            'intensity' : intensity
        })

    return jsonify(heatmap), 200


# ── Export regional data CSV ──
@regional_bp.route('/export', methods=['GET'])
def export_regional():
    period     = request.args.get('period', 'quarter')
    start, end = get_date_range(period)

    results = db.session.query(
        Sale.region,
        func.sum(Sale.revenue).label('revenue'),
        func.count(Sale.id).label('orders')
    ).filter(
        Sale.sale_date >= start,
        Sale.sale_date <= end
    ).group_by(
        Sale.region
    ).order_by(
        func.sum(Sale.revenue).desc()
    ).all()

    data = []
    for i, row in enumerate(results):
        data.append({
            'Rank'    : i + 1,
            'Region'  : row[0],
            'Revenue' : float(row[1] or 0),
            'Orders'  : int(row[2] or 0)
        })

    df     = pd.DataFrame(data)
    output = io.StringIO()
    df.to_csv(output, index=False)

    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={
            'Content-Disposition':
                'attachment; filename=salesiq_regional.csv'
        }
    )