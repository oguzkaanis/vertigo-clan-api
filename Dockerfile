# 1. Base image
FROM python:3.12-slim

# 2. Çalışma dizini
WORKDIR /app

# 3. Gereksinimler
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# 4. Uygulama dosyalarını kopyala
COPY ./app ./app

# 5. Port
EXPOSE 8000

# 6. Çalıştırma komutu
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
