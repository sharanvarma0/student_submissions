#!/bin/bash

echo "🚀 Setting up Student Submissions API..."

# Check if MongoDB is installed
if ! command -v mongod &> /dev/null; then
    echo "📦 MongoDB not found. Installing MongoDB..."
    
    # Detect OS and install MongoDB
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        if ! command -v brew &> /dev/null; then
            echo "❌ Homebrew not found. Please install Homebrew first:"
            echo "   /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
            exit 1
        fi
        
        echo "🍺 Installing MongoDB via Homebrew..."
        brew tap mongodb/brew
        brew install mongodb-community
        
        echo "🔄 Starting MongoDB service..."
        brew services start mongodb-community
        
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux (Ubuntu/Debian)
        echo "🐧 Installing MongoDB on Linux..."
        sudo apt update
        sudo apt install -y mongodb
        sudo systemctl start mongodb
        sudo systemctl enable mongodb
        
    else
        echo "❌ Unsupported OS. Please install MongoDB manually:"
        echo "   Visit: https://www.mongodb.com/try/download/community"
        exit 1
    fi
else
    echo "✅ MongoDB is already installed"
    
    # Start MongoDB if not running
    if [[ "$OSTYPE" == "darwin"* ]]; then
        brew services start mongodb-community 2>/dev/null || true
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        sudo systemctl start mongodb 2>/dev/null || true
    fi
fi

# Wait for MongoDB to start
echo "⏳ Waiting for MongoDB to start..."
sleep 3

# Test MongoDB connection
echo "🔍 Testing MongoDB connection..."
if mongosh --eval "db.adminCommand('ping')" --quiet; then
    echo "✅ MongoDB is running successfully"
else
    echo "❌ MongoDB connection failed. Please check your MongoDB installation."
    exit 1
fi

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Initialize database with sample data
echo "🗄️  Initializing database with sample data..."
python database.py

echo ""
echo "🎉 Setup completed successfully!"
echo ""
echo "To start the application:"
echo "  python main.py"
echo ""
echo "Or with uvicorn:"
echo "  uvicorn main:app --host 0.0.0.0 --port 8000 --reload"
echo ""
echo "API will be available at: http://localhost:8000"
echo "Interactive docs at: http://localhost:8000/docs"
