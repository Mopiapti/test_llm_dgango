FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Create working directory
WORKDIR /app

# Copy dependency files
COPY pyproject.toml ./
COPY requirements.txt* ./

# Install Python dependencies
# Handle both pyproject.toml and requirements.txt
RUN pip install --upgrade pip && \
    if [ -f requirements.txt ]; then \
        pip install --no-cache-dir -r requirements.txt; \
    fi && \
    if [ -f pyproject.toml ]; then \
        pip install --no-cache-dir -e .; \
    fi

# Copy source code
COPY . .

# Expose port
EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]