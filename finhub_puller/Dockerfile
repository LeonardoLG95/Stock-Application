FROM python:3.9-buster

COPY . /finhub_puller
WORKDIR /finhub_puller

ENV PYTHONPATH="/"

RUN pip install -r requirements.txt

ENTRYPOINT python3 service.py
