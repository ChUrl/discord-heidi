# syntax=docker/dockerfile:1

FROM python:3.10.1-slim-buster
RUN apt-get update -y
RUN apt-get install -y ffmpeg libopus0
WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
COPY . .
CMD ["python3", "bot.py"]
