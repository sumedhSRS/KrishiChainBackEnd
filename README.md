# KrishiChain - Agriculture Supply Chain Management System

## 📋 Project Overview
KrishiChain is a blockchain-inspired agricultural supply chain management system that tracks products from farm to consumer using QR codes and a relational database backend.

## 🏗️ Architecture
- **Frontend**: HTML, CSS, JavaScript (Single Page Application)
- **Backend**: Flask (Python) REST API
- **Database**: SQLite (RDBMS)
- **Authentication**: Session-based with password hashing
- **QR Codes**: Generated dynamically for product tracking

## 📁 Project Structure
```
krishichain/
├── frontend/
│   ├── index.html              # Main UI with all pages
│   ├── style.css               # Styling for the application
│   ├── app.js                  # Original frontend-only logic
│   ├── app_backend_integrated.js # Backend-integrated version
│   └── logo.jpg                # Project logo
├── backend/
│   ├── backend_app.py          # Flask API server
│   ├── krishichain_schema.sql  # Database schema
│   ├── insert_sample_data.py   # Sample data insertion script
│   └── requirements.txt        # Python dependencies
└── README.md
```

## 🚀 Setup Instructions

### 1. Prerequisites
- Python 3.7+
- pip (Python package manager)
- Modern web browser

### 2. Backend Setup
```bash
# Install Python dependencies
pip install -r requirements.txt

# Start the Flask server
python backend_app.py
```
The API will be available at `http://localhost:5000`

### 3. Database Setup
The database is automatically created when you first run `backend_app.py`.

To populate with sample data:
```bash
python insert_sample_data.py
```

### 4. Frontend Setup
1. Update `index.html` to use `app_backend_integrated.js` instead of `app.js`
2. Serve the frontend files using a local server:
   ```bash
   # Using Python's built-in server
   python -m http.server 8000
   ```
3. Open `http://localhost:8000` in your browser

## 🔐 Sample Users
After running the sample data script, you can use these test accounts:

| Role | Username | Password | Description |
|------|----------|----------|-------------|
| Farmer | farmer1 | password123 | The Farmer |
| Distributor | distributor1 | password123 | The Distributor |
| Retailer | retailer1 | password123 | The Retailer |
| Customer | customer1 | password123 | The Customer |

## 🛠️ API Endpoints

### Authentication
- `POST /api/register` - Register new user
- `POST /api/login` - User login
- `POST /api/logout` - User logout

### Product Management
- `POST /api/farmer/register-product` - Register new product
- `POST /api/distributor/add-record` - Add distributor information
- `POST /api/retailer/add-record` - Add retailer information
- `GET /api/verify-product/<qr_code>` - Verify product and get supply chain

### Dashboard
- `GET /api/dashboard/<role>` - Get role-specific dashboard data
- `GET /api/health` - API health check

## 📊 Database Schema

### Core Tables
1. **users** - User authentication and profiles
2. **products** - Basic product information
3. **farmer_records** - Farmer-specific data
4. **distributor_records** - Distribution information
5. **retailer_records** - Retail information
6. **customer_transactions** - Customer interactions
7. **supply_chain_tracking** - Complete audit trail

## 🔄 Supply Chain Flow
1. **Farmer** registers produce → Gets QR code
2. **Distributor** scans farmer QR → Adds distribution data
3. **Retailer** scans distributor QR → Sets final price
4. **Customer** verifies product → Views complete journey

## 🎯 Key Features
- ✅ Complete supply chain tracking
- ✅ QR code generation and verification
- ✅ Role-based access control
- ✅ Real-time data persistence
- ✅ Bilingual support (English/Hindi)
- ✅ Responsive design
- ✅ RESTful API architecture

## 🔧 Development Features
- Session-based authentication
- Password hashing with SHA256
- CORS enabled for frontend-backend communication
- Error handling and validation
- Sample data for testing
- API documentation

## 🚦 Deployment
For production deployment:
1. Use a production WSGI server (e.g., Gunicorn)
2. Configure a reverse proxy (e.g., Nginx)
3. Use a production database (PostgreSQL/MySQL)
4. Set up proper SSL certificates
5. Configure environment variables

## 🤝 Contributing
This project is designed for hackathons and educational purposes. Key areas for enhancement:
- Blockchain integration
- Mobile app development
- Advanced analytics dashboard
- IoT sensor integration
- Multi-language support

## 📝 License
Open source - designed for educational and hackathon use.
