
-- KrishiChain Database Schema
-- Users table for authentication
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('farmer', 'distributor', 'retailer', 'customer') NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    phone VARCHAR(20),
    address TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Products table for basic product information
CREATE TABLE products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    qr_code VARCHAR(50) UNIQUE NOT NULL,
    product_name VARCHAR(255) NOT NULL,
    category VARCHAR(100),
    description TEXT,
    current_stage ENUM('farmer', 'distributor', 'retailer', 'customer') DEFAULT 'farmer',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Farmer records table
CREATE TABLE farmer_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER NOT NULL,
    farmer_id INTEGER NOT NULL,
    quantity VARCHAR(50) NOT NULL,
    unit VARCHAR(20) NOT NULL,
    farmer_price DECIMAL(10,2) NOT NULL,
    farm_location VARCHAR(255) NOT NULL,
    harvest_date DATE NOT NULL,
    farming_method VARCHAR(100),
    pesticides_used TEXT,
    certification VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(id),
    FOREIGN KEY (farmer_id) REFERENCES users(id)
);

-- Distributor records table
CREATE TABLE distributor_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER NOT NULL,
    distributor_id INTEGER NOT NULL,
    distributor_name VARCHAR(255) NOT NULL,
    storage_location VARCHAR(255) NOT NULL,
    distributor_margin DECIMAL(10,2) NOT NULL,
    transport_date DATE NOT NULL,
    transport_method VARCHAR(100),
    storage_temperature VARCHAR(50),
    quality_check_status VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(id),
    FOREIGN KEY (distributor_id) REFERENCES users(id)
);

-- Retailer records table
CREATE TABLE retailer_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER NOT NULL,
    retailer_id INTEGER NOT NULL,
    shop_name VARCHAR(255) NOT NULL,
    final_price DECIMAL(10,2) NOT NULL,
    retail_location VARCHAR(255) NOT NULL,
    expiry_date DATE,
    storage_conditions VARCHAR(100),
    display_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(id),
    FOREIGN KEY (retailer_id) REFERENCES users(id)
);

-- Customer transactions table
CREATE TABLE customer_transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER NOT NULL,
    customer_id INTEGER,
    verification_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    purchase_status ENUM('verified', 'purchased') DEFAULT 'verified',
    feedback_rating INTEGER CHECK(feedback_rating >= 1 AND feedback_rating <= 5),
    feedback_comment TEXT,
    FOREIGN KEY (product_id) REFERENCES products(id),
    FOREIGN KEY (customer_id) REFERENCES users(id)
);

-- Supply chain tracking table
CREATE TABLE supply_chain_tracking (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER NOT NULL,
    stage VARCHAR(50) NOT NULL,
    user_id INTEGER NOT NULL,
    action VARCHAR(100) NOT NULL,
    details JSON,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(id),
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Indexes for better performance
CREATE INDEX idx_products_qr_code ON products(qr_code);
CREATE INDEX idx_products_stage ON products(current_stage);
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_supply_chain_product ON supply_chain_tracking(product_id);
CREATE INDEX idx_supply_chain_stage ON supply_chain_tracking(stage);
