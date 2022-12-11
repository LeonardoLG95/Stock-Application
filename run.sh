#!/bin/bash
cd finhub_puller
docker build . -t finhub-puller:latest &
cd -
cd wallet_admin
docker build . -t wallet-admin:latest &
cd -
cd frontend
docker build . -t frontend:latest &
wait
# docker-compose up -d
docker-compose up
