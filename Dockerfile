# Use the official Python base image
FROM python:3.10

# Set environment variables

# Set the working directory in the container
WORKDIR /app
ENV PYTHONUNBUFFERED 1
# Install dependencies
COPY requirements.txt /app/

RUN apt-get update && apt-get install -y firefox-esr && \
    apt-get install -y wget unzip && \
    wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb && \
    apt install -y ./google-chrome-stable_current_amd64.deb && \
    rm google-chrome-stable_current_amd64.deb  && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*
    
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Django project into the container
COPY . /app/

EXPOSE 10000
CMD [ "python" , "manage.py" , "runserver" ,"0.0.0.0:10000"]
