from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

# ── Users Table ──
class User(db.Model):
    __tablename__ = 'users'

    id         = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name  = db.Column(db.String(50), nullable=False)
    email      = db.Column(db.String(100), unique=True, nullable=False)
    password   = db.Column(db.String(255), nullable=False)
    role       = db.Column(db.Enum('admin', 'user'), default='user')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# ── Products Table ──
class Product(db.Model):
    __tablename__ = 'products'

    id       = db.Column(db.Integer, primary_key=True)
    name     = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    price    = db.Column(db.Float, nullable=False)
    stock    = db.Column(db.Integer, default=0)

# ── Sales Table ──
class Sale(db.Model):
    __tablename__ = 'sales'

    id         = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    units      = db.Column(db.Integer, nullable=False)
    revenue    = db.Column(db.Float, nullable=False)
    region     = db.Column(db.String(50), nullable=False)
    status     = db.Column(db.Enum('Completed','Pending','Refunded'), default='Completed')
    notes      = db.Column(db.String(255), default='')
    sale_date  = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    product = db.relationship('Product', backref='sales')

# ── Customers Table ──
class Customer(db.Model):
    __tablename__ = 'customers'

    id               = db.Column(db.Integer, primary_key=True)
    name             = db.Column(db.String(100), nullable=False)
    email            = db.Column(db.String(100), unique=True, nullable=False)
    region           = db.Column(db.String(50), nullable=False)
    segment          = db.Column(db.String(50), default='One-Time')
    total_orders     = db.Column(db.Integer, default=0)
    total_spend      = db.Column(db.Float, default=0.0)
    avg_spend        = db.Column(db.Float, default=0.0)
    ltv              = db.Column(db.Float, default=0.0)
    created_at       = db.Column(db.DateTime, default=datetime.utcnow)

# ── Regions Table ──
class Region(db.Model):
    __tablename__ = 'regions'

    id      = db.Column(db.Integer, primary_key=True)
    name    = db.Column(db.String(50), nullable=False)
    revenue = db.Column(db.Float, default=0.0)
    orders  = db.Column(db.Integer, default=0)
    growth  = db.Column(db.Float, default=0.0)