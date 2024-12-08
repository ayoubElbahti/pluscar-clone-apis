# Use the official Python base image
FROM python:3.10

# Set environment variables

# Set the working directory in the container
WORKDIR /app
ENV PYTHONUNBUFFERED 1
# Install dependencies
COPY requirements.txt /app/
    
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Django project into the container
COPY . /app/

EXPOSE 10000
CMD [ "python" , "manage.py" , "runserver" ,"0.0.0.0:10000"]
