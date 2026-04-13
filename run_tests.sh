#!/bin/bash
set -e

echo "TESTE"
echo "=================================================="

if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python -m venv venv
fi

echo "Activating virtual environment..."
source venv/bin/activate

echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Run tests with coverage
echo ""
echo "🧪 Running unit tests..."
pytest tests/ -v

# Run coverage report
echo ""
echo "Generating coverage report..."
pytest tests/ --cov=audio_utils --cov=metadata_utils --cov=file_processor \
    --cov-report=html --cov-report=term-missing