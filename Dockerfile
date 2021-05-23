FROM python

RUN pip install django
RUN pip install psycopg2-binary
RUN pip install numpy
RUN pip install pytickersymbols
RUN pip install pandas_datareader

WORKDIR /stocklooker
ENTRYPOINT python3 manage.py runserver 0.0.0.0:8000 --noreload
