FROM python:3.11.5-slim

WORKDIR /app

COPY ./requirements.txt /app/
RUN pip install -r requirements.txt

COPY ./src ./src

RUN rm requirements.txt