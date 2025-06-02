# Use a lean official Python image as the base
# We'll use 3.10-slim-buster as it's a stable, widely used base.
# You can choose a different version if your project specifically requires it.
FROM python:3.10-slim-buster

# Set environment variables for Python to run unbuffered and not write .pyc files.
# This is good practice for Dockerized applications.
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

# Set the working directory inside the container.
# This is where your application code will reside.
# If your Django project is in a subdirectory (e.g., 'backend/'), change this to '/app/backend'
WORKDIR /app

# Install system dependencies required by some Python packages (like psycopg2-binary).
# 'libpq-dev' is for PostgreSQL client libraries, 'gcc' is for compiling C extensions.
# Remove the cache to keep the image size small.
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    # Add any other system dependencies your specific project might need (e.g., imagemagick, webp tools, etc.)
    # imagemagick-6.q16-dev \
    # libwebp-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy only the requirements file first to leverage Docker's build cache.
# If requirements.txt doesn't change, Docker won't re-run pip install.
COPY requirements.txt /app/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application code into the container.
# This assumes your Dockerfile is in the root and your Django project code is relative to it.
COPY . /app/

# Run Django migrations and collect static files during the build process.
# This ensures your database schema is up-to-date and static files are ready
# BEFORE the application starts serving requests.
# --noinput prevents interactive prompts.
RUN python manage.py migrate --noinput && python manage.py collectstatic --noinput

# Define the command to run your Django application using Gunicorn.
# 'Store.wsgi:application' refers to your project's WSGI application.
# '--bind 0.0.0.0:$PORT' binds Gunicorn to all network interfaces on the port
# provided by the Koyeb environment variable.
# '--log-file -' sends Gunicorn logs to stdout, which Koyeb captures.
CMD ["gunicorn", "Store.wsgi:application", "--bind", "0.0.0.0:$PORT", "--log-file", "-"]