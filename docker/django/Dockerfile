FROM python:3.8-buster

RUN pip install django==3.2 \
    psycopg2-binary \
    numpy \
    pytickersymbols \
    pandas

WORKDIR /stocklooker
ENTRYPOINT python3 manage.py runserver 0.0.0.0:8000 --noreload
