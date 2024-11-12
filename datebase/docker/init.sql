CREATE TABLE data (
    id SERIAL PRIMARY KEY,
    massage  VARCHAR(255) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE OR REPLACE FUNCTION update_modified_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_explore_modtime
    BEFORE UPDATE ON explore
    FOR EACH ROW
    EXECUTE FUNCTION update_modified_column();

CREATE INDEX idx_explore_name ON data(massage);


