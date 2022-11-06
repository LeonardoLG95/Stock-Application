FROM node:19.0-buster-slim

COPY . /frontend
WORKDIR /frontend

RUN npm install

ENTRYPOINT npm run start
