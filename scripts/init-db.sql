-- Database initialization script for Modern Chatbot System
-- This script sets up the database with proper security and performance settings

-- Create database if it doesn't exist (handled by Docker environment variables)
-- CREATE DATABASE chatbot;

-- Create user if it doesn't exist (handled by Docker environment variables)
-- CREATE USER chatbot_user WITH PASSWORD 'secure_password';

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE chatbot TO chatbot_user;

-- Connect to the chatbot database
\c chatbot;

-- Create extensions for better performance and functionality
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "btree_gin";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";

-- Grant usage on extensions
GRANT USAGE ON SCHEMA public TO chatbot_user;
GRANT CREATE ON SCHEMA public TO chatbot_user;

-- Performance tuning settings
ALTER SYSTEM SET shared_preload_libraries = 'pg_stat_statements';
ALTER SYSTEM SET pg_stat_statements.track = 'all';
ALTER SYSTEM SET pg_stat_statements.max = 10000;

-- Connection and memory settings for production
ALTER SYSTEM SET max_connections = 200;
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET effective_cache_size = '1GB';
ALTER SYSTEM SET maintenance_work_mem = '64MB';
ALTER SYSTEM SET checkpoint_completion_target = 0.9;
ALTER SYSTEM SET wal_buffers = '16MB';
ALTER SYSTEM SET default_statistics_target = 100;
ALTER SYSTEM SET random_page_cost = 1.1;
ALTER SYSTEM SET effective_io_concurrency = 200;

-- Logging settings for monitoring
ALTER SYSTEM SET log_destination = 'stderr';
ALTER SYSTEM SET logging_collector = on;
ALTER SYSTEM SET log_directory = 'log';
ALTER SYSTEM SET log_filename = 'postgresql-%Y-%m-%d_%H%M%S.log';
ALTER SYSTEM SET log_rotation_age = '1d';
ALTER SYSTEM SET log_rotation_size = '100MB';
ALTER SYSTEM SET log_min_duration_statement = 1000;
ALTER SYSTEM SET log_line_prefix = '%t [%p]: [%l-1] user=%u,db=%d,app=%a,client=%h ';
ALTER SYSTEM SET log_checkpoints = on;
ALTER SYSTEM SET log_connections = on;
ALTER SYSTEM SET log_disconnections = on;
ALTER SYSTEM SET log_lock_waits = on;
ALTER SYSTEM SET log_temp_files = 0;

-- Security settings
ALTER SYSTEM SET password_encryption = 'scram-sha-256';
ALTER SYSTEM SET ssl = off;  -- SSL handled by load balancer in production

-- Reload configuration
SELECT pg_reload_conf();

-- Create indexes for better performance (these will be created by Alembic migrations)
-- But we can create some basic ones for immediate performance

-- Create a function for updating timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create a function for generating UUIDs
CREATE OR REPLACE FUNCTION generate_uuid()
RETURNS UUID AS $$
BEGIN
    RETURN uuid_generate_v4();
END;
$$ language 'plpgsql';

-- Grant execute permissions on functions
GRANT EXECUTE ON FUNCTION update_updated_at_column() TO chatbot_user;
GRANT EXECUTE ON FUNCTION generate_uuid() TO chatbot_user;

-- Create a monitoring view for database health
CREATE OR REPLACE VIEW db_health AS
SELECT
    'connections' as metric,
    count(*) as value,
    'active connections' as description
FROM pg_stat_activity
WHERE state = 'active'
UNION ALL
SELECT
    'database_size' as metric,
    pg_database_size(current_database()) as value,
    'database size in bytes' as description
UNION ALL
SELECT
    'cache_hit_ratio' as metric,
    round(
        100.0 * sum(blks_hit) / (sum(blks_hit) + sum(blks_read) + 1), 2
    ) as value,
    'cache hit ratio percentage' as description
FROM pg_stat_database
WHERE datname = current_database();

-- Grant access to monitoring view
GRANT SELECT ON db_health TO chatbot_user;

-- Create a simple health check function
CREATE OR REPLACE FUNCTION health_check()
RETURNS TABLE(status text, timestamp timestamptz) AS $$
BEGIN
    RETURN QUERY SELECT 'healthy'::text, now();
END;
$$ language 'plpgsql';

GRANT EXECUTE ON FUNCTION health_check() TO chatbot_user;

-- Log successful initialization
INSERT INTO pg_stat_statements_info (dealloc) VALUES (0);

-- Final message
DO $$
BEGIN
    RAISE NOTICE 'Database initialization completed successfully for Modern Chatbot System';
    RAISE NOTICE 'Database: %', current_database();
    RAISE NOTICE 'User: %', current_user;
    RAISE NOTICE 'Timestamp: %', now();
END $$;