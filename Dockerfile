FROM python:3.10-slim

WORKDIR /app

RUN python -m pip install --upgrade pip


COPY . /app

RUN pip install -r requirements.txt