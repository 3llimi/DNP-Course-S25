#!/bin/bash

# 0. Write propper RabbitMQ parameters
echo "RMQ_HOST = 'rabbitmq'  # For automatic testing, RMQ_HOST should be 'rabbitmq'
RMQ_USER = 'rabbit'
RMQ_PASS = '1234'
EXCHANGE_NAME = 'numbers'" > applications/Globals.py 


# 1. Create a docker network for isolation
docker network create test || true

# 2. Run RabbitMQ in a container
docker run -q --rm -d --network test --name "rabbitmq" -e RABBITMQ_DEFAULT_USER=rabbit -e RABBITMQ_DEFAULT_PASS=1234 rabbitmq:4-alpine

# 3. Wait for the container to boot
sleep 5
