# Transdom Shipping Rates API

A high-performance FastAPI REST API for managing and querying international shipping rates. Features async MongoDB integration, API key authentication, and real-time rate lookups across 8 global zones.

## 🚀 Features

- **⚡ High Performance**: Async FastAPI with Motor (async MongoDB driver) for non-blocking operations
- **🔐 API Key Authentication**: Protect routes with simple header-based authentication
- **🌍 Global Coverage**: 8 shipping zones with 69 weight-based rates each (552 total entries)
- **💰 Formatted Prices**: All prices returned with comma-separated format (e.g., `1,234.56`)
- **📊 Flexible Querying**: Filter by zone, lookup specific prices, or get all rates
- **➕ Easy Management**: Add or update shipping rates via REST endpoint
- **� Email Notifications**: Automated emails via Zoho for signup, orders, and approvals
- **�📚 Interactive Docs**: Built-in Swagger UI and ReDoc documentation
- **☁️ Cloud Ready**: Optimized for Vercel serverless deployment

## 📋 API Endpoints

All endpoints require `X-API-Key` header for authentication. See [API_AUTHENTICATION.md](API_AUTHENTICATION.md) for details.

### GET `/api/rates`

Retrieve all shipping rates or filter by zone.

**Headers:**

```
X-API-Key: your-api-key
```

**Query Parameters:**

- `zone` (optional): Filter by specific zone (e.g., `UK_IRELAND`, `USA_CANADA`)

**Example:**

```bash
# Get all rates
curl -H "X-API-Key: transdom-api-key-2026" http://localhost:8000/api/rates

# Get rates for specific zone
curl -H "X-API-Key: transdom-api-key-2026" http://localhost:8000/api/rates?zone=UK_IRELAND
```

**Response:**

```json
[
  {
    "_id": "6979050a0ebb6fe749b86366",
    "zone": "UK_IRELAND",
    "currency": "NGN",
    "unit": "kg",
    "rates": [
      {"weight": 2, "price": "85,378.48"},
      {"weight": 3, "price": "102,410.07"},
      ...
    ]
  }
]
```

### POST `/api/add-rates`

Add a new shipping rate card or update an existing one.

**Headers:**

```
X-API-Key: your-api-key
Content-Type: application/json
```

**Request Body:**

```json
{
  "zone": "UK_IRELAND",
  "currency": "NGN",
  "unit": "kg",
  "rates": [
    { "weight": 2, "price": 85378.48 },
    { "weight": 3, "price": 102410.07 },
    { "weight": 4, "price": 126375.73 }
  ]
}
```

**Response:** Returns the inserted/updated document (same format as GET /api/rates)

### GET `/api/rates/{zone}/price`

Lookup the price for a specific weight in a zone.

**Headers:**

```
X-API-Key: your-api-key
```

**Path Parameters:**

- `zone`: Destination zone (e.g., `UK_IRELAND`)

**Query Parameters:**

- `weight`: Weight in kg

**Example:**

```bash
curl -H "X-API-Key: transdom-api-key-2026" http://localhost:8000/api/rates/UK_IRELAND/price?weight=5
```

**Response:**

```json
{
  "zone": "UK_IRELAND",
  "weight": 5,
  "price": "135,341.42",
  "currency": "NGN"
}
```

### POST `/api/calculate-insurance`

Calculate insurance fee for a shipment based on its declared value.

**Headers:**

```
Content-Type: application/json
```

**Request Body:**

```json
{
  "shipment_value": 50000
}
```

**Response:**

```json
{
  "shipment_value": 50000,
  "insurance_fee": 5000,
  "insurance_rate": 0.02,
  "minimum_fee": 500,
  "currency": "NGN"
}
```

**Insurance Tiers:**
- ₦0 to ₦100,000: ₦5,000
- ₦101,000 to ₦200,000: ₦7,500
- ₦200,001 to ₦500,000: ₦10,000
- ₦500,001 to ₦1,000,000: ₦20,000
- ₦1,000,001 to ₦2,000,000: ₦30,000
- ₦2,000,001 to ₦5,000,000: ₦120,000
- ₦5,000,001 to ₦10,000,000: ₦240,000

### GET `/`

Health check endpoint (no authentication required).

**Response:**

```json
{
  "status": "ok",
  "message": "Transdom API is running"
}
```

## 🔐 Authentication

This API uses **API Key authentication**. All protected endpoints require an `X-API-Key` header.

**Your API Key:** `transdom-api-key-2026`

**Usage Example:**

```bash
curl -H "X-API-Key: transdom-api-key-2026" http://localhost:8000/api/rates
```

For detailed authentication examples in JavaScript, React, Python, and more, see [API_AUTHENTICATION.md](API_AUTHENTICATION.md).

**Error Responses:**

```json
// Missing API Key (403)
{"detail": "API key required in X-API-Key header"}

// Invalid API Key (401)
{"detail": "Invalid API key"}
```

## 📦 Installation

### Prerequisites

- Python 3.11+
- MongoDB (local or Atlas)
- pip

### Setup

1. **Clone the repository**

```bash
git clone <repository-url>
cd transdom
```

2. **Create virtual environment**

```bash
python3.11 -m venv venv
source venv/bin/activate
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

4. **Configure environment**

Create a `.env` file in the root directory:

```env
# MongoDB connection string
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority
DB_NAME=transdom

# API Key for protecting routes
API_KEY=transdom-api-key-2026
```

**Note:** `.env` is not committed to Git. See `.env.example` for template.

## 🏃 Running Locally

```bash
# Activate virtual environment
source venv/bin/activate

# Start the API server
uvicorn main:app --reload

# Server will be available at http://localhost:8000
```

### API Documentation

Once the server is running, interactive API documentation is available at:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🗂️ Project Structure

```
transdom/
├── main.py              # FastAPI app initialization with lifecycle management
├── config.py            # Environment configuration loader
├── database.py          # MongoDB async connection (Motor)
├── models.py            # Pydantic data validation models
├── routes.py            # API endpoints with authentication
├── utils.py             # Utility functions (format_price, etc)
├── auth.py              # API key authentication logic
├── api/
│   └── index.py         # Vercel serverless entry point
├── requirements.txt     # Python dependencies
├── .env                 # Local environment variables (not in Git)
├── .env.example         # Environment template
├── .gitignore           # Git ignore rules
├── vercel.json          # Vercel deployment config
├── README.md            # This file
├── API_AUTHENTICATION.md # Detailed auth examples
├── DEPLOYMENT.md        # Vercel deployment guide
├── QUICKSTART.md        # Quick reference
└── venv/                # Python virtual environment
```

## 🔧 Configuration

### Environment Variables

Create `.env` file with:

| Variable                | Required | Description                         | Example                              |
| ----------------------- | -------- | ----------------------------------- | ------------------------------------ |
| `MONGODB_URI`           | Yes      | MongoDB connection string           | `mongodb+srv://user:pass@cluster...` |
| `DB_NAME`               | Yes      | Database name                       | `transdom`                           |
| `API_KEY`               | Yes      | API key for authentication          | `transdom-api-key-2026`              |
| `INSURANCE_RATE`        | No       | Insurance rate as decimal (default: 0.02 = 2%) | `0.02`                    |
| `MINIMUM_INSURANCE_FEE` | No       | Minimum insurance fee in NGN (default: 500)    | `500`                     |

### MongoDB Connection

The API uses **Motor** (async MongoDB driver) for non-blocking database operations:

- Connection established on app startup
- Closed gracefully on app shutdown
- Connection pooling for performance
- Compatible with MongoDB Atlas and local MongoDB

## 📊 Data Schema

Shipping rates are stored in MongoDB as documents with the following structure:

```json
{
  "_id": ObjectId,
  "zone": "UK_IRELAND",
  "currency": "NGN",
  "unit": "kg",
  "rates": [
    {"weight": 2, "price": 85378.48},
    {"weight": 3, "price": 102410.07},
    {"weight": 4, "price": 126375.73},
    ...
  ]
}
```

## 🌍 Available Zones

- `UK_IRELAND` - United Kingdom & Ireland
- `WEST_CENTRAAFRICA` - West & Central Africa
- `USA_CANADA` - United States & Canada
- `EUROPE` - European Countries
- `EAST_SOUTHAFRICA` - East & Southern Africa
- `MIDDLEEAST` - Middle East
- `ASIA` - Asian Countries
- `SOUTHAMERICA` - South American Countries

## 🚀 Deployment

### Vercel Deployment

The API is optimized for Vercel serverless deployment. See [DEPLOYMENT.md](DEPLOYMENT.md) for step-by-step instructions.

**Quick Summary:**

1. Push to GitHub
2. Connect repository to Vercel
3. Set environment variables (`MONGODB_URI`, `DB_NAME`, `API_KEY`)
4. Deploy automatically on git push

**Your API will be live at:** `https://<project>.vercel.app`

**Example API Calls:**

```bash
# Get all rates
curl -H "X-API-Key: transdom-api-key-2026" \
  https://<project>.vercel.app/api/rates

# Get specific zone
curl -H "X-API-Key: transdom-api-key-2026" \
  https://<project>.vercel.app/api/rates?zone=UK_IRELAND

# Lookup price
curl -H "X-API-Key: transdom-api-key-2026" \
  https://<project>.vercel.app/api/rates/UK_IRELAND/price?weight=5
```

## 💾 Dependencies

**Core Framework:**

- `fastapi` - Modern web framework
- `uvicorn` - ASGI server with uvloop support

**Database:**

- `motor` - Async MongoDB driver
- `pymongo` - MongoDB Python driver

**Validation & Configuration:**

- `pydantic` - Data validation and serialization
- `python-dotenv` - Environment variable management

**Complete List:** See `requirements.txt`

## 🔒 Error Handling

The API includes comprehensive error handling:

| Status | Scenario        | Response                            |
| ------ | --------------- | ----------------------------------- |
| 200    | Success         | JSON data                           |
| 201    | Created         | Created document                    |
| 400    | Invalid request | `{"detail": "..."}`                 |
| 401    | Invalid API key | `{"detail": "Invalid API key"}`     |
| 403    | Missing API key | `{"detail": "API key required..."}` |
| 404    | Not found       | `{"detail": "No rates found"}`      |
| 500    | Server error    | `{"detail": "Error..."}`            |

## 📝 Examples

### Using cURL

```bash
# Get all rates
curl -H "X-API-Key: transdom-api-key-2026" http://localhost:8000/api/rates

# Get UK_IRELAND rates
curl -H "X-API-Key: transdom-api-key-2026" http://localhost:8000/api/rates?zone=UK_IRELAND

# Lookup 5kg price to UK_IRELAND
curl -H "X-API-Key: transdom-api-key-2026" http://localhost:8000/api/rates/UK_IRELAND/price?weight=5

# Add new zone
curl -X POST http://localhost:8000/api/add-rates \
  -H "X-API-Key: transdom-api-key-2026" \
  -H "Content-Type: application/json" \
  -d '{
    "zone": "AUSTRALIA",
    "currency": "NGN",
    "unit": "kg",
    "rates": [
      {"weight": 2, "price": 120000},
      {"weight": 3, "price": 150000}
    ]
  }'
```

### Using JavaScript/Fetch

```javascript
const API_KEY = "transdom-api-key-2026";
const API_URL = "http://localhost:8000";

// Get all rates
const rates = await fetch(`${API_URL}/api/rates`, {
  headers: { "X-API-Key": API_KEY },
}).then((r) => r.json());

// Get specific price
const price = await fetch(`${API_URL}/api/rates/UK_IRELAND/price?weight=5`, {
  headers: { "X-API-Key": API_KEY },
}).then((r) => r.json());

console.log(price);
// { zone: "UK_IRELAND", weight: 5, price: "135,341.42", currency: "NGN" }
```

### Using Python

```python
import requests

API_KEY = "transdom-api-key-2026"
BASE_URL = "http://localhost:8000"

# Get all rates
response = requests.get(
    f"{BASE_URL}/api/rates",
    headers={"X-API-Key": API_KEY}
)
rates = response.json()

# Get specific zone
response = requests.get(
    f"{BASE_URL}/api/rates",
    params={"zone": "UK_IRELAND"},
    headers={"X-API-Key": API_KEY}
)
uk_rates = response.json()

# Lookup price
response = requests.get(
    f"{BASE_URL}/api/rates/UK_IRELAND/price",
    params={"weight": 5},
    headers={"X-API-Key": API_KEY}
)
price_info = response.json()
```

**For more examples, see [API_AUTHENTICATION.md](API_AUTHENTICATION.md)**

## 🐛 Troubleshooting

### API Key Issues

- Verify `X-API-Key` header is present in request
- Check API key matches `API_KEY` in `.env`
- Ensure header name is exactly `X-API-Key` (case-sensitive)

### MongoDB Connection Failed

- Ensure MongoDB is running (local) or accessible (Atlas)
- Verify `MONGODB_URI` in `.env` is correct
- Check network connectivity and firewall rules
- Verify MongoDB user credentials

### Port Already in Use

```bash
# Use a different port
uvicorn main:app --port 8001
```

### Import Error

- Verify all dependencies: `pip install -r requirements.txt`
- Ensure Python 3.11+ is being used
- Check that `.env` file exists with correct configuration

### Database Connection Timeout

- MongoDB Atlas: Allow access from `0.0.0.0/0` in Network Access
- Local MongoDB: Ensure MongoDB service is running
- Check connection string includes database name

### 404 Not Found

- Verify zone name is correct (case-insensitive in queries)
- Check weight parameter is provided for price lookup
- Ensure zone exists in database

## 📚 Documentation

- **[API_AUTHENTICATION.md](API_AUTHENTICATION.md)** - Detailed authentication guide with examples in multiple languages
- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Vercel deployment step-by-step guide
- **[QUICKSTART.md](QUICKSTART.md)** - Quick reference for local development
- **[CHECKLIST.md](CHECKLIST.md)** - Pre-deployment verification checklist

## 📄 License

[Add your license here]

## 👥 Contributors

[Add contributors here]

---

**Last Updated:** January 27, 2026  
**Version:** 1.0.0  
**API Status:** Production Ready ✓
