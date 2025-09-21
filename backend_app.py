
from flask import Flask, request, jsonify, session
from flask_cors import CORS
import sqlite3
import hashlib
import secrets
import qrcode
import io
import base64
from datetime import datetime, date
import os
import json

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)
CORS(app)

DATABASE = 'krishichain.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_database():
    """Initialize the database with schema"""
    conn = get_db_connection()

    # Read and execute schema
    with open('krishichain_schema.sql', 'r') as f:
        schema = f.read()

    # Execute each statement separately
    statements = schema.split(';')
    for statement in statements:
        if statement.strip():
            try:
                conn.execute(statement)
            except sqlite3.Error as e:
                print(f"Error executing statement: {e}")

    conn.commit()
    conn.close()

def hash_password(password):
    """Hash password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

def generate_qr_code():
    """Generate unique QR code"""
    return f"QR-{secrets.token_hex(6).upper()}"

def create_qr_image(qr_text):
    """Create QR code image and return base64 string"""
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(qr_text)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    img_buffer = io.BytesIO()
    img.save(img_buffer, format='PNG')
    img_buffer.seek(0)
    img_str = base64.b64encode(img_buffer.getvalue()).decode()
    return f"data:image/png;base64,{img_str}"

# Authentication endpoints
@app.route('/api/register', methods=['POST'])
def register():
    """Register new user"""
    try:
        data = request.json
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        role = data.get('role')
        full_name = data.get('full_name')
        phone = data.get('phone', '')
        address = data.get('address', '')

        if not all([username, email, password, role, full_name]):
            return jsonify({'error': 'Missing required fields'}), 400

        if role not in ['farmer', 'distributor', 'retailer', 'customer']:
            return jsonify({'error': 'Invalid role'}), 400

        conn = get_db_connection()

        # Check if user already exists
        existing = conn.execute('SELECT id FROM users WHERE username = ? OR email = ?', 
                               (username, email)).fetchone()
        if existing:
            return jsonify({'error': 'User already exists'}), 409

        # Create new user
        password_hash = hash_password(password)
        conn.execute('''INSERT INTO users 
                       (username, email, password_hash, role, full_name, phone, address)
                       VALUES (?, ?, ?, ?, ?, ?, ?)''',
                    (username, email, password_hash, role, full_name, phone, address))
        conn.commit()
        conn.close()

        return jsonify({'message': 'User registered successfully'}), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/login', methods=['POST'])
def login():
    """User login"""
    try:
        data = request.json
        username = data.get('username')
        password = data.get('password')

        if not all([username, password]):
            return jsonify({'error': 'Username and password required'}), 400

        conn = get_db_connection()
        user = conn.execute('''SELECT id, username, email, role, full_name 
                              FROM users WHERE username = ? AND password_hash = ?''',
                           (username, hash_password(password))).fetchone()
        conn.close()

        if not user:
            return jsonify({'error': 'Invalid credentials'}), 401

        session['user_id'] = user['id']
        session['username'] = user['username']
        session['role'] = user['role']

        return jsonify({
            'message': 'Login successful',
            'user': {
                'id': user['id'],
                'username': user['username'],
                'email': user['email'],
                'role': user['role'],
                'full_name': user['full_name']
            }
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/logout', methods=['POST'])
def logout():
    """User logout"""
    session.clear()
    return jsonify({'message': 'Logged out successfully'}), 200

# Product management endpoints
@app.route('/api/farmer/register-product', methods=['POST'])
def register_product():
    """Farmer registers new product"""
    try:
        if 'user_id' not in session or session.get('role') != 'farmer':
            return jsonify({'error': 'Authentication required'}), 401

        data = request.json
        product_name = data.get('product_name')
        quantity = data.get('quantity')
        unit = data.get('unit', 'kg')
        farmer_price = data.get('farmer_price')
        farm_location = data.get('farm_location')
        harvest_date = data.get('harvest_date')
        category = data.get('category', '')
        farming_method = data.get('farming_method', '')

        if not all([product_name, quantity, farmer_price, farm_location, harvest_date]):
            return jsonify({'error': 'Missing required fields'}), 400

        qr_code = generate_qr_code()

        conn = get_db_connection()

        # Insert product
        cursor = conn.execute('''INSERT INTO products 
                                (qr_code, product_name, category, current_stage)
                                VALUES (?, ?, ?, ?)''',
                             (qr_code, product_name, category, 'farmer'))
        product_id = cursor.lastrowid

        # Insert farmer record
        conn.execute('''INSERT INTO farmer_records 
                       (product_id, farmer_id, quantity, unit, farmer_price, 
                        farm_location, harvest_date, farming_method)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                    (product_id, session['user_id'], quantity, unit, farmer_price,
                     farm_location, harvest_date, farming_method))

        # Add to supply chain tracking
        conn.execute('''INSERT INTO supply_chain_tracking 
                       (product_id, stage, user_id, action, details)
                       VALUES (?, ?, ?, ?, ?)''',
                    (product_id, 'farmer', session['user_id'], 'Product Registered',
                     json.dumps(data)))

        conn.commit()
        conn.close()

        qr_image = create_qr_image(qr_code)

        return jsonify({
            'message': 'Product registered successfully',
            'qr_code': qr_code,
            'qr_image': qr_image,
            'product_id': product_id
        }), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/distributor/add-record', methods=['POST'])
def add_distributor_record():
    """Distributor adds record to supply chain"""
    try:
        if 'user_id' not in session or session.get('role') != 'distributor':
            return jsonify({'error': 'Authentication required'}), 401

        data = request.json
        qr_code = data.get('qr_code')
        distributor_name = data.get('distributor_name')
        storage_location = data.get('storage_location')
        distributor_margin = data.get('distributor_margin')
        transport_date = data.get('transport_date')

        if not all([qr_code, distributor_name, storage_location, distributor_margin, transport_date]):
            return jsonify({'error': 'Missing required fields'}), 400

        conn = get_db_connection()

        # Find product
        product = conn.execute('SELECT id FROM products WHERE qr_code = ?', (qr_code,)).fetchone()
        if not product:
            return jsonify({'error': 'Invalid QR code'}), 404

        product_id = product['id']

        # Insert distributor record
        conn.execute('''INSERT INTO distributor_records 
                       (product_id, distributor_id, distributor_name, storage_location,
                        distributor_margin, transport_date)
                       VALUES (?, ?, ?, ?, ?, ?)''',
                    (product_id, session['user_id'], distributor_name, storage_location,
                     distributor_margin, transport_date))

        # Update product stage
        conn.execute('UPDATE products SET current_stage = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?',
                    ('distributor', product_id))

        # Add to supply chain tracking
        conn.execute('''INSERT INTO supply_chain_tracking 
                       (product_id, stage, user_id, action, details)
                       VALUES (?, ?, ?, ?, ?)''',
                    (product_id, 'distributor', session['user_id'], 'Distributor Record Added',
                     json.dumps(data)))

        conn.commit()
        conn.close()

        return jsonify({'message': 'Distributor record added successfully'}), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/retailer/add-record', methods=['POST'])
def add_retailer_record():
    """Retailer adds record to supply chain"""
    try:
        if 'user_id' not in session or session.get('role') != 'retailer':
            return jsonify({'error': 'Authentication required'}), 401

        data = request.json
        qr_code = data.get('qr_code')
        shop_name = data.get('shop_name')
        final_price = data.get('final_price')
        retail_location = data.get('retail_location')

        if not all([qr_code, shop_name, final_price, retail_location]):
            return jsonify({'error': 'Missing required fields'}), 400

        conn = get_db_connection()

        # Find product
        product = conn.execute('SELECT id FROM products WHERE qr_code = ?', (qr_code,)).fetchone()
        if not product:
            return jsonify({'error': 'Invalid QR code'}), 404

        product_id = product['id']

        # Insert retailer record
        conn.execute('''INSERT INTO retailer_records 
                       (product_id, retailer_id, shop_name, final_price, retail_location)
                       VALUES (?, ?, ?, ?, ?)''',
                    (product_id, session['user_id'], shop_name, final_price, retail_location))

        # Update product stage
        conn.execute('UPDATE products SET current_stage = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?',
                    ('retailer', product_id))

        # Add to supply chain tracking
        conn.execute('''INSERT INTO supply_chain_tracking 
                       (product_id, stage, user_id, action, details)
                       VALUES (?, ?, ?, ?, ?)''',
                    (product_id, 'retailer', session['user_id'], 'Retailer Record Added',
                     json.dumps(data)))

        conn.commit()
        conn.close()

        return jsonify({'message': 'Retailer record added successfully'}), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/verify-product/<qr_code>', methods=['GET'])
def verify_product(qr_code):
    """Verify product and get complete supply chain information"""
    try:
        conn = get_db_connection()

        # Get product information
        product = conn.execute('SELECT * FROM products WHERE qr_code = ?', (qr_code,)).fetchone()
        if not product:
            return jsonify({'error': 'Invalid QR code'}), 404

        product_id = product['id']

        # Get farmer record
        farmer_record = conn.execute('''
            SELECT fr.*, u.full_name as farmer_name 
            FROM farmer_records fr 
            JOIN users u ON fr.farmer_id = u.id 
            WHERE fr.product_id = ?
        ''', (product_id,)).fetchone()

        # Get distributor record
        distributor_record = conn.execute('''
            SELECT dr.*, u.full_name as distributor_user_name 
            FROM distributor_records dr 
            JOIN users u ON dr.distributor_id = u.id 
            WHERE dr.product_id = ?
        ''', (product_id,)).fetchone()

        # Get retailer record
        retailer_record = conn.execute('''
            SELECT rr.*, u.full_name as retailer_user_name 
            FROM retailer_records rr 
            JOIN users u ON rr.retailer_id = u.id 
            WHERE rr.product_id = ?
        ''', (product_id,)).fetchone()

        # Get supply chain tracking
        tracking = conn.execute('''
            SELECT st.*, u.full_name as user_name 
            FROM supply_chain_tracking st 
            JOIN users u ON st.user_id = u.id 
            WHERE st.product_id = ? 
            ORDER BY st.timestamp ASC
        ''', (product_id,)).fetchall()

        conn.close()

        # Format response
        result = {
            'qr_code': qr_code,
            'product_name': product['product_name'],
            'category': product['category'],
            'current_stage': product['current_stage'],
            'farmer': dict(farmer_record) if farmer_record else None,
            'distributor': dict(distributor_record) if distributor_record else None,
            'retailer': dict(retailer_record) if retailer_record else None,
            'tracking': [dict(row) for row in tracking]
        }

        # Log customer verification
        if 'user_id' in session:
            conn = get_db_connection()
            conn.execute('''INSERT INTO customer_transactions 
                           (product_id, customer_id, verification_date)
                           VALUES (?, ?, CURRENT_TIMESTAMP)''',
                        (product_id, session['user_id']))
            conn.commit()
            conn.close()

        return jsonify(result), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/dashboard/<role>', methods=['GET'])
def get_dashboard(role):
    """Get dashboard data for specific role"""
    try:
        if 'user_id' not in session or session.get('role') != role:
            return jsonify({'error': 'Authentication required'}), 401

        conn = get_db_connection()
        user_id = session['user_id']

        if role == 'farmer':
            products = conn.execute('''
                SELECT p.*, fr.quantity, fr.farmer_price, fr.harvest_date
                FROM products p 
                JOIN farmer_records fr ON p.id = fr.product_id
                WHERE fr.farmer_id = ?
                ORDER BY p.created_at DESC
            ''', (user_id,)).fetchall()

        elif role == 'distributor':
            products = conn.execute('''
                SELECT p.*, dr.distributor_name, dr.transport_date, dr.storage_location
                FROM products p 
                JOIN distributor_records dr ON p.id = dr.product_id
                WHERE dr.distributor_id = ?
                ORDER BY dr.created_at DESC
            ''', (user_id,)).fetchall()

        elif role == 'retailer':
            products = conn.execute('''
                SELECT p.*, rr.shop_name, rr.final_price, rr.retail_location
                FROM products p 
                JOIN retailer_records rr ON p.id = rr.product_id
                WHERE rr.retailer_id = ?
                ORDER BY rr.created_at DESC
            ''', (user_id,)).fetchall()

        else:
            products = []

        conn.close()

        return jsonify({
            'products': [dict(row) for row in products]
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Health check endpoint
@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'message': 'KrishiChain API is running'}), 200

def create_app():
    """Application factory function"""
    if not os.path.exists(DATABASE):
        init_database()
        print("Database initialized!")
    return app

if __name__ == '__main__':
    print("Starting KrishiChain Backend API...")
    print("API Documentation:")
    print("- POST /api/register - Register new user")
    print("- POST /api/login - User login")
    print("- POST /api/logout - User logout")
    print("- POST /api/farmer/register-product - Register product")
    print("- POST /api/distributor/add-record - Add distributor record")
    print("- POST /api/retailer/add-record - Add retailer record")
    print("- GET /api/verify-product/<qr_code> - Verify product")
    print("- GET /api/dashboard/<role> - Get dashboard data")
    print("- GET /api/health - Health check")
    
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') != 'production'
    app.run(host='0.0.0.0', port=port, debug=debug)

# Initialize database when module loads
if not os.path.exists(DATABASE):
    init_database()
    print("Database initialized!")
    
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

