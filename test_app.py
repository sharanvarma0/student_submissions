#!/usr/bin/env python3
"""
Test script for the Student Submissions API
This script tests the application without requiring MongoDB to be running
"""

import asyncio
import json
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_without_mongodb():
    """Test the application structure without MongoDB"""
    print("🧪 Testing Student Submissions API structure...")
    
    try:
        # Import models
        from models import User, Exam, Result, UserCreate, ExamCreate
        print("✅ Models imported successfully")
        
        # Test model creation
        user_create = UserCreate(
            user_id="test001",
            user_name="Test User",
            exams_enrolled=["Test Exam"]
        )
        print("✅ UserCreate model works")
        
        exam_create = ExamCreate(
            exam_name="Test Exam",
            questions=[
                {
                    "question_id": "q1",
                    "question_description": "Test question?",
                    "options": [
                        {"option_id": "a", "option_description": "Option A"},
                        {"option_id": "b", "option_description": "Option B"}
                    ],
                    "correct_option": "a"
                }
            ]
        )
        print("✅ ExamCreate model works")
        
        print("\n📋 Model validation successful!")
        
    except Exception as e:
        print(f"❌ Model test failed: {e}")
        return False
    
    return True


def test_api_structure():
    """Test API endpoints structure"""
    print("\n🌐 Testing API structure...")
    
    try:
        # Mock the database collections to avoid MongoDB dependency
        with patch('database.users_collection', new=AsyncMock()), \
             patch('database.exams_collection', new=AsyncMock()), \
             patch('database.results_collection', new=AsyncMock()), \
             patch('database.create_sample_data', new=AsyncMock()):
            
            from main import app
            client = TestClient(app)
            
            # Test root endpoint
            response = client.get("/")
            assert response.status_code == 200
            data = response.json()
            assert "name" in data
            assert "Student Submissions API" in data["name"]
            print("✅ Root endpoint works")
            
            print("✅ API structure test passed")
            return True
            
    except Exception as e:
        print(f"❌ API structure test failed: {e}")
        return False


def print_setup_instructions():
    """Print setup instructions"""
    print("\n" + "="*60)
    print("🚀 STUDENT SUBMISSIONS API - SETUP COMPLETE")
    print("="*60)
    
    print("\n📁 Files created:")
    files = [
        "main.py - FastAPI application with all endpoints",
        "models.py - Pydantic models for data validation", 
        "database.py - MongoDB connection and sample data",
        "requirements.txt - Python dependencies",
        "setup.sh - Automated setup script",
        "README.md - Complete documentation",
        "test_app.py - Test script"
    ]
    
    for file in files:
        print(f"  ✅ {file}")
    
    print("\n🗄️  Database Collections Created:")
    collections = [
        "users - Store user information and exam enrollments",
        "exams - Store exam questions and answers", 
        "results - Store calculated exam results"
    ]
    
    for collection in collections:
        print(f"  📊 {collection}")
    
    print("\n🔧 To complete setup:")
    print("1. Install MongoDB:")
    print("   macOS: brew install mongodb-community")
    print("   Ubuntu: sudo apt install mongodb")
    print("   Windows: Download from mongodb.com")
    
    print("\n2. Install Python dependencies:")
    print("   pip install -r requirements.txt")
    
    print("\n3. Initialize database:")
    print("   python database.py")
    
    print("\n4. Start the application:")
    print("   python main.py")
    
    print("\n🌐 API Endpoints:")
    endpoints = [
        "GET / - API information",
        "POST /users/ - Create user",
        "GET /users/ - Get all users", 
        "GET /users/{user_id} - Get specific user",
        "POST /exams/ - Create exam",
        "GET /exams/ - Get all exams",
        "GET /exams/{exam_name} - Get specific exam",
        "POST /submit-answers/ - Submit exam answers",
        "POST /calculate-result/{user_id}/{exam_name} - Calculate result",
        "GET /results/ - Get all results",
        "GET /results/{user_id} - Get user results"
    ]
    
    for endpoint in endpoints:
        print(f"  🔗 {endpoint}")
    
    print("\n📖 Documentation available at: http://localhost:8000/docs")
    print("🎯 API ready at: http://localhost:8000")


def main():
    """Run all tests"""
    print("🔍 Running Student Submissions API Tests...\n")
    
    success = True
    
    # Test models
    if not test_without_mongodb():
        success = False
    
    # Test API structure  
    if not test_api_structure():
        success = False
    
    if success:
        print("\n🎉 All tests passed!")
        print_setup_instructions()
    else:
        print("\n❌ Some tests failed. Please check the errors above.")
    
    return success


if __name__ == "__main__":
    main()
