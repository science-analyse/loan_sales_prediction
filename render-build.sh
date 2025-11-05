#!/usr/bin/env bash
# exit on error
set -o errexit

echo "🔧 Installing Python packages with pre-built wheels..."

# Upgrade pip
pip install --upgrade pip

# Install packages with pre-built wheels (no compilation needed)
pip install --only-binary=:all: \
    fastapi==0.104.1 \
    uvicorn[standard]==0.24.0 \
    jinja2==3.1.2 \
    python-multipart==0.0.6 \
    pandas==2.2.3 \
    numpy==1.26.4 \
    gunicorn==21.2.0

# Install ML packages
pip install scikit-learn==1.5.2
pip install statsmodels==0.14.4

echo "✅ Build completed successfully!"
