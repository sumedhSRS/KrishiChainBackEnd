
import sqlite3
import hashlib
import json
from datetime import datetime, date

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def insert_sample_data():
    conn = sqlite3.connect('krishichain.db')

    # Sample users
    users = [
        ('farmer1', 'farmer1@krishichain.com', hash_password('password123'), 'farmer', 'राजेश कुमार', '9876543210', 'Village Khetpura, Punjab'),
        ('distributor1', 'dist1@krishichain.com', hash_password('password123'), 'distributor', 'सुनील गुप्ता', '9876543211', 'Delhi Warehouse, Delhi'),
        ('retailer1', 'retail1@krishichain.com', hash_password('password123'), 'retailer', 'प्रिया शर्मा', '9876543212', 'Fresh Mart, Mumbai'),
        ('customer1', 'customer1@krishichain.com', hash_password('password123'), 'customer', 'अमित वर्मा', '9876543213', 'Andheri, Mumbai')
    ]

    for user in users:
        try:
            conn.execute('''INSERT INTO users 
                           (username, email, password_hash, role, full_name, phone, address)
                           VALUES (?, ?, ?, ?, ?, ?, ?)''', user)
        except sqlite3.IntegrityError:
            print(f"User {user[0]} already exists")

    # Sample products with complete supply chain
    sample_products = [
        {
            'qr_code': 'QR-RICE001',
            'product_name': 'Basmati Rice',
            'category': 'Grains',
            'current_stage': 'customer',
            'farmer': {
                'farmer_id': 1,
                'quantity': '100',
                'unit': 'kg',
                'farmer_price': 80.00,
                'farm_location': 'Village Khetpura, Punjab',
                'harvest_date': '2025-09-15',
                'farming_method': 'Organic'
            },
            'distributor': {
                'distributor_id': 2,
                'distributor_name': 'Punjab Grains Ltd',
                'storage_location': 'Delhi Warehouse',
                'distributor_margin': 15.00,
                'transport_date': '2025-09-17',
                'transport_method': 'Refrigerated Truck'
            },
            'retailer': {
                'retailer_id': 3,
                'shop_name': 'Fresh Mart',
                'final_price': 120.00,
                'retail_location': 'Mumbai Central',
                'display_date': '2025-09-20'
            }
        },
        {
            'qr_code': 'QR-WHEAT002',
            'product_name': 'Wheat',
            'category': 'Grains',
            'current_stage': 'retailer',
            'farmer': {
                'farmer_id': 1,
                'quantity': '200',
                'unit': 'kg',
                'farmer_price': 25.00,
                'farm_location': 'Village Khetpura, Punjab',
                'harvest_date': '2025-09-10',
                'farming_method': 'Traditional'
            },
            'distributor': {
                'distributor_id': 2,
                'distributor_name': 'Haryana Distributors',
                'storage_location': 'Gurgaon Hub',
                'distributor_margin': 8.00,
                'transport_date': '2025-09-12',
                'transport_method': 'Standard Truck'
            }
        }
    ]

    for product_data in sample_products:
        # Insert product
        cursor = conn.execute('''INSERT OR REPLACE INTO products 
                                (qr_code, product_name, category, current_stage)
                                VALUES (?, ?, ?, ?)''',
                             (product_data['qr_code'], product_data['product_name'], 
                              product_data['category'], product_data['current_stage']))
        product_id = cursor.lastrowid

        # Insert farmer record
        farmer = product_data['farmer']
        conn.execute('''INSERT OR REPLACE INTO farmer_records 
                       (product_id, farmer_id, quantity, unit, farmer_price, 
                        farm_location, harvest_date, farming_method)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                    (product_id, farmer['farmer_id'], farmer['quantity'], farmer['unit'],
                     farmer['farmer_price'], farmer['farm_location'], farmer['harvest_date'],
                     farmer['farming_method']))

        # Insert distributor record if exists
        if 'distributor' in product_data:
            distributor = product_data['distributor']
            conn.execute('''INSERT OR REPLACE INTO distributor_records 
                           (product_id, distributor_id, distributor_name, storage_location,
                            distributor_margin, transport_date, transport_method)
                           VALUES (?, ?, ?, ?, ?, ?, ?)''',
                        (product_id, distributor['distributor_id'], distributor['distributor_name'],
                         distributor['storage_location'], distributor['distributor_margin'],
                         distributor['transport_date'], distributor['transport_method']))

        # Insert retailer record if exists
        if 'retailer' in product_data:
            retailer = product_data['retailer']
            conn.execute('''INSERT OR REPLACE INTO retailer_records 
                           (product_id, retailer_id, shop_name, final_price, retail_location, display_date)
                           VALUES (?, ?, ?, ?, ?, ?)''',
                        (product_id, retailer['retailer_id'], retailer['shop_name'],
                         retailer['final_price'], retailer['retail_location'], retailer['display_date']))

    conn.commit()
    conn.close()
    print("✅ Sample data inserted successfully!")
    print("\n👥 Sample Users Created:")
    print("- Username: farmer1, Password: password123 (Farmer)")
    print("- Username: distributor1, Password: password123 (Distributor)")
    print("- Username: retailer1, Password: password123 (Retailer)")
    print("- Username: customer1, Password: password123 (Customer)")
    print("\n📦 Sample Products Created:")
    print("- QR-RICE001: Basmati Rice (Complete supply chain)")
    print("- QR-WHEAT002: Wheat (Farmer + Distributor stages)")

if __name__ == '__main__':
    insert_sample_data()
