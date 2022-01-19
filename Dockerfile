# syntax=docker/dockerfile:1

FROM python:3.10.1-alpine3.15
WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
COPY . .
CMD ["python3", "bot.py"]
