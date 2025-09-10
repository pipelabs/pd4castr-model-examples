FROM python:3.12-slim-bookworm AS base

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

CMD [ "python", "model/main.py" ]
