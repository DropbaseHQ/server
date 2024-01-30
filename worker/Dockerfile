# Use an official Python runtime as a parent image
FROM python:3.11-slim
WORKDIR /app
RUN mkdir -p /app/data

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir --upgrade -r requirements.txt