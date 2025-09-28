# Student Submissions API

A FastAPI-based backend application for tracking student exam submissions and results using MongoDB.

## Features
- **Authentication**: Register and Login required for Users.
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

## Future Improvements

Look at schema improvements

The current schema uses unbounded arrays. This is an antipattern in MongoDB and would not work at scale. There is a requirement for a more optimized approach to the schema.

Indexing for Schema?

The default indexing at the _id field exists. However, currently no extra indexing has been put into place. The indexing we can attempt are: Simple Index, Compound Index.
A simple index can be added to each of the documents - user and results to increase performance in fetching users and user specific results.

The exams model doesn't seem to need an index as the options and entries would be vastly lower in comparison to results or users table.

A simple index on user_id field can be added to both users and results. These additions will cause an initial performance impact due to the building process including limited read/write access. Its best done before deployment or during downtime if possible.

Does the current schema scale with increasing traffic to the service?
The current schema simply maintains a list of entries of each of exam, user and results. All operations on these documents are done via Async code.
While the code itself will scale, especially if deployed as a distributed system using kubernetes or nomad. The DB operations might need to be queued at the MongoDB level to ensure that the database doesn't tank.

In order to prevent DB level tanking, at high scale we can cache the updates or store the updates initially and then commit them at a batch level. This will ensure that the number of write requests to DB is less.


Implementing Predictive Results

- Change schema for exams and include a tag: mock: true/false
- Generate result for all mock exams a user has given (use tag mock=true)
- These can be done on a per exam basis.
- These can be predictive results

Implementing Comparison

- For an exam, get mock test results and the performance
- For that exam, get the final exam test results
- Calculate comparison in marks. This can be expressed as a + or - relative to mock exam.
- A much heavier approach would be to train an ML model at the backend with all mock exam marks as data points and use that model to output the potential performance of the candidate before the test. The initial training would be an async process and will need to be done before its use. Once done, the ML model might be able to churn out real time predictions on the test results.

Real Time Prediction vs Accuracy.
- Real Time prediction can be done in 2 ways.
- First: For each request to prediction, calculate mock exam results and the current exam results and present this. This has problems however. The first one being load. At high traffic times, this could result in a huge system slowdown as millions of prediction requests are being sent to the system. Even if the application is developed to make use of async programming, the code itself would need to run quickly since the results are expected soon. A large queue of async tasks could lead to an increase in computation time.
- Second: Pre compute all mock exam results and cache them for a certain number of days. Update this cache value every time a mock exam is given by computing results for that mock exam and storing it in the cache. When requested, fetch the cached value instead. This highly reduces the load. Its highly unlikely that the cache would tank due to its in memory nature and precomputing would also result in the prediction fetch time to go down drastically.
- Third: If we are going by the ML model approach, we can use the model to get the results. If the model is running on a good hardware setup and uses parallel inference mechanisms, the result would be obtained faster and in realtime. The accuracy would vary depending on the algorithm and training data used. The ML model training itself can be done in an async manner where the data is generated as soon as a mock exam is attempted and then fed into a model during a routine training job as a cron.