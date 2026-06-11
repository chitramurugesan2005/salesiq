from flask import Blueprint, request, jsonify, Response
from models import db, Sale, Product
from sqlalchemy import func
from datetime import datetime, timedelta
import pandas as pd
import io

products_bp = Blueprint('products', __name__)

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


# ── Get all products with performance ──
@products_bp.route('/', methods=['GET'])
def get_products():
    period   = request.args.get('period', 'quarter')
    category = request.args.get('category', '')
    metric   = request.args.get('metric', 'revenue')
    start, end = get_date_range(period)

    query = db.session.query(
        Product.id,
        Product.name,
        Product.category,
        Product.price,
        Product.stock,
        func.sum(Sale.revenue).label('total_revenue'),
        func.sum(Sale.units).label('total_units')
    ).outerjoin(
        Sale, (Sale.product_id == Product.id) &
              (Sale.sale_date >= start) &
              (Sale.sale_date <= end)
    ).group_by(
        Product.id,
        Product.name,
        Product.category,
        Product.price,
        Product.stock
    )

    if category:
        query = query.filter(Product.category == category)

    # Sort by selected metric
    if metric == 'units':
        query = query.order_by(
            func.sum(Sale.units).desc()
        )
    else:
        query = query.order_by(
            func.sum(Sale.revenue).desc()
        )

    results  = query.all()
    products = []

    for row in results:
        products.append({
            'id'       : row[0],
            'name'     : row[1],
            'category' : row[2],
            'price'    : float(row[3]),
            'stock'    : int(row[4]),
            'revenue'  : float(row[5] or 0),
            'units'    : int(row[6] or 0)
        })

    return jsonify(products), 200


# ── Get single product ──
@products_bp.route('/<int:product_id>', methods=['GET'])
def get_product(product_id):
    product = Product.query.get_or_404(product_id)

    return jsonify({
        'id'       : product.id,
        'name'     : product.name,
        'category' : product.category,
        'price'    : float(product.price),
        'stock'    : int(product.stock)
    }), 200


# ── Add new product ──
@products_bp.route('/', methods=['POST'])
def add_product():
    data     = request.get_json()
    name     = data.get('name')
    category = data.get('category')
    price    = data.get('price')
    stock    = data.get('stock', 0)

    if not all([name, category, price]):
        return jsonify({'error': 'All fields are required'}), 400

    # Check if product already exists
    existing = Product.query.filter_by(
        name=name, category=category
    ).first()

    if existing:
        return jsonify({'error': 'Product already exists'}), 409

    new_product = Product(
        name     = name,
        category = category,
        price    = float(price),
        stock    = int(stock)
    )

    db.session.add(new_product)
    db.session.commit()

    return jsonify({'message': 'Product added successfully'}), 201


# ── Update product ──
@products_bp.route('/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    product  = Product.query.get_or_404(product_id)
    data     = request.get_json()

    product.name     = data.get('name', product.name)
    product.category = data.get('category', product.category)
    product.price    = float(data.get('price', product.price))
    product.stock    = int(data.get('stock', product.stock))

    db.session.commit()

    return jsonify({'message': 'Product updated successfully'}), 200


# ── Delete product ──
@products_bp.route('/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)

    # Check if product has sales records
    sales_count = Sale.query.filter_by(
        product_id=product_id
    ).count()

    if sales_count > 0:
        return jsonify({
            'error': f'Cannot delete — product has {sales_count} sales records'
        }), 400

    db.session.delete(product)
    db.session.commit()

    return jsonify({'message': 'Product deleted successfully'}), 200


# ── Get category summary ──
@products_bp.route('/categories/summary', methods=['GET'])
def get_category_summary():
    period     = request.args.get('period', 'quarter')
    start, end = get_date_range(period)

    results = db.session.query(
        Product.category,
        func.count(Product.id).label('product_count'),
        func.sum(Sale.revenue).label('total_revenue'),
        func.sum(Sale.units).label('total_units')
    ).outerjoin(
        Sale, (Sale.product_id == Product.id) &
              (Sale.sale_date >= start) &
              (Sale.sale_date <= end)
    ).group_by(
        Product.category
    ).all()

    summary = []
    for row in results:
        summary.append({
            'category'      : row[0],
            'product_count' : int(row[1] or 0),
            'revenue'       : float(row[2] or 0),
            'units'         : int(row[3] or 0)
        })

    return jsonify(summary), 200


# ── Get underperforming products ──
@products_bp.route('/underperforming', methods=['GET'])
def get_underperforming():
    period     = request.args.get('period', 'quarter')
    threshold  = float(request.args.get('threshold', 2000))
    start, end = get_date_range(period)

    results = db.session.query(
        Product.id,
        Product.name,
        Product.category,
        func.sum(Sale.revenue).label('total_revenue'),
        func.sum(Sale.units).label('total_units')
    ).outerjoin(
        Sale, (Sale.product_id == Product.id) &
              (Sale.sale_date >= start) &
              (Sale.sale_date <= end)
    ).group_by(
        Product.id,
        Product.name,
        Product.category
    ).having(
        func.sum(Sale.revenue) < threshold
    ).order_by(
        func.sum(Sale.revenue).asc()
    ).all()

    products = []
    for row in results:
        products.append({
            'id'       : row[0],
            'name'     : row[1],
            'category' : row[2],
            'revenue'  : float(row[3] or 0),
            'units'    : int(row[4] or 0)
        })

    return jsonify(products), 200


# ── Export products CSV ──
@products_bp.route('/export', methods=['GET'])
def export_products():
    products = Product.query.all()

    data = []
    for p in products:
        data.append({
            'ID'       : p.id,
            'Name'     : p.name,
            'Category' : p.category,
            'Price'    : p.price,
            'Stock'    : p.stock
        })

    df     = pd.DataFrame(data)
    output = io.StringIO()
    df.to_csv(output, index=False)

    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={
            'Content-Disposition':
                'attachment; filename=salesiq_products.csv'
        }
    )