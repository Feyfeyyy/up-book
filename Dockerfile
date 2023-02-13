# Use an official Python image as the base image
FROM python:3.9-alpine

# Set the working directory
WORKDIR /app

# Copy the project files to the container
COPY app .

# Copy the .env file to the container
COPY .env /app/

# Install Poetry
RUN pip install poetry

# Install the dependencies specified in the poetry.lock file
COPY poetry.lock pyproject.toml /app/
RUN poetry config virtualenvs.create false
RUN poetry install --no-dev --no-interaction --no-ansi

# Set environment variables
ENV FLASK_APP=app.py
ENV FLASK_ENV=production

# Expose the default Flask port
EXPOSE 5000

# Run the Flask app
CMD ["gunicorn", "--bind=0.0.0.0:5000", "--workers=4", "--timeout=120", "app:app"]