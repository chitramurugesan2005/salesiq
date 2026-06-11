import os

class Config:
    # Database connection
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:Chitra%402005@localhost/salesiq'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'salesiq-secret-key-2026'

    # File upload settings
    UPLOAD_FOLDER = 'uploads'
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10 MB max file size