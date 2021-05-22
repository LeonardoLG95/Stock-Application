FROM python:3.10.0b1-alpine3.13

RUN apk update && apk add postgresql-dev gcc python3-dev musl-dev
RUN pip install django
RUN pip install psycopg2-binary
WORKDIR /stocklooker
ENTRYPOINT python3 manage.py runserver 0.0.0.0:8000 --noreload