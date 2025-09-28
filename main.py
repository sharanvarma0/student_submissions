from fastapi import FastAPI, HTTPException, status, Depends
from typing import List, Optional
import asyncio
from contextlib import asynccontextmanager
from datetime import timedelta

from models import (
    User, Exam, Result, UserCreate, ExamCreate, ResultCreate, 
    SubmitAnswers, ExamAnswer, ExamResult, UserLogin, UserRegister, 
    Token, UserResponse, SubmitAnswersRequest
)
from database import (
    users_collection, exams_collection, results_collection, 
    init_mongodb, create_sample_data
)
from auth import (
    authenticate_user, create_access_token,
    get_current_active_user, ACCESS_TOKEN_EXPIRE_MINUTES
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Starting up Student Submissions API...")
    try:
        # Initialize MongoDB and create sample data
        await create_sample_data()
        print("Database initialized with sample data")
    except Exception as e:
        print(f"Warning: Could not initialize database: {e}")
    
    yield
    
    # Shutdown
    print("Shutting down Student Submissions API...")


app = FastAPI(
    title="Student Submissions API",
    description="A backend to track submissions for certain exams by students",
    version="1.0.0",
    lifespan=lifespan
)


@app.get("/")
async def read_root():
    """Root endpoint with API information"""
    json_response = {
        "name": "Student Submissions API",
        "description": "A backend to track submissions for certain exams by students",
        "capabilities": [
            "Track user specific marks", 
            "Track subject specific marks for a user", 
            "Track the questions posed to the user", 
            "Track results for each exam for the user"
        ],
        "endpoints": {
            "users": "/users/",
            "exams": "/exams/",
            "results": "/results/",
            "submit_answers": "/submit-answers/",
            "calculate_result": "/calculate-result/"
        }
    }
    return json_response


# Authentication endpoints
@app.post("/auth/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(user: UserRegister):
    """Register a new user"""
    # Check if user already exists
    existing_user = await users_collection.find_one({
        "$or": [
            {"user_id": user.user_id},
            {"user_name": user.user_name}
        ]
    })
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this user_id or user_name already exists"
        )
    
    # Store the hashed password directly (assuming it comes pre-hashed from frontend)
    user_dict = {
        "user_id": user.user_id,
        "user_name": user.user_name,
        "hashed_password": user.password,  # Store as-is (already hashed from frontend)
        "exams_enrolled": user.exams_enrolled,
        "exam_answers": [],
        "is_active": True
    }
    
    result = await users_collection.insert_one(user_dict)
    created_user = await users_collection.find_one({"_id": result.inserted_id})
    # Convert ObjectId to string for Pydantic
    if created_user and "_id" in created_user:
        created_user["_id"] = str(created_user["_id"])
    return UserResponse(**created_user)


@app.post("/auth/login", response_model=Token)
async def login_user(login_data: UserLogin):
    """Login user and return access token"""
    # login_data.password is expected to be already hashed from frontend
    print(login_data.username, login_data.password)
    user = await authenticate_user(login_data.username, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.user_id}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/auth/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    """Get current user information"""
    return UserResponse(**current_user.model_dump())


# User endpoints (Admin only - for demonstration, you might want to add admin role)
@app.post("/users/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate, current_user: User = Depends(get_current_active_user)):
    """Create a new user (Admin function)"""
    # Check if user already exists
    existing_user = await users_collection.find_one({
        "$or": [
            {"user_id": user.user_id},
            {"user_name": user.user_name}
        ]
    })
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this user_id or user_name already exists"
        )
    
    # Store the hashed password directly (assuming it comes pre-hashed from frontend)
    user_dict = {
        "user_id": user.user_id,
        "user_name": user.user_name,
        "hashed_password": user.password,  # Store as-is (already hashed from frontend)
        "exams_enrolled": user.exams_enrolled,
        "exam_answers": [],
        "is_active": True
    }
    result = await users_collection.insert_one(user_dict)
    created_user = await users_collection.find_one({"_id": result.inserted_id})
    return UserResponse(**created_user)


@app.get("/users/", response_model=List[UserResponse])
async def get_all_users(current_user: User = Depends(get_current_active_user)):
    """Get all users (Admin function)"""
    users = []
    async for user in users_collection.find():
        users.append(UserResponse(**user))
    return users


@app.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: str, current_user: User = Depends(get_current_active_user)):
    """Get a specific user by user_id"""
    user = await users_collection.find_one({"user_id": user_id})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return UserResponse(**user)


# Exam endpoints
@app.post("/exams/", response_model=Exam, status_code=status.HTTP_201_CREATED)
async def create_exam(exam: ExamCreate, current_user: User = Depends(get_current_active_user)):
    """Create a new exam (Admin function)"""
    # Check if exam already exists
    existing_exam = await exams_collection.find_one({"exam_name": exam.exam_name})
    if existing_exam:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Exam with this name already exists"
        )
    
    exam_dict = exam.model_dump()
    result = await exams_collection.insert_one(exam_dict)
    created_exam = await exams_collection.find_one({"_id": result.inserted_id})
    return Exam(**created_exam)


@app.get("/exams/", response_model=List[Exam])
async def get_all_exams(current_user: User = Depends(get_current_active_user)):
    """Get all exams"""
    exams = []
    async for exam in exams_collection.find():
        exams.append(Exam(**exam))
    return exams


@app.get("/exams/{exam_name}", response_model=Exam)
async def get_exam(exam_name: str, current_user: User = Depends(get_current_active_user)):
    """Get a specific exam by name"""
    exam = await exams_collection.find_one({"exam_name": exam_name})
    if not exam:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exam not found"
        )
    return Exam(**exam)


# Result endpoints
@app.post("/results/", response_model=Result, status_code=status.HTTP_201_CREATED)
async def create_result(result: ResultCreate, current_user: User = Depends(get_current_active_user)):
    """Create a new result (Admin function)"""
    # Check if user exists
    user = await users_collection.find_one({"user_id": result.user_id})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Check if result already exists for this user
    existing_result = await results_collection.find_one({"user_id": result.user_id})
    if existing_result:
        # Update existing result
        await results_collection.update_one(
            {"user_id": result.user_id},
            {"$set": {"exam_results": result.exam_results}}
        )
        updated_result = await results_collection.find_one({"user_id": result.user_id})
        return Result(**updated_result)
    else:
        # Create new result
        result_dict = result.model_dump()
        insert_result = await results_collection.insert_one(result_dict)
        created_result = await results_collection.find_one({"_id": insert_result.inserted_id})
        return Result(**created_result)


@app.get("/results/", response_model=List[Result])
async def get_all_results(current_user: User = Depends(get_current_active_user)):
    """Get all results (Admin function)"""
    results = []
    async for result in results_collection.find():
        results.append(Result(**result))
    return results


@app.get("/results/me", response_model=Result)
async def get_my_results(current_user: User = Depends(get_current_active_user)):
    """Get results for the current user"""
    result = await results_collection.find_one({"user_id": current_user.user_id})
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No results found for current user"
        )
    return Result(**result)


@app.get("/results/{user_id}", response_model=Result)
async def get_user_results(user_id: str, current_user: User = Depends(get_current_active_user)):
    """Get results for a specific user (Admin function)"""
    result = await results_collection.find_one({"user_id": user_id})
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Results not found for this user"
        )
    return Result(**result)


# Submit answers endpoint


@app.post("/submit-answers/", status_code=status.HTTP_200_OK)
async def submit_answers(submission: SubmitAnswersRequest, current_user: User = Depends(get_current_active_user)):
    """Submit answers for an exam"""
    # Check if exam exists
    exam = await exams_collection.find_one({"exam_name": submission.exam_name})
    if not exam:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exam not found"
        )
    
    # Check if user is enrolled in this exam
    if submission.exam_name not in current_user.exams_enrolled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not enrolled in this exam"
        )
    
    # Update user's exam answers
    exam_answer = {
        "exam_name": submission.exam_name,
        "answers": submission.answers
    }
    
    # Remove existing answers for this exam if any
    await users_collection.update_one(
        {"user_id": current_user.user_id},
        {"$pull": {"exam_answers": {"exam_name": submission.exam_name}}}
    )
    
    # Add new answers
    await users_collection.update_one(
        {"user_id": current_user.user_id},
        {"$push": {"exam_answers": exam_answer}}
    )
    
    return {"message": "Answers submitted successfully"}


# Calculate result endpoints
@app.post("/calculate-result/me/{exam_name}")
async def calculate_my_result(exam_name: str, current_user: User = Depends(get_current_active_user)):
    """Calculate and store result for current user's exam"""
    return await _calculate_result_for_user(current_user.user_id, exam_name)


@app.post("/calculate-result/{user_id}/{exam_name}")
async def calculate_result(user_id: str, exam_name: str, current_user: User = Depends(get_current_active_user)):
    """Calculate and store result for a user's exam (Admin function)"""
    return await _calculate_result_for_user(user_id, exam_name)


async def _calculate_result_for_user(user_id: str, exam_name: str):
    """Internal function to calculate result for a user"""
    # Get user
    user = await users_collection.find_one({"user_id": user_id})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Get exam
    exam = await exams_collection.find_one({"exam_name": exam_name})
    if not exam:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exam not found"
        )
    
    # Find user's answers for this exam
    user_answers = None
    for exam_answer in user.get("exam_answers", []):
        if exam_answer["exam_name"] == exam_name:
            user_answers = exam_answer["answers"]
            break
    
    if user_answers is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User has not submitted answers for this exam"
        )
    
    # Calculate score
    correct_answers = 0
    total_questions = len(exam["questions"])
    
    for i, question in enumerate(exam["questions"]):
        if i < len(user_answers) and user_answers[i] == question["correct_option"]:
            correct_answers += 1
    
    score_percentage = (correct_answers / total_questions) * 100
    
    # Determine grade
    if score_percentage >= 90:
        grade = "A+ - Excellent"
    elif score_percentage >= 80:
        grade = "A - Very Good"
    elif score_percentage >= 70:
        grade = "B - Good"
    elif score_percentage >= 60:
        grade = "C - Average"
    else:
        grade = "F - Fail"
    
    result_text = f"{score_percentage:.1f}% - {grade}"
    
    # Store result
    exam_result = {
        "exam_name": exam_name,
        "exam_result": result_text
    }
    
    # Check if result already exists for this user
    existing_result = await results_collection.find_one({"user_id": user_id})
    if existing_result:
        # Remove existing result for this exam
        await results_collection.update_one(
            {"user_id": user_id},
            {"$pull": {"exam_results": {"exam_name": exam_name}}}
        )
        # Add new result
        await results_collection.update_one(
            {"user_id": user_id},
            {"$push": {"exam_results": exam_result}}
        )
    else:
        # Create new result document
        new_result = {
            "user_id": user_id,
            "exam_results": [exam_result]
        }
        await results_collection.insert_one(new_result)
    
    return {
        "message": "Result calculated successfully",
        "score": f"{correct_answers}/{total_questions}",
        "percentage": f"{score_percentage:.1f}%",
        "grade": grade,
        "result": result_text
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9000)
