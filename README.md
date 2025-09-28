# Student Submissions API

A FastAPI-based backend application for tracking student exam submissions and results using MongoDB.

## Features

- **User Management**: Create and manage student users
- **Exam Management**: Create exams with multiple-choice questions
- **Answer Submission**: Students can submit answers for enrolled exams
- **Result Calculation**: Automatic scoring and grade calculation
- **Result Tracking**: Store and retrieve exam results

## Prerequisites

- Python 3.8+
- MongoDB (Community Edition)

## Installation

### 1. Install MongoDB

#### macOS (using Homebrew):
```bash
brew tap mongodb/brew
brew install mongodb-community
brew services start mongodb-community
```

#### Ubuntu/Debian:
```bash
sudo apt update
sudo apt install mongodb
sudo systemctl start mongodb
sudo systemctl enable mongodb
```

#### Windows:
Download and install from [MongoDB Community Server](https://www.mongodb.com/try/download/community)

### 2. Setup Python Environment

```bash
# Clone or navigate to the project directory
cd student_submissions

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Initialize Database

```bash
# Run the database initialization script
python database.py
```

This will:
- Test MongoDB connection
- Create sample data including users, exams, and results

## Running the Application

```bash
# Start the FastAPI server
python main.py

# Or using uvicorn directly
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at: `http://localhost:8000`

Interactive API documentation: `http://localhost:8000/docs`

## API Endpoints

### Root
- `GET /` - API information and available endpoints

### Users
- `POST /users/` - Create a new user
- `GET /users/` - Get all users
- `GET /users/{user_id}` - Get specific user

### Exams
- `POST /exams/` - Create a new exam
- `GET /exams/` - Get all exams
- `GET /exams/{exam_name}` - Get specific exam

### Results
- `POST /results/` - Create/update results
- `GET /results/` - Get all results
- `GET /results/{user_id}` - Get user's results

### Submissions
- `POST /submit-answers/` - Submit exam answers
- `POST /calculate-result/{user_id}/{exam_name}` - Calculate and store exam result

## Data Models

### User Document
```json
{
  "user_id": "user001",
  "user_name": "John Doe",
  "exams_enrolled": ["Python Basics", "JavaScript Fundamentals"],
  "exam_answers": [
    {
      "exam_name": "Python Basics",
      "answers": ["a", "b"]
    }
  ]
}
```

### Exam Document
```json
{
  "exam_name": "Python Basics",
  "questions": [
    {
      "question_id": "q1",
      "question_description": "What is the correct way to create a list in Python?",
      "options": [
        {"option_id": "a", "option_description": "list = []"},
        {"option_id": "b", "option_description": "list = {}"}
      ],
      "correct_option": "a"
    }
  ]
}
```

### Result Document
```json
{
  "user_id": "user001",
  "exam_results": [
    {
      "exam_name": "Python Basics",
      "exam_result": "100.0% - A+ - Excellent"
    }
  ]
}
```

## Sample Data

The application comes with sample data including:

### Users:
- **user001** (John Doe) - Enrolled in Python Basics and JavaScript Fundamentals
- **user002** (Jane Smith) - Enrolled in Python Basics
- **user003** (Bob Johnson) - Enrolled in JavaScript Fundamentals

### Exams:
- **Python Basics** - 2 questions about Python fundamentals
- **JavaScript Fundamentals** - 2 questions about JavaScript basics

### Results:
- Sample results for users who have completed exams

## Usage Examples

### 1. Create a New User
```bash
curl -X POST "http://localhost:8000/users/" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user004",
    "user_name": "Alice Brown",
    "exams_enrolled": ["Python Basics"]
  }'
```

### 2. Submit Exam Answers
```bash
curl -X POST "http://localhost:8000/submit-answers/" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user004",
    "exam_name": "Python Basics",
    "answers": ["a", "b"]
  }'
```

### 3. Calculate Result
```bash
curl -X POST "http://localhost:8000/calculate-result/user004/Python%20Basics"
```

## Environment Variables

- `MONGODB_URL` - MongoDB connection string (default: `mongodb://localhost:27017`)

## Development

The application uses:
- **FastAPI** - Modern, fast web framework
- **Motor** - Async MongoDB driver
- **Pydantic** - Data validation and serialization
- **Uvicorn** - ASGI server

## Error Handling

The API includes comprehensive error handling for:
- User not found
- Exam not found
- Duplicate users/exams
- Invalid submissions
- Database connection issues

## License

This project is for educational purposes.
