# Use the official Python image.
FROM python:3.9

# Set the working directory
WORKDIR /app

# Copy the current directory contents into the container
COPY . /app

# Install dependencies
RUN pip install -r requirements.txt

# Install ffmpeg
RUN apt-get update && apt-get install -y ffmpeg

# Run the Django development server
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
