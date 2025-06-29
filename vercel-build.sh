#!/bin/bash

# Install frontend dependencies and build
cd frontend-vite
npm install
npm run build

# Go back to root
cd ..

# Install Python dependencies
pip install -r requirements.txt
