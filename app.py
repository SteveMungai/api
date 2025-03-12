from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from config import users_collection, jobs_collection
from bson.objectid import ObjectId

app = Flask(__name__)
CORS(app)  # Enable CORS
bcrypt = Bcrypt(app)  # Enable password hashing

#register a new user
@app.post("/register")
def register_user():
    data = request.json
    email = data.get("email")
    password = data.get("password")

    if users_collection.find_one({"email": email}):
        return jsonify({"error": "User already exists"}), 400

    hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")
    user = {
        "name": data.get("name"),
        "email": email,
        "password": hashed_password,
        "saved_jobs": []
    }
    
    users_collection.insert_one(user)
    return jsonify({"message": "User registered successfully"}), 201

#authenticate a user
@app.post("/login")
def login_user():
    data = request.json
    email = data.get("email")
    password = data.get("password")

    user = users_collection.find_one({"email": email})
    if not user or not bcrypt.check_password_hash(user["password"], password):
        return jsonify({"error": "Invalid email or password"}), 401

    return jsonify({"message": "Login successful", "user_id": str(user["_id"])}), 200

#fetch all jobs
@app.get("/jobs")
def get_jobs():
    jobs = list(jobs_collection.find({}, {"_id": 0}))  # Exclude MongoDB `_id`
    return jsonify(jobs)

#save a job
@app.post("/users/<user_id>/save_job/<job_id>")
def save_job(user_id, job_id):
    user = users_collection.find_one({"_id": ObjectId(user_id)})
    job = jobs_collection.find_one({"_id": ObjectId(job_id)})

    if not user or not job:
        return jsonify({"error": "User or Job not found"}), 404

    users_collection.update_one(
        {"_id": ObjectId(user_id)},
        {"$addToSet": {"saved_jobs": job_id}}  # Prevent duplicate saves
    )
    return jsonify({"message": "Job saved successfully"}), 200

#get a user's saved jobs
@app.get("/users/<user_id>/saved_jobs")
def get_saved_jobs(user_id):
    user = users_collection.find_one({"_id": ObjectId(user_id)})
    if not user:
        return jsonify({"error": "User not found"}), 404

    job_ids = user.get("saved_jobs", [])
    saved_jobs = list(jobs_collection.find({"_id": {"$in": [ObjectId(j) for j in job_ids]}}, {"_id": 0}))

    return jsonify(saved_jobs)

#delete users
@app.delete("/users/<user_id>/saved_jobs/<job_id>")
def delete_saved_job(user_id, job_id):
    result = users_collection.update_one(
        {"_id": ObjectId(user_id)},
        {"$pull": {"saved_jobs": ObjectId(job_id)}}
    )
    
    if result.modified_count == 0:
        return jsonify({"error": "Job not found or not saved"}), 404

    return jsonify({"message": "Job deleted successfully"}), 200