-- KIT CampusAI Database Setup Script
-- Run this script to create and configure the database

-- Create database (run as postgres user)
CREATE DATABASE kit_campusai;

-- Connect to the database
\c kit_campusai

-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create application user (optional but recommended)
CREATE USER kit_admin WITH ENCRYPTED PASSWORD 'change_this_password';

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE kit_campusai TO kit_admin;
GRANT ALL PRIVILEGES ON SCHEMA public TO kit_admin;

-- Verify extension
SELECT * FROM pg_extension WHERE extname = 'vector';

-- Success message
\echo 'Database setup complete!'
\echo 'Next steps:'
\echo '1. Update DATABASE_URL in backend/.env'
\echo '2. Run: cd backend && alembic upgrade head'
