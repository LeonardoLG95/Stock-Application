FROM python:3.9-buster

COPY . .
RUN pip install -r requirements.yml && cd models/ && pip install .

# ENTRYPOINT python3 service.py
ENTRYPOINT python3 script.py
