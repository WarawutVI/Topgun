-- สร้างตาราง users
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- สร้าง function สำหรับอัพเดท updated_at โดยอัตโนมัติ
CREATE OR REPLACE FUNCTION update_modified_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- สร้าง trigger สำหรับอัพเดท updated_at
CREATE TRIGGER update_users_modtime
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_modified_column();

-- สร้าง indexes เพื่อเพิ่มประสิทธิภาพ
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_name ON users(name);


-- เพิ่มข้อมูลตัวอย่าง
INSERT INTO users (name, email) VALUES 
    ('ณัฐโชติ พรหมฤทธิ์', 'nuttachot@example.com'),
    ('สัจจาภรณ์ ไวจรรยา', 'sajjaporn@example.com'),
    ('สมศรี มีสุข', 'somsri@example.com');