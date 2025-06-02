# Use a lean official Python image as the base.
# Python 3.10 is a good, stable choice. You can adjust the version
# if your project explicitly needs a different one (e.g., 3.11 or 3.12).
FROM python:3.10-slim-buster

# Set environment variables for Python.
# PYTHONUNBUFFERED makes stdout/stderr streams unbuffered, useful for logging.
# PYTHONDONTWRITEBYTECODE prevents Python from writing .pyc files, keeping the image clean.
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

# Set the working directory inside the container.
# Since your Dockerfile, manage.py, etc., are in the same directory (repo root),
# we set the workdir to '/app' and copy everything into it.
WORKDIR /app

# Install system dependencies required by some Python packages (like psycopg2-binary).
# 'libpq-dev' provides PostgreSQL client libraries, 'gcc' is for compiling C extensions.
# We update apt-get, install packages, and then clean up the cache to keep the image small.
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    # Add any other system dependencies your project might need here.
    # For example, for image processing libraries like Pillow or WeasyPrint with specific features:
    # libjpeg-dev zlib1g-dev libfreetype6-dev liblcms2-dev libwebp-dev tcl8.6-dev tk8.6-dev \
    # ghostscript \ # For WeasyPrint if it needs PostScript capabilities
    # fontconfig \ # For fonts if your app generates PDFs/images
    && rm -rf /var/lib/apt/lists/*

# Copy requirements.txt first to leverage Docker's build cache.
# If only code changes, but requirements.txt stays the same, this step is cached.
COPY requirements.txt /app/

# Install Python dependencies using pip.
# '--no-cache-dir' prevents pip from storing its cache, again for smaller image size.
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application code into the container.
# The '.' refers to the current directory where the Dockerfile is located.
COPY . /app/

# Run Django database migrations and collect static files during the build process.
# This ensures your database schema is up-to-date and all static assets are gathered
# BEFORE the application starts serving requests.
# '--noinput' prevents interactive prompts during these commands.
RUN python manage.py migrate --noinput && python manage.py collectstatic --noinput

# Define the command that will run your Django application when the container starts.
# 'gunicorn Store.wsgi:application' refers to your project's WSGI application.
# '--bind 0.0.0.0:$PORT' makes Gunicorn listen on all network interfaces on the port
# dynamically provided by Koyeb's environment ($PORT).
# '--log-file -' sends Gunicorn logs to standard output, which Koyeb captures for you.
CMD ["gunicorn", "Store.wsgi:application", "--bind", "0.0.0.0:$PORT", "--log-file", "-"]