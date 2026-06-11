from flask import Blueprint, request, jsonify
from models import db, Sale, Product
from datetime import datetime
import pandas as pd
import io

sales_bp = Blueprint('sales', __name__)

# ── Get all sales records ──
@sales_bp.route('/', methods=['GET'])
def get_sales():
    # Get filter parameters
    category = request.args.get('category')
    status   = request.args.get('status')
    region   = request.args.get('region')
    search   = request.args.get('search')

    query = Sale.query.join(Product)

    if category:
        query = query.filter(Product.category == category)
    if status:
        query = query.filter(Sale.status == status)
    if region:
        query = query.filter(Sale.region == region)
    if search:
        query = query.filter(Product.name.ilike(f'%{search}%'))

    sales = query.order_by(Sale.sale_date.desc()).all()

    result = []
    for s in sales:
        result.append({
            'id'        : s.id,
            'product'   : s.product.name,
            'category'  : s.product.category,
            'date'      : s.sale_date.strftime('%Y-%m-%d'),
            'region'    : s.region,
            'units'     : s.units,
            'price'     : s.product.price,
            'revenue'   : s.revenue,
            'status'    : s.status,
            'notes'     : s.notes
        })

    return jsonify(result), 200


# ── Add single sale record ──
@sales_bp.route('/', methods=['POST'])
def add_sale():
    data = request.get_json()

    product_name = data.get('product')
    category     = data.get('category')
    date         = data.get('date')
    region       = data.get('region')
    units        = data.get('units')
    price        = data.get('price')
    status       = data.get('status', 'Completed')
    notes        = data.get('notes', '')

    if not all([product_name, category, date, region, units, price]):
        return jsonify({'error': 'All fields are required'}), 400

    # Find or create product
    product = Product.query.filter_by(
        name=product_name,
        category=category
    ).first()

    if not product:
        product = Product(
            name     = product_name,
            category = category,
            price    = float(price),
            stock    = 0
        )
        db.session.add(product)
        db.session.flush()

    revenue = float(units) * float(price)

    new_sale = Sale(
        product_id = product.id,
        units      = int(units),
        revenue    = revenue,
        region     = region,
        status     = status,
        notes      = notes,
        sale_date  = datetime.strptime(date, '%Y-%m-%d').date()
    )

    db.session.add(new_sale)
    db.session.commit()

    return jsonify({'message': 'Sale record added successfully'}), 201


# ── Update sale record ──
@sales_bp.route('/<int:sale_id>', methods=['PUT'])
def update_sale(sale_id):
    sale = Sale.query.get_or_404(sale_id)
    data = request.get_json()

    units  = data.get('units', sale.units)
    price  = data.get('price', sale.product.price)
    region = data.get('region', sale.region)
    status = data.get('status', sale.status)
    notes  = data.get('notes', sale.notes)
    date   = data.get('date')

    sale.units   = int(units)
    sale.revenue = float(units) * float(price)
    sale.region  = region
    sale.status  = status
    sale.notes   = notes

    if date:
        sale.sale_date = datetime.strptime(date, '%Y-%m-%d').date()

    # Update product price
    sale.product.price = float(price)

    db.session.commit()

    return jsonify({'message': 'Sale record updated successfully'}), 200


# ── Delete single sale record ──
@sales_bp.route('/<int:sale_id>', methods=['DELETE'])
def delete_sale(sale_id):
    sale = Sale.query.get_or_404(sale_id)
    db.session.delete(sale)
    db.session.commit()
    return jsonify({'message': 'Sale record deleted successfully'}), 200


# ── Bulk delete ──
@sales_bp.route('/bulk-delete', methods=['POST'])
def bulk_delete():
    data = request.get_json()
    ids  = data.get('ids', [])

    if not ids:
        return jsonify({'error': 'No IDs provided'}), 400

    Sale.query.filter(Sale.id.in_(ids)).delete(
        synchronize_session=False
    )
    db.session.commit()

    return jsonify({
        'message': f'{len(ids)} records deleted successfully'
    }), 200


# ── Bulk import from CSV/Excel ──
@sales_bp.route('/bulk-import', methods=['POST'])
def bulk_import():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['file']
    filename = file.filename

    try:
        # Read file into dataframe
        if filename.endswith('.csv'):
            df = pd.read_csv(io.StringIO(
                file.read().decode('utf-8')
            ))
        else:
            df = pd.read_excel(file)

        required_cols = [
            'product_name', 'category',
            'sale_date', 'units_sold',
            'unit_price', 'region'
        ]

        # Check required columns exist
        for col in required_cols:
            if col not in df.columns:
                return jsonify({
                    'error': f'Missing column: {col}'
                }), 400

        imported = 0
        for _, row in df.iterrows():
            # Find or create product
            product = Product.query.filter_by(
                name     = str(row['product_name']),
                category = str(row['category'])
            ).first()

            if not product:
                product = Product(
                    name     = str(row['product_name']),
                    category = str(row['category']),
                    price    = float(row['unit_price']),
                    stock    = 0
                )
                db.session.add(product)
                db.session.flush()

            units   = int(row['units_sold'])
            price   = float(row['unit_price'])
            revenue = units * price

            new_sale = Sale(
                product_id = product.id,
                units      = units,
                revenue    = revenue,
                region     = str(row['region']),
                status     = str(row.get('status', 'Completed')),
                notes      = str(row.get('notes', '')),
                sale_date  = pd.to_datetime(
                    row['sale_date']
                ).date()
            )
            db.session.add(new_sale)
            imported += 1

        db.session.commit()
        return jsonify({
            'message': f'{imported} records imported successfully'
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ── Export sales as CSV ──
@sales_bp.route('/export', methods=['GET'])
def export_sales():
    sales = Sale.query.join(Product).all()

    data = []
    for s in sales:
        data.append({
            'ID'       : s.id,
            'Product'  : s.product.name,
            'Category' : s.product.category,
            'Date'     : s.sale_date.strftime('%Y-%m-%d'),
            'Region'   : s.region,
            'Units'    : s.units,
            'Price'    : s.product.price,
            'Revenue'  : s.revenue,
            'Status'   : s.status,
            'Notes'    : s.notes
        })

    df = pd.DataFrame(data)
    output = io.StringIO()
    df.to_csv(output, index=False)

    from flask import Response
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={
            'Content-Disposition':
                'attachment; filename=salesiq_records.csv'
        }
    )