FROM python:3.8.10-alpine

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

RUN apk --update add
RUN apk add gcc libc-dev libffi-dev jpeg-dev zlib-dev libjpeg

RUN pip install --upgrade pip

COPY ./requirements.txt .
COPY ./entrypoint.sh .

RUN chmod +x entrypoint.sh

RUN pip install -r requirements.txt

COPY . .

ENTRYPOINT ["/app/entrypoint.sh"]