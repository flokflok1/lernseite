@echo off
REM ============================================================================
REM LernsystemX Database Reset Script
REM Description: Drops and recreates the database for a fresh start
REM ============================================================================

echo.
echo ========================================
echo LernsystemX Database Reset
echo ========================================
echo.
echo This script will:
echo   1. Drop lernsystemx_dev database (if exists)
echo   2. Create fresh lernsystemx_dev database
echo   3. Enable required PostgreSQL extensions
echo.
echo WARNING: All existing data will be lost!
echo.

pause

echo.
echo Connecting to PostgreSQL...
echo.

REM Set PostgreSQL path
set PGPATH="C:\Program Files\PostgreSQL\17\bin"
set PGPASSWORD=postgres

REM Drop existing database
echo Dropping existing database...
%PGPATH%\psql.exe -U postgres -c "DROP DATABASE IF EXISTS lernsystemx_dev;"

REM Create fresh database
echo Creating fresh database...
%PGPATH%\psql.exe -U postgres -c "CREATE DATABASE lernsystemx_dev OWNER postgres;"

REM Enable extensions
echo Enabling PostgreSQL extensions...
%PGPATH%\psql.exe -U postgres -d lernsystemx_dev -c "CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";"
%PGPATH%\psql.exe -U postgres -d lernsystemx_dev -c "CREATE EXTENSION IF NOT EXISTS \"pgcrypto\";"

echo.
echo ========================================
echo Database reset complete!
echo ========================================
echo.
echo Next steps:
echo   1. Start the backend: python run.py
echo   2. Navigate to: http://localhost:5000/setup/status
echo   3. Click "Initialize Database"
echo.

pause
