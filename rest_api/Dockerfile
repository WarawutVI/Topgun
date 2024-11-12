FROM python:3.11-slim

WORKDIR /app

# ติดตั้ง system dependencies และ curl สำหรับ health check
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# คัดลอกไฟล์ requirements.txt
COPY requirements.txt .

# ติดตั้ง Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# คัดลอกโค้ดทั้งหมด
COPY . .

# แก้ปัญหา permission denied สำหรับ non-root user
RUN useradd -m myuser
RUN chown -R myuser:myuser /app
USER myuser

# รัน Flask ด้วย gunicorn
CMD ["gunicorn", "-b", "0.0.0.0:8000", "main:app", "--access-logfile", "-", "--error-logfile", "-"]