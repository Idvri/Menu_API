FROM python:3.10-slim

WORKDIR /code/

COPY . .
RUN pip install -r /code/requirements.txt