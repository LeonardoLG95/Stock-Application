FROM python:3.10.0b1-alpine3.13

RUN apk update && apk add postgresql-dev gcc python3-dev musl-dev linux-headers g++ libxml2-dev libxslt-dev libxml2 libxslt
RUN pip install virtualenv
RUN virtualenv env
RUN source env/bin/activate
RUN pip install --upgrade pip setuptools wheel
RUN pip install django
RUN pip install psycopg2-binary
RUN pip install pandas_datareader
RUN pip install --no-use-pep517 numpy
RUN pip install pytickersymbols
WORKDIR /stocklooker
ENTRYPOINT python3 manage.py runserver 0.0.0.0:8000 --noreload
