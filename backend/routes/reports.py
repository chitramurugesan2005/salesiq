from flask import Blueprint, request, jsonify, Response
from models import db, Sale, Product, Customer
from sqlalchemy import func
from datetime import datetime, timedelta
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
import pandas as pd
import openpyxl
import io

reports_bp = Blueprint('reports', __name__)

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


# ── Helper: get summary data ──
def get_summary_data(start, end):
    # Revenue and orders
    summary = db.session.query(
        func.sum(Sale.revenue),
        func.count(Sale.id),
        func.sum(Sale.units)
    ).filter(
        Sale.sale_date >= start,
        Sale.sale_date <= end
    ).first()

    # Top products
    top_products = db.session.query(
        Product.name,
        Product.category,
        func.sum(Sale.revenue).label('revenue'),
        func.sum(Sale.units).label('units')
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

    # Regional breakdown
    regions = db.session.query(
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

    return summary, top_products, regions


# ── Generate PDF report ──
@reports_bp.route('/pdf', methods=['GET'])
def generate_pdf():
    period     = request.args.get('period', 'quarter')
    title      = request.args.get('title', 'SalesIQ Report')
    prepared_by = request.args.get('prepared_by', 'Admin')
    start, end = get_date_range(period)

    summary, top_products, regions = get_summary_data(start, end)

    # Create PDF buffer
    buffer = io.BytesIO()
    doc    = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story  = []

    # ── Title ──
    story.append(Paragraph(title, styles['Title']))
    story.append(Spacer(1, 10))
    story.append(Paragraph(
        f'Period: {start} to {end} | Prepared by: {prepared_by}',
        styles['Normal']
    ))
    story.append(Spacer(1, 20))

    # ── KPI Summary ──
    story.append(Paragraph('KPI Summary', styles['Heading1']))
    story.append(Spacer(1, 8))

    kpi_data = [
        ['Metric', 'Value'],
        ['Total Revenue',
            f"${float(summary[0] or 0):,.2f}"],
        ['Total Orders',
            str(int(summary[1] or 0))],
        ['Total Units Sold',
            str(int(summary[2] or 0))],
    ]

    kpi_table = Table(kpi_data, colWidths=[250, 200])
    kpi_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4f8ef7')),
        ('TEXTCOLOR',  (0, 0), (-1, 0), colors.white),
        ('FONTNAME',   (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE',   (0, 0), (-1, 0), 11),
        ('ALIGN',      (0, 0), (-1, -1), 'LEFT'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1),
            [colors.HexColor('#f5f5f5'), colors.white]),
        ('GRID',       (0, 0), (-1, -1), 0.5, colors.grey),
        ('PADDING',    (0, 0), (-1, -1), 8),
    ]))
    story.append(kpi_table)
    story.append(Spacer(1, 20))

    # ── Top Products ──
    story.append(Paragraph('Top 5 Products', styles['Heading1']))
    story.append(Spacer(1, 8))

    prod_data = [['Rank', 'Product', 'Category', 'Revenue', 'Units']]
    for i, row in enumerate(top_products):
        prod_data.append([
            str(i + 1),
            row[0],
            row[1],
            f"${float(row[2] or 0):,.2f}",
            str(int(row[3] or 0))
        ])

    prod_table = Table(
        prod_data,
        colWidths=[40, 160, 100, 100, 60]
    )
    prod_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3ecf8e')),
        ('TEXTCOLOR',  (0, 0), (-1, 0), colors.white),
        ('FONTNAME',   (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('ALIGN',      (0, 0), (-1, -1), 'LEFT'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1),
            [colors.HexColor('#f5f5f5'), colors.white]),
        ('GRID',       (0, 0), (-1, -1), 0.5, colors.grey),
        ('PADDING',    (0, 0), (-1, -1), 8),
    ]))
    story.append(prod_table)
    story.append(Spacer(1, 20))

    # ── Regional Breakdown ──
    story.append(Paragraph('Regional Breakdown', styles['Heading1']))
    story.append(Spacer(1, 8))

    reg_data = [['Region', 'Revenue', 'Orders']]
    for row in regions:
        reg_data.append([
            row[0],
            f"${float(row[1] or 0):,.2f}",
            str(int(row[2] or 0))
        ])

    reg_table = Table(reg_data, colWidths=[160, 160, 140])
    reg_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f0a04b')),
        ('TEXTCOLOR',  (0, 0), (-1, 0), colors.white),
        ('FONTNAME',   (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('ALIGN',      (0, 0), (-1, -1), 'LEFT'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1),
            [colors.HexColor('#f5f5f5'), colors.white]),
        ('GRID',       (0, 0), (-1, -1), 0.5, colors.grey),
        ('PADDING',    (0, 0), (-1, -1), 8),
    ]))
    story.append(reg_table)
    story.append(Spacer(1, 20))

    # ── Footer ──
    story.append(Paragraph(
        f'Generated: {datetime.now().strftime("%d %b %Y %H:%M")} | SalesIQ Analytics Platform',
        styles['Normal']
    ))

    # Build PDF
    doc.build(story)
    buffer.seek(0)

    return Response(
        buffer.getvalue(),
        mimetype='application/pdf',
        headers={
            'Content-Disposition':
                f'attachment; filename=salesiq_report.pdf'
        }
    )


# ── Generate Excel report ──
@reports_bp.route('/excel', methods=['GET'])
def generate_excel():
    period     = request.args.get('period', 'quarter')
    start, end = get_date_range(period)

    summary, top_products, regions = get_summary_data(start, end)

    # Get all sales for raw data sheet
    sales = Sale.query.join(Product).filter(
        Sale.sale_date >= start,
        Sale.sale_date <= end
    ).order_by(Sale.sale_date.desc()).all()

    buffer = io.BytesIO()
    wb     = openpyxl.Workbook()

    # ── Sheet 1: KPI Summary ──
    ws1 = wb.active
    ws1.title = 'KPI Summary'

    ws1.append(['SalesIQ — KPI Summary'])
    ws1.append([f'Period: {start} to {end}'])
    ws1.append([])
    ws1.append(['Metric', 'Value'])
    ws1.append(['Total Revenue',
        float(summary[0] or 0)])
    ws1.append(['Total Orders',
        int(summary[1] or 0)])
    ws1.append(['Total Units Sold',
        int(summary[2] or 0)])

    # ── Sheet 2: Top Products ──
    ws2 = wb.create_sheet('Top Products')
    ws2.append(['Rank', 'Product', 'Category',
        'Revenue', 'Units'])

    for i, row in enumerate(top_products):
        ws2.append([
            i + 1,
            row[0],
            row[1],
            float(row[2] or 0),
            int(row[3] or 0)
        ])

    # ── Sheet 3: Regional ──
    ws3 = wb.create_sheet('Regional')
    ws3.append(['Region', 'Revenue', 'Orders'])

    for row in regions:
        ws3.append([
            row[0],
            float(row[1] or 0),
            int(row[2] or 0)
        ])

    # ── Sheet 4: Raw Sales Data ──
    ws4 = wb.create_sheet('Raw Sales Data')
    ws4.append([
        'ID', 'Product', 'Category', 'Date',
        'Region', 'Units', 'Price', 'Revenue',
        'Status', 'Notes'
    ])

    for s in sales:
        ws4.append([
            s.id,
            s.product.name,
            s.product.category,
            s.sale_date.strftime('%Y-%m-%d'),
            s.region,
            s.units,
            float(s.product.price),
            float(s.revenue),
            s.status,
            s.notes
        ])

    wb.save(buffer)
    buffer.seek(0)

    return Response(
        buffer.getvalue(),
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        headers={
            'Content-Disposition':
                'attachment; filename=salesiq_report.xlsx'
        }
    )


# ── Generate CSV report ──
@reports_bp.route('/csv', methods=['GET'])
def generate_csv():
    period     = request.args.get('period', 'quarter')
    start, end = get_date_range(period)

    sales = Sale.query.join(Product).filter(
        Sale.sale_date >= start,
        Sale.sale_date <= end
    ).order_by(Sale.sale_date.desc()).all()

    data = []
    for s in sales:
        data.append({
            'ID'       : s.id,
            'Product'  : s.product.name,
            'Category' : s.product.category,
            'Date'     : s.sale_date.strftime('%Y-%m-%d'),
            'Region'   : s.region,
            'Units'    : s.units,
            'Price'    : float(s.product.price),
            'Revenue'  : float(s.revenue),
            'Status'   : s.status,
            'Notes'    : s.notes
        })

    df     = pd.DataFrame(data)
    output = io.StringIO()
    df.to_csv(output, index=False)

    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={
            'Content-Disposition':
                'attachment; filename=salesiq_report.csv'
        }
    )


# ── Get report history (static for now) ──
@reports_bp.route('/history', methods=['GET'])
def get_history():
    history = [
        {
            'name'   : 'Q2 2026 Full Report',
            'format' : 'PDF',
            'date'   : 'Today',
            'status' : 'Ready'
        },
        {
            'name'   : 'Sales Performance',
            'format' : 'Excel',
            'date'   : 'Yesterday',
            'status' : 'Ready'
        },
        {
            'name'   : 'Customer Analytics',
            'format' : 'PDF',
            'date'   : '2 days ago',
            'status' : 'Ready'
        }
    ]
    return jsonify(history), 200