FROM python:3.9-buster

COPY . /finhub_puller
WORKDIR /finhub_puller

ENV PYTHONPATH="/"

RUN pip install -r requirements.txt

# 
ENTRYPOINT uvicorn service:APP --reload --host "0.0.0.0" --port "8000"
