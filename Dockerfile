FROM python:3.11

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all application code and data
COPY main.py .
COPY models/ ./models/
COPY services/ ./services/
COPY data/ ./data/

# Make sure the directories are accessible
RUN chmod -R 755 ./data ./models ./services

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]

