# Use official Python image
FROM python:3.12-slim

# Setting working directory
WORKDIR /app

# Copy project files
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Create output directory
RUN mkdir -p output

# Run the script
CMD ["python", "project_script.py"]