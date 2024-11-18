FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Install required system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file into the container# Copy the requirements file into the container
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install NLTK stopwords during the build process
RUN python -m nltk.downloader stopwords

# Copy the FastAPI application code into the container
COPY . .

# Expose the port the FastAPI app runs on
EXPOSE 8000

CMD ["python", "search_recipe.py"]
