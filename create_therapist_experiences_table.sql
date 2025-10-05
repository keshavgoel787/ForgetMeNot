-- Create THERAPIST_EXPERIENCES table for ReMind
-- This table stores curated memory experiences created by therapists for patients

CREATE TABLE IF NOT EXISTS THERAPIST_EXPERIENCES (
    id VARCHAR(36) PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    general_context TEXT,
    experience_data VARIANT,  -- Stores JSON with scenes and memories
    total_memories INT,
    created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    updated_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

-- Add index for faster queries
CREATE INDEX IF NOT EXISTS idx_therapist_experiences_title
ON THERAPIST_EXPERIENCES(title);

CREATE INDEX IF NOT EXISTS idx_therapist_experiences_created_at
ON THERAPIST_EXPERIENCES(created_at);

-- Verify table created
SHOW TABLES LIKE 'THERAPIST_EXPERIENCES';
