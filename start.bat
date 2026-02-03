@echo off
REM AI Construction Assistant - Windows Quick Start Script

echo ============================================
echo AI Construction Contract ^& Law Assistant
echo ============================================
echo.

REM Check if virtual environment exists
if not exist "venv\" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo Installing dependencies...
pip install -q -r requirements.txt

REM Check for .env file
if not exist ".env" (
    echo.
    echo WARNING: .env file not found!
    echo Please copy .env.example to .env and configure:
    echo   copy .env.example .env
    echo   notepad .env  # Add your OPENAI_API_KEY
    echo.
    pause
)

REM Create necessary directories
if not exist "logs" mkdir logs
if not exist "uploads" mkdir uploads
if not exist "vector_db_storage" mkdir vector_db_storage

REM Start the application
echo.
echo Starting AI Construction Assistant...
echo Access the application at: http://localhost:5000
echo.
echo Press Ctrl+C to stop the server
echo.

cd backend
python app.py
