#!/bin/bash

# KIT CampusAI - Automated Setup Script
# This script helps automate the setup process

set -e  # Exit on error

echo "🚀 KIT CampusAI Setup Script"
echo "================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored messages
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "ℹ️  $1"
}

# Check if running from project root
if [ ! -f "PROJECT_REQUIREMENTS.md" ]; then
    print_error "Please run this script from the project root directory"
    exit 1
fi

# Step 1: Check prerequisites
echo "Step 1: Checking prerequisites..."
echo "================================"

# Check Python
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    print_success "Python 3 found: $PYTHON_VERSION"
else
    print_error "Python 3 not found. Please install Python 3.9+"
    exit 1
fi

# Check PostgreSQL
if command -v psql &> /dev/null; then
    PSQL_VERSION=$(psql --version | cut -d' ' -f3)
    print_success "PostgreSQL found: $PSQL_VERSION"
else
    print_warning "PostgreSQL not found. You'll need to install it manually."
fi

# Check pip
if command -v pip3 &> /dev/null; then
    print_success "pip3 found"
else
    print_error "pip3 not found. Please install pip3"
    exit 1
fi

echo ""

# Step 2: Setup backend
echo "Step 2: Setting up backend..."
echo "================================"

cd backend

# Create virtual environment
if [ ! -d "venv" ]; then
    print_info "Creating virtual environment..."
    python3 -m venv venv
    print_success "Virtual environment created"
else
    print_info "Virtual environment already exists"
fi

# Activate virtual environment
print_info "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
print_info "Installing Python dependencies... (this may take a few minutes)"
pip install --upgrade pip > /dev/null 2>&1
pip install -r requirements.txt > /dev/null 2>&1
print_success "Dependencies installed"

# Setup environment file
if [ ! -f ".env" ]; then
    print_info "Creating .env file from template..."
    cp .env.example .env
    print_warning "Please edit backend/.env with your API credentials!"
    print_info "You need to add:"
    echo "  - GOOGLE_CLIENT_ID"
    echo "  - GOOGLE_CLIENT_SECRET"
    echo "  - GEMINI_API_KEY"
    echo "  - DATABASE_URL (if different from default)"
    echo ""
    
    # Generate JWT secret
    JWT_SECRET=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
    
    # Update JWT_SECRET in .env
    if [[ "$OSTYPE" == "darwin"* ]]; then
        sed -i '' "s/JWT_SECRET=.*/JWT_SECRET=$JWT_SECRET/" .env
    else
        sed -i "s/JWT_SECRET=.*/JWT_SECRET=$JWT_SECRET/" .env
    fi
    
    print_success ".env file created with random JWT_SECRET"
else
    print_info ".env file already exists"
fi

cd ..

echo ""

# Step 3: Database setup instructions
echo "Step 3: Database setup"
echo "================================"
print_warning "Database setup requires manual steps:"
echo ""
echo "Run these commands in PostgreSQL:"
echo ""
echo "  CREATE DATABASE kit_campusai;"
echo "  \\c kit_campusai"
echo "  CREATE EXTENSION vector;"
echo ""
print_info "After database is created, run migrations:"
echo "  cd backend"
echo "  source venv/bin/activate"
echo "  alembic upgrade head"
echo ""

# Step 4: Check for Flutter (optional)
echo "Step 4: Mobile app setup (optional)"
echo "================================"

if command -v flutter &> /dev/null; then
    FLUTTER_VERSION=$(flutter --version | head -n 1)
    print_success "Flutter found: $FLUTTER_VERSION"
    
    print_info "Setting up mobile app..."
    cd mobile/android_app
    flutter pub get > /dev/null 2>&1
    print_success "Mobile app dependencies installed"
    cd ../..
else
    print_warning "Flutter not found. Skip mobile app setup for now."
    print_info "Install Flutter later from: https://docs.flutter.dev/get-started/install"
fi

echo ""

# Summary
echo "🎉 Setup Complete!"
echo "================================"
echo ""
print_success "Backend setup finished!"
echo ""
print_info "Next steps:"
echo ""
echo "1. Get API credentials from Google Cloud:"
echo "   - Gemini API: https://makersuite.google.com/app/apikey"
echo "   - OAuth: https://console.cloud.google.com/apis/credentials"
echo ""
echo "2. Update backend/.env with your credentials"
echo ""
echo "3. Setup PostgreSQL database (see Step 3 above)"
echo ""
echo "4. Run migrations:"
echo "   cd backend"
echo "   source venv/bin/activate"
echo "   alembic upgrade head"
echo ""
echo "5. Start the backend:"
echo "   uvicorn app.main:app --reload"
echo ""
echo "6. Open http://localhost:8000/docs to test the API"
echo ""
print_info "For detailed instructions, see QUICK_START.md"
echo ""
