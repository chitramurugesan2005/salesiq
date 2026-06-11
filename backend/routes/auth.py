from flask import Blueprint, request, jsonify, session
from models import db, User
from werkzeug.security import generate_password_hash, check_password_hash

auth_bp = Blueprint('auth', __name__)

# ── Admin secret key ──
# Keep this value same as in login.html and register.html
ADMIN_SECRET_KEY = 'ADMIN-SECRET-KEY'


# ── Register ──
@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    first_name = data.get('first_name', '').strip()
    last_name  = data.get('last_name',  '').strip()
    email      = data.get('email',      '').strip().lower()
    password   = data.get('password',   '')
    role       = data.get('role',       'user')
    admin_key  = data.get('admin_key',  '')

    # Validate required fields
    if not first_name or not last_name or not email or not password:
        return jsonify({'error': 'All fields are required'}), 400

    # Validate role value
    if role not in ('admin', 'user'):
        return jsonify({'error': 'Invalid role'}), 400

    # Validate admin secret key if registering as admin
    if role == 'admin' and admin_key != ADMIN_SECRET_KEY:
        return jsonify({'error': 'Invalid admin secret key'}), 403

    # Check if email already registered
    existing = User.query.filter_by(email=email).first()
    if existing:
        return jsonify({'error': 'Email already registered'}), 409

    # Hash password and save
    hashed_password = generate_password_hash(password)
    new_user = User(
        first_name = first_name,
        last_name  = last_name,
        email      = email,
        password   = hashed_password,
        role       = role
    )
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'Account created successfully'}), 201


# ── Login ──
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    email     = data.get('email',     '').strip().lower()
    password  = data.get('password',  '')
    role      = data.get('role',      'user')
    admin_key = data.get('admin_key', '')

    if not email or not password:
        return jsonify({'error': 'Email and password are required'}), 400

    # Find user
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({'error': 'Invalid email or password'}), 401

    # Check password
    if not check_password_hash(user.password, password):
        return jsonify({'error': 'Invalid email or password'}), 401

    # Check selected role matches account role
    if user.role != role:
        return jsonify({'error': f'This account is not registered as {role}'}), 401

    # Extra admin key check
    if role == 'admin' and admin_key != ADMIN_SECRET_KEY:
        return jsonify({'error': 'Invalid admin secret key'}), 401

    # Save session
    session.permanent          = True
    session['user_id']         = user.id
    session['role']            = user.role
    session['email']           = user.email
    session['first_name']      = user.first_name
    session['last_name']       = user.last_name

    return jsonify({
        'message'    : 'Login successful',
        'user_id'    : user.id,
        'role'       : user.role,
        'first_name' : user.first_name,
        'last_name'  : user.last_name,
        'email'      : user.email
    }), 200


# ── Logout ──
@auth_bp.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'message': 'Logged out successfully'}), 200


# ── Get current logged-in user ──
@auth_bp.route('/me', methods=['GET'])
def me():
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401

    user = User.query.get(session['user_id'])
    if not user:
        session.clear()
        return jsonify({'error': 'User not found'}), 404

    return jsonify({
        'user_id'    : user.id,
        'role'       : user.role,
        'first_name' : user.first_name,
        'last_name'  : user.last_name,
        'email'      : user.email
    }), 200


# ── Role check helper (used by other route files) ──
def require_role(*roles):
    """
    Call this at the top of any protected route.
    Returns (session_dict, None) if OK.
    Returns (None, error_response_tuple) if not.

    Example:
        user, err = require_role('admin')
        if err: return err
    """
    if 'user_id' not in session:
        return None, (jsonify({'error': 'Not authenticated'}), 401)
    if session.get('role') not in roles:
        return None, (jsonify({'error': 'Access denied — insufficient permissions'}), 403)
    return session, None