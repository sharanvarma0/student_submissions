from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Annotated
from bson import ObjectId


# Simplified ObjectId handling for Pydantic v2
PyObjectId = Annotated[str, Field(description="MongoDB ObjectId as string")]


class Option(BaseModel):
    option_id: str
    option_description: str


class Question(BaseModel):
    question_id: str
    question_description: str
    options: List[Option]
    correct_option: str


class Exam(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    exam_name: str
    questions: List[Question]

    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }


class ExamAnswer(BaseModel):
    exam_name: str
    answers: List[str]  # List of selected option_ids


class User(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    user_id: str
    user_name: str
    hashed_password: str
    exams_enrolled: List[str]
    exam_answers: List[ExamAnswer] = []
    is_active: bool = True

    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }


class ExamResult(BaseModel):
    exam_name: str
    exam_result: str  # Could be score, grade, or percentage


class Result(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    user_id: str
    exam_results: List[ExamResult]

    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }


# Authentication models
class UserLogin(BaseModel):
    username: str  # Can be user_id or user_name
    password: str


class UserRegister(BaseModel):
    user_id: str
    user_name: str
    password: str
    exams_enrolled: List[str] = []


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    user_id: Optional[str] = None


class UserResponse(BaseModel):
    """User model for API responses (without password)"""
    user_id: str
    user_name: str
    exams_enrolled: List[str]
    exam_answers: List[ExamAnswer] = []
    is_active: bool = True

    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }


# Request/Response models
class UserCreate(BaseModel):
    user_id: str
    user_name: str
    password: str
    exams_enrolled: List[str] = []


class ExamCreate(BaseModel):
    exam_name: str
    questions: List[Question]


class ResultCreate(BaseModel):
    user_id: str
    exam_results: List[ExamResult]


class SubmitAnswers(BaseModel):
    user_id: str
    exam_name: str
    answers: List[str]  # List of selected option_ids


class SubmitAnswersRequest(BaseModel):
    exam_name: str
    answers: List[str]  # List of selected option_ids
