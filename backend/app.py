from flask import Flask, send_from_directory
from flask_cors import CORS
from config import Config
from models import db
import os

def create_app():
    app = Flask(
        __name__,
        static_folder='frontend',
        static_url_path=''
    )
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)
    CORS(app)

    # Create upload folder if not exists
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])

    # Register all route blueprints
    from routes.auth      import auth_bp
    from routes.sales     import sales_bp
    from routes.dashboard import dashboard_bp
    from routes.products  import products_bp
    from routes.customers import customers_bp
    from routes.regional  import regional_bp
    from routes.reports   import reports_bp
    from ai_ml.ai         import ai_bp 

    app.register_blueprint(auth_bp,      url_prefix='/api/auth')
    app.register_blueprint(sales_bp,     url_prefix='/api/sales')
    app.register_blueprint(dashboard_bp, url_prefix='/api/dashboard')
    app.register_blueprint(products_bp,  url_prefix='/api/products')
    app.register_blueprint(customers_bp, url_prefix='/api/customers')
    app.register_blueprint(regional_bp,  url_prefix='/api/regional')
    app.register_blueprint(reports_bp,   url_prefix='/api/reports')
    app.register_blueprint(ai_bp,        url_prefix='/api/ai')

    # Create all tables in database
    with app.app_context():
        db.create_all()
        print("✅ Database tables created successfully")

    # ── Serve frontend pages ──
    @app.route('/')
    def index():
        return send_from_directory('frontend', 'login.html')

    @app.route('/<path:filename>')
    def serve_frontend(filename):
        return send_from_directory('frontend', filename)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)