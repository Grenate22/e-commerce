FROM python:3.9-alpine3.19

ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt requirements.txt
RUN apk update \
    && apk add --virtual build-deps gcc python3-dev musl-dev \
    && apk add --no-cache mariadb-dev

RUN pip install mysqlclient  

RUN apk del build-deps

RUN pip install -r requirements.txt
RUN mkdir /app
COPY . /app
WORKDIR /app
