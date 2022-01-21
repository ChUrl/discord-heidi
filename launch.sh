#!/bin/sh

docker pull registry.gitlab.com/churl/heidibot
docker container rm -f heidibot
docker run -d --env-file .env --mount src=/home/christoph/HeidiBot/voicelines,target=/sounds,type=bind --name heidibot registry.gitlab.com/churl/heidibot
