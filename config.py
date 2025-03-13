from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/job_dashboard")
client = MongoClient(MONGO_URI)
db = client["job_dashboard"]  # Database Name

# Collections
users_collection = db["users"]
jobs_collection = db["jobs"]
applications_collection = db["applications"]

# Test connection
try:
    # The ping command is cheap and does not require auth.
    client.admin.command('ping')
    print("Connected to MongoDB successfully!")
except Exception as e:
    print(f"Error connecting to MongoDB: {e}")
