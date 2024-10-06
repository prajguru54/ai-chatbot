#!/bin/bash

# Create the backend folder structure
mkdir -p backend/app/models
mkdir -p backend/app/routers
mkdir -p backend/app/services
touch backend/app/main.py
touch backend/requirements.txt
touch backend/Dockerfile

# Create the frontend folder structure
mkdir -p frontend/public
mkdir -p frontend/src/components
touch frontend/src/App.jsx
touch frontend/src/index.css
touch frontend/src/main.jsx
touch frontend/index.html
touch frontend/package.json
touch frontend/vite.config.js

# Create the README.md file in the root
touch README.md

echo "Folder structure created successfully!"
