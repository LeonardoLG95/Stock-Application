FROM python:3.9-buster

COPY . /finhub_puller
WORKDIR /finhub_puller

ENV PYTHONPATH="/"

RUN pip install -r puller_requirements.txt

ENTRYPOINT python3 service.py
