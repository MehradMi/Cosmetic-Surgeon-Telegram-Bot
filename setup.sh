#!/bin/bash

# Cosmetic Surgery Bot Docker Setup Script
# This script helps you set up and run your Telegram bot with Docker

set -e

echo "🚀 Setting up Cosmetic Surgery Bot with Docker..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker compose &> /dev/null && ! docker compose version &> /dev/null; then
    print_error "Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

print_success "Docker and Docker Compose are installed!"

# Create necessary directories
print_status "Creating necessary directories..."
mkdir -p data/database
mkdir -p data/static/pictures
mkdir -p data/static/target_person_pictures
mkdir -p data/static/comparison_pictures
mkdir -p data/logs
mkdir -p templates
mkdir -p assets

print_success "Directories created!"

# Check if .env file exists
if [ ! -f .env ]; then
    print_warning ".env file not found!"
    
    if [ -f .env.example ]; then
        print_status "Copying .env.example to .env..."
        cp .env.example .env
        print_warning "Please edit .env file with your actual values before running the bot!"
        print_status "Required variables:"
        echo "  - TELEGRAM_BOT_TOKEN"
        echo "  - OPENAI_API_KEY"
        echo "  - ADMIN_USERNAME"
        echo "  - ADMIN_PASSWORD"
        echo "  - FLASK_SECRET_KEY"
    else
        print_error ".env.example file not found. Please create .env file manually."
        exit 1
    fi
else
    print_success ".env file found!"
fi

# Check if requirements.txt exists
if [ ! -f requirements.txt ]; then
    print_warning "requirements.txt not found. Creating a basic one..."
    cat > requirements.txt << EOF
python-telegram-bot==20.7
openai==1.3.5
Pillow==10.1.0
requests==2.31.0
python-dotenv==1.0.0
Flask==3.0.0
asyncio
sqlite3
EOF
    print_success "Created basic requirements.txt"
fi

# Function to validate .env file
validate_env() {
    print_status "Validating .env file..."
    
    required_vars=("TELEGRAM_BOT_TOKEN" "OPENAI_API_KEY" "ADMIN_USERNAME" "ADMIN_PASSWORD")
    missing_vars=()
    
    for var in "${required_vars[@]}"; do
        if ! grep -q "^${var}=" .env || grep -q "^${var}=$" .env || grep -q "^${var}=your_" .env; then
            missing_vars+=("$var")
        fi
    done
    
    if [ ${#missing_vars[@]} -ne 0 ]; then
        print_error "Missing or invalid environment variables:"
        for var in "${missing_vars[@]}"; do
            echo "  - $var"
        done
        print_warning "Please update your .env file with valid values."
        return 1
    fi
    
    print_success "Environment variables are properly configured!"
    return 0
}

# Menu function
show_menu() {
    echo ""
    echo "==================== MENU ===================="
    echo "1. Validate configuration"
    echo "2. Build Docker images"
    echo "3. Start services (bot + dashboard)"
    echo "4. Start only bot"
    echo "5. Start only dashboard"
    echo "6. Stop all services"
    echo "7. View logs"
    echo "8. Clean up (remove containers and images)"
    echo "9. Reset data (WARNING: deletes all images and database)"
    echo "0. Exit"
    echo "=============================================="
}

# Main script logic
case "${1:-menu}" in
    "validate")
        validate_env
        ;;
    "build")
        print_status "Building Docker images..."
        docker compose build
        print_success "Images built successfully!"
        ;;
    "start")
        validate_env || exit 1
        print_status "Starting all services..."
        docker compose up -d
        print_success "Services started!"
        print_status "Dashboard available at: http://localhost:${DASHBOARD_PORT:-5000}"
        ;;
    "bot")
        validate_env || exit 1
        print_status "Starting only the bot..."
        docker compose up -d telegram-bot
        print_success "Bot started!"
        ;;
    "dashboard")
        validate_env || exit 1
        print_status "Starting only the dashboard..."
        docker compose up -d dashboard
        print_success "Dashboard started!"
        print_status "Dashboard available at: http://localhost:${DASHBOARD_PORT:-5000}"
        ;;
    "stop")
        print_status "Stopping all services..."
        docker compose down
        print_success "Services stopped!"
        ;;
    "logs")
        print_status "Showing logs... (Press Ctrl+C to exit)"
        docker compose logs -f
        ;;
    "clean")
        print_warning "This will remove all containers and images. Continue? (y/N)"
        read -r response
        if [[ "$response" =~ ^[Yy]$ ]]; then
            print_status "Cleaning up..."
            docker compose down --rmi all --volumes
            print_success "Cleanup completed!"
        else
            print_status "Cleanup cancelled."
        fi
        ;;
    "reset")
        print_warning "This will delete ALL data including images and database. Continue? (y/N)"
        read -r response
        if [[ "$response" =~ ^[Yy]$ ]]; then
            print_status "Resetting data..."
            docker compose down
            sudo rm -rf data/
            mkdir -p data/database data/static/pictures data/static/target_person_pictures data/static/comparison_pictures data/logs
            print_success "Data reset completed!"
        else
            print_status "Reset cancelled."
        fi
        ;;
    "menu"|*)
        while true; do
            show_menu
            read -p "Choose an option (0-9): " choice
            
            case $choice in
                1) validate_env ;;
                2) 
                    print_status "Building Docker images..."
                    docker compose build
                    print_success "Images built successfully!"
                    ;;
                3)
                    validate_env || continue
                    print_status "Starting all services..."
                    docker compose up -d
                    print_success "Services started!"
                    print_status "Dashboard available at: http://localhost:${DASHBOARD_PORT:-5000}"
                    ;;
                4)
                    validate_env || continue
                    print_status "Starting only the bot..."
                    docker compose up -d telegram-bot
                    print_success "Bot started!"
                    ;;
                5)
                    validate_env || continue
                    print_status "Starting only the dashboard..."
                    docker compose up -d dashboard
                    print_success "Dashboard started!"
                    print_status "Dashboard available at: http://localhost:${DASHBOARD_PORT:-5000}"
                    ;;
                6)
                    print_status "Stopping all services..."
                    docker compose down
                    print_success "Services stopped!"
                    ;;
                7)
                    print_status "Showing logs... (Press Ctrl+C to exit)"
                    docker compose logs -f
                    ;;
                8)
                    print_warning "This will remove all containers and images. Continue? (y/N)"
                    read -r response
                    if [[ "$response" =~ ^[Yy]$ ]]; then
                        print_status "Cleaning up..."
                        docker compose down --rmi all --volumes
                        print_success "Cleanup completed!"
                    else
                        print_status "Cleanup cancelled."
                    fi
                    ;;
                9)
                    print_warning "This will delete ALL data including images and database. Continue? (y/N)"
                    read -r response
                    if [[ "$response" =~ ^[Yy]$ ]]; then
                        print_status "Resetting data..."
                        docker compose down
                        sudo rm -rf data/
                        mkdir -p data/database data/static/pictures data/static/target_person_pictures data/static/comparison_pictures data/logs
                        print_success "Data reset completed!"
                    else
                        print_status "Reset cancelled."
                    fi
                    ;;
                0)
                    print_success "Goodbye!"
                    exit 0
                    ;;
                *)
                    print_error "Invalid option. Please try again."
                    ;;
            esac
            
            echo ""
            read -p "Press Enter to continue..."
        done
        ;;
esac