#!/bin/bash

docker build . --tag reports-ws
docker image ls
docker rm reports-ws
docker run --name reports-ws -p 5000:5000 reports-ws

docker build . --tag reports-ws && docker rm reports-ws; docker run --name reports-ws -p 5000:5000 reports-ws