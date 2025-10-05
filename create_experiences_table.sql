-- Simple Therapist Experiences Table
-- Therapist sends context + query → Results stored here → Patient retrieves by topic

CREATE TABLE IF NOT EXISTS THERAPIST_EXPERIENCES (
    experience_id VARCHAR PRIMARY KEY,
    title VARCHAR NOT NULL,
    general_context VARCHAR NOT NULL,

    -- Full experience JSON (scenes, memories, narratives)
    experience_data VARIANT NOT NULL,

    total_memories INTEGER,
    created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);
