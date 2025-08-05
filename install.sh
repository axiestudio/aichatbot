#!/bin/bash

echo "Installing Modern Chatbot System Dependencies..."
echo

echo "Installing root dependencies..."
npm install

echo
echo "Installing frontend dependencies..."
cd frontend
npm install
cd ..

echo
echo "Installing backend dependencies..."
cd backend
pip install -r requirements.txt
cd ..

echo
echo "Installation complete!"
echo "Run './start.sh' to start the application."
