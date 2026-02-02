import os
from dotenv import load_dotenv

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "transdom")
SECRET_KEY = os.getenv("SECRET_KEY", "change-me-in-prod")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
# minutes
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

# Insurance configuration
# Insurance rate as a percentage of shipment value (default: 2%)
INSURANCE_RATE = float(os.getenv("INSURANCE_RATE", "0.02"))
MINIMUM_INSURANCE_FEE = float(os.getenv("MINIMUM_INSURANCE_FEE", "500"))  # Minimum insurance fee in NGN
