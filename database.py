import os
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient
import asyncio
from models import User, Exam, Result, Question, Option, ExamAnswer, ExamResult

# MongoDB connection settings
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost/?directConnection=true&serverSelectionTimeoutMS=200")
DATABASE_NAME = "student_submissions"

# Async MongoDB client for FastAPI
client = AsyncIOMotorClient(MONGODB_URL)
database = client[DATABASE_NAME]

# Collections
users_collection = database.get_collection("users")
exams_collection = database.get_collection("exams")
results_collection = database.get_collection("results")


async def create_sample_data():
    """Create sample data for testing"""
    
    # Clear existing data
    await users_collection.delete_many({})
    await exams_collection.delete_many({})
    await results_collection.delete_many({})
    
    # Sample exams
    sample_exams = [
        {
            "exam_name": "Python Basics",
            "questions": [
                {
                    "question_id": "q1",
                    "question_description": "What is the correct way to create a list in Python?",
                    "options": [
                        {"option_id": "a", "option_description": "list = []"},
                        {"option_id": "b", "option_description": "list = {}"},
                        {"option_id": "c", "option_description": "list = ()"},
                        {"option_id": "d", "option_description": "list = <>"}
                    ],
                    "correct_option": "a"
                },
                {
                    "question_id": "q2",
                    "question_description": "Which keyword is used to define a function in Python?",
                    "options": [
                        {"option_id": "a", "option_description": "function"},
                        {"option_id": "b", "option_description": "def"},
                        {"option_id": "c", "option_description": "func"},
                        {"option_id": "d", "option_description": "define"}
                    ],
                    "correct_option": "b"
                }
            ]
        },
        {
            "exam_name": "JavaScript Fundamentals",
            "questions": [
                {
                    "question_id": "q1",
                    "question_description": "How do you declare a variable in JavaScript?",
                    "options": [
                        {"option_id": "a", "option_description": "var myVar;"},
                        {"option_id": "b", "option_description": "variable myVar;"},
                        {"option_id": "c", "option_description": "v myVar;"},
                        {"option_id": "d", "option_description": "declare myVar;"}
                    ],
                    "correct_option": "a"
                },
                {
                    "question_id": "q2",
                    "question_description": "What does '===' operator do in JavaScript?",
                    "options": [
                        {"option_id": "a", "option_description": "Assigns a value"},
                        {"option_id": "b", "option_description": "Compares values only"},
                        {"option_id": "c", "option_description": "Compares values and types"},
                        {"option_id": "d", "option_description": "Creates a new variable"}
                    ],
                    "correct_option": "c"
                }
            ]
        }
    ]
    
    # Insert sample exams
    await exams_collection.insert_many(sample_exams)
    
    # Sample users with pre-hashed passwords (these would come from frontend)
    sample_users = [
        {
            "user_id": "user001",
            "user_name": "John Doe",
            "hashed_password": "5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8",  # sha256 hash of "password123"
            "exams_enrolled": ["Python Basics", "JavaScript Fundamentals"],
            "exam_answers": [
                {
                    "exam_name": "Python Basics",
                    "answers": ["a", "b"]
                }
            ],
            "is_active": True
        },
        {
            "user_id": "user002",
            "user_name": "Jane Smith",
            "hashed_password": "8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92",  # sha256 hash of "jane456"
            "exams_enrolled": ["Python Basics"],
            "exam_answers": [],
            "is_active": True
        },
        {
            "user_id": "user003",
            "user_name": "Bob Johnson",
            "hashed_password": "481f6cc0511143ccdd7e2d1b1b94faf0a700a8b49cd13922a70b5ae28acaa8c5",  # sha256 hash of "bob789"
            "exams_enrolled": ["JavaScript Fundamentals"],
            "exam_answers": [
                {
                    "exam_name": "JavaScript Fundamentals",
                    "answers": ["a", "c"]
                }
            ],
            "is_active": True
        }
    ]
    
    # Insert sample users
    await users_collection.insert_many(sample_users)
    
    # Sample results
    sample_results = [
        {
            "user_id": "user001",
            "exam_results": [
                {
                    "exam_name": "Python Basics",
                    "exam_result": "100% - Excellent"
                }
            ]
        },
        {
            "user_id": "user003",
            "exam_results": [
                {
                    "exam_name": "JavaScript Fundamentals",
                    "exam_result": "100% - Excellent"
                }
            ]
        }
    ]
    
    # Insert sample results
    await results_collection.insert_many(sample_results)
    
    print("Sample data created successfully!")


def init_mongodb():
    """Initialize MongoDB connection and create sample data"""
    try:
        # Test connection
        sync_client = MongoClient(MONGODB_URL)
        sync_client.admin.command('ping')
        print("MongoDB connection successful!")
        sync_client.close()
        
        # Create sample data
        asyncio.run(create_sample_data())
        
    except Exception as e:
        print(f"MongoDB connection failed: {e}")
        print("Please make sure MongoDB is running on localhost:27017")
        print("To install MongoDB:")
        print("1. macOS: brew install mongodb-community")
        print("2. Ubuntu: sudo apt install mongodb")
        print("3. Windows: Download from https://www.mongodb.com/try/download/community")


if __name__ == "__main__":
    init_mongodb()
