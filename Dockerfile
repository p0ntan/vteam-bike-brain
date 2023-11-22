FROM python:3.10.12-slim

WORKDIR /bike/app

COPY ./app/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
